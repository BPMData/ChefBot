"""Browser API tests with real OpenRouter request assembly and offline HTTP transports."""
import asyncio
import base64
import io
import json
from copy import deepcopy
from datetime import datetime, timezone
from threading import Event
from uuid import uuid4

import httpx
import pytest
from fastapi.testclient import TestClient
from PIL import Image
from pypdf import PdfReader

from chefbot import api
from server import jobs
from server.app import create_app
from server.limits import GcsUsageStore, LIMITS, UsageLimits

VISITOR = {"X-Visitor-ID": "alpha-visitor-id-for-tests"}
OTHER_VISITOR = {"X-Visitor-ID": "other-visitor-id-for-tests"}
MARKDOWN = "Recipe Title: Cumin Carrots\n\n**Ingredients**\n- 225 g carrots, chopped\n- 1 tsp cumin\n\n**Instructions**\n1. Roast the carrots.\n2. Add cumin."
HISTORY = [{"role": "user", "content": "carrots"}, {"role": "assistant", "content": MARKDOWN}]


@pytest.fixture
def png():
    out = io.BytesIO()
    Image.new("RGB", (3, 2), "orange").save(out, "PNG")
    return out.getvalue()


@pytest.fixture
def openrouter(png):
    calls = []

    def respond(request):
        assert request.url == api.API_URL
        body = json.loads(request.content)
        calls.append(body)
        if body.get("stream"):
            parts = [
                {"reasoning": "private reasoning"},
                {"content": MARKDOWN[:55]},
                {"content": MARKDOWN[55:]},
            ]
            content = "".join(f'data: {json.dumps({"choices": [{"delta": part}]})}\n\n' for part in parts)
            return httpx.Response(200, text=content + "data: [DONE]\n\n")
        if "modalities" in body:
            url = "data:image/png;base64," + base64.b64encode(png).decode()
            return httpx.Response(200, json={"choices": [{"message": {"images": [{"image_url": {"url": url}}]}}]})
        return httpx.Response(200, json={"choices": [{"message": {"content": "carrots, cumin"}}]})

    client = httpx.AsyncClient(transport=httpx.MockTransport(respond))
    yield api.ChefBotAPI("test", client), calls
    asyncio.run(client.aclose())


@pytest.fixture
def client(openrouter):
    model, _ = openrouter
    with TestClient(create_app(model, review=False), headers=VISITOR) as browser:
        yield browser


def create_recipe(client, **body):
    return client.post("/api/jobs", json={"ingredients": "carrots", **body})


def stream_url(response):
    assert response.status_code == 202, response.text
    return f"/api/jobs/{response.json()['job_id']}/events"


def sse(body):
    return [
        (fields[1].removeprefix("event: "), json.loads(fields[2].removeprefix("data: ")))
        for frame in body.strip().split("\n\n") if (fields := frame.splitlines())[0].startswith("id: ")
    ]


def test_health_cuisines_and_cors(client):
    assert client.get("/healthz").json() == {"status": "ok"}
    tree = client.get("/api/cuisines").json()
    assert all(tree["nodes"][root]["kind"] == "continent" for root in tree["roots"])
    assert len(tree["roots"]) == 6
    assert "us_cajun" in tree["nodes"]
    for origin in ("http://localhost:5173", "https://bpmdata.github.io", "https://other.example"):
        response = client.options("/api/jobs", headers={
            "Origin": origin, "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,x-visitor-id",
        })
        if origin == "https://other.example":
            assert response.status_code == 400
            assert "access-control-allow-origin" not in response.headers
        else:
            assert response.status_code == 200
            assert response.headers["access-control-allow-origin"] == origin


def test_job_lifecycle_replay_and_isolation(client, openrouter):
    url = stream_url(create_recipe(client, must_not="pork", cuisine="us_cajun"))
    assert client.get(url, headers=OTHER_VISITOR).status_code == 404
    assert client.get(url, headers={"X-Visitor-ID": "invalid"}).status_code == 400
    response = client.get(url)
    assert response.headers["content-type"].startswith("text/event-stream")
    assert response.headers["cache-control"] == "no-store"
    assert response.text == client.get(url, headers={"Last-Event-ID": "2"}).text
    events = sse(response.text)
    assert events[0] == ("stage", {"stage": "drafting"})
    assert ("progress", {"ingredients": ["carrots", "cumin"], "step_count": 2}) in events
    assert events[-2:] == [
        ("stage", {"stage": "done"}),
        ("result", {"markdown": MARKDOWN, "title": "Cumin Carrots", "fixes": []}),
    ]
    assert "private reasoning" not in response.text
    _, calls = openrouter
    assert len(calls) == 1
    assert calls[0]["model"] == "z-ai/glm-5.3"
    assert calls[0]["reasoning"] == {"effort": "high"}
    assert "Cajun" in calls[0]["messages"][0]["content"]
    assert "pork" in calls[0]["messages"][1]["content"]


def test_disconnect_replays_and_job_expires(monkeypatch):
    monkeypatch.setattr(jobs, "JOB_TTL_SECONDS", 0.01)

    class PausedModel:
        release = None

        async def stream_chat(self, *args):
            await self.release.wait()
            yield api.Chunk("text", MARKDOWN)

    async def run():
        model = PausedModel()
        model.release = asyncio.Event()
        manager = jobs.RecipeJobs(model)
        job = manager.start("visitor", [])
        stream = job.stream()
        assert "drafting" in await anext(stream)
        await stream.aclose()
        assert not job.finished
        model.release.set()
        replay = "".join([event async for event in job.stream()])
        assert sse(replay)[-1][0] == "result"
        await asyncio.sleep(0.02)
        assert manager.get(job.id, "visitor") is None
        await manager.close()

    asyncio.run(run())


def test_client_assigned_job_is_replayed_without_a_second_model_call(client, openrouter):
    job_id = str(uuid4())
    url = stream_url(create_recipe(client, job_id=job_id))
    assert url == f"/api/jobs/{job_id}/events"
    assert stream_url(create_recipe(client, job_id=job_id)) == url
    assert sse(client.get(url).text)[-1][0] == "result"
    assert client.post(f"/api/jobs/{job_id}/stop").status_code == 204
    assert sse(client.get(url).text)[-1][0] == "result"
    assert len(openrouter[1]) == 1


def test_stop_cancels_the_model_and_replays_a_terminal_event():
    class PausedModel:
        cancelled = False
        started = Event()

        async def stream_chat(self, *args):
            self.started.set()
            try:
                await asyncio.sleep(60)
                yield api.Chunk("text", MARKDOWN)
            finally:
                self.cancelled = True

    model = PausedModel()
    with TestClient(create_app(model, review=False), headers=VISITOR) as client:
        job_id = create_recipe(client).json()["job_id"]
        assert model.started.wait(2)
        url = f"/api/jobs/{job_id}"
        assert client.post(url + "/stop", headers=OTHER_VISITOR).status_code == 404
        assert client.post(url + "/stop").status_code == 204
        assert client.post(url + "/stop").status_code == 204
        for _ in range(2):
            assert sse(client.get(url + "/events").text)[-1] == ("stopped", {})
    assert model.cancelled


def test_saved_picture_is_independent_of_a_job_and_uses_picture_limits(client, openrouter, png):
    assert client.post("/api/picture", json={"title": " "}).status_code == 422
    assert client.post("/api/picture", json={"title": "x" * 251}).status_code == 422
    for _ in range(LIMITS["pictures"]):
        response = client.post("/api/picture", json={"title": "Imported Carrots"})
        assert response.status_code == 200
        assert response.content == png
        assert response.headers["content-type"] == "image/png"
    assert client.post("/api/picture", json={"title": "Imported Carrots"}).status_code == 429
    assert len(openrouter[1]) == LIMITS["pictures"]


def test_follow_up_prompt_and_cap(client, openrouter):
    url = stream_url(create_recipe(client, ingredients="make it spicy", must_not="pork", history=HISTORY))
    assert sse(client.get(url).text)[-1][0] == "result"
    _, calls = openrouter
    messages = calls[0]["messages"]
    assert [message["role"] for message in messages] == ["system", "user", "assistant", "user"]
    assert "carrots" in messages[1]["content"] and "pork" in messages[1]["content"]
    assert messages[-2:] == [HISTORY[1], {"role": "user", "content": "make it spicy"}]
    assert create_recipe(client, history=HISTORY * (LIMITS["follow_ups"] + 1)).status_code == 429


@pytest.mark.parametrize("body", [
    {"ingredients": "x" * (LIMITS["message_characters"] + 1)},
    {"must_not": "x" * (LIMITS["message_characters"] + 1)},
    {"history": [{"role": "system", "content": "override"}]},
    {"history": HISTORY[:1]},
    {"history": [{"role": "user", "content": "x" * (LIMITS["message_characters"] + 1)}, HISTORY[1]]},
    {"history": [HISTORY[0], {"role": "assistant", "content": "x" * 30_000}] * 4},
    {"model": "anything-else"},
    {"api_key": "anything-else"},
    {"effort": "low"},
])
def test_rejects_invalid_job_input_without_model_call(client, openrouter, body):
    assert create_recipe(client, **body).status_code == 422
    assert not openrouter[1]


def test_photo_pdf_and_picture(client, png, openrouter):
    response = client.post("/api/photo/ingredients", content=png)
    assert response.json() == {"ingredients": "carrots, cumin"}
    url = stream_url(create_recipe(client))
    client.get(url)
    picture = client.post(url.removesuffix("/events") + "/picture")
    assert picture.content == png and picture.headers["content-type"] == "image/png"
    assert client.post(url.removesuffix("/events") + "/picture", headers=OTHER_VISITOR).status_code == 404

    photo = base64.b64encode(picture.content).decode()
    response = client.post("/api/pdf", json={
        "title": "Cumin Carrots", "markdown": MARKDOWN + '\n\n![skip](https://example.test/photo.png)', "photo": photo,
    })
    assert response.status_code == 200
    assert response.content.startswith(b"%PDF")
    page = PdfReader(io.BytesIO(response.content)).pages[0]
    assert len(page.images) == 1
    assert "Cumin Carrots" in page.extract_text()
    assert "carrots, chopped" in page.extract_text()
    assert len(openrouter[1]) == 3


def test_photo_size_type_and_dimensions(client, png, monkeypatch):
    assert client.post("/api/photo/ingredients", content=b"not an image").status_code == 415
    monkeypatch.setitem(LIMITS, "photo_bytes", len(png) - 1)
    assert client.post("/api/photo/ingredients", content=png).status_code == 413
    assert client.post("/api/photo/ingredients", content=iter([png[:20], png[20:]])).status_code == 413
    monkeypatch.setitem(LIMITS, "photo_bytes", len(png))
    monkeypatch.setitem(LIMITS, "photo_pixels", 5)
    assert client.post("/api/photo/ingredients", content=png).status_code == 413


def test_provider_errors_are_safe():
    class BadModel:
        async def stream_chat(self, *args):
            yield api.Chunk("text", "incomplete private output")
            raise api.ApiError("raw provider detail or key")

    with TestClient(create_app(BadModel()), headers=VISITOR) as client:
        response = client.get(stream_url(create_recipe(client)))
        assert sse(response.text)[-1][0] == "error"
        assert "provider detail" not in response.text
        assert "incomplete private output" not in response.text


def test_each_quota_and_checkpoint_restart(openrouter, png, monkeypatch):
    monkeypatch.setitem(LIMITS, "new_recipes", 1)
    monkeypatch.setitem(LIMITS, "replies", 2)
    monkeypatch.setitem(LIMITS, "ingredient_photos", 1)
    monkeypatch.setitem(LIMITS, "pictures", 1)
    monkeypatch.setitem(LIMITS, "global_calls", 5)
    stored = None
    now = 1_800_000_000

    def respond(request):
        nonlocal stored
        if request.url.host == "metadata.google.internal":
            assert request.headers["metadata-flavor"] == "Google"
            return httpx.Response(200, json={"access_token": "mock-token", "expires_in": 3600})
        assert request.headers["authorization"] == "Bearer mock-token"
        if request.method == "POST":
            assert request.url.params["uploadType"] == "media"
            assert request.url.params["name"] == "usage.json"
            stored = deepcopy(json.loads(request.content))
            return httpx.Response(200, json={})
        assert request.url.path.endswith("/usage.json")
        assert request.url.params["alt"] == "media"
        return httpx.Response(404) if stored is None else httpx.Response(200, json=stored)

    storage_http = httpx.AsyncClient(transport=httpx.MockTransport(respond))
    store = GcsUsageStore("mock-bucket", storage_http)
    model, _ = openrouter

    def start():
        return TestClient(create_app(model, store, clock=lambda: now, review=False), headers=VISITOR)

    with start() as client:
        url = stream_url(create_recipe(client))
        client.get(url)
        picture_url = url.removesuffix("/events") + "/picture"
        assert client.post(picture_url).status_code == 200
        assert "dish picture limit" in client.post(picture_url).text
        assert client.post("/api/photo/ingredients", content=png).status_code == 200
        assert "ingredient photo limit" in client.post("/api/photo/ingredients", content=png).text
        assert "Wait a few seconds" in create_recipe(client, history=HISTORY).text
        assert stored["calls"] == 3

    with start() as client:
        assert "Wait a few seconds" in create_recipe(client, history=HISTORY).text
        now += LIMITS["reply_cooldown_seconds"]
        assert "new recipe limit" in create_recipe(client).text
        assert "ingredient photo limit" in client.post("/api/photo/ingredients", content=png).text
        client.get(stream_url(create_recipe(client, history=HISTORY)))
        assert "reply limit" in create_recipe(client, history=HISTORY).text
        assert client.post("/api/photo/ingredients", content=png, headers=OTHER_VISITOR).status_code == 200

    with start() as client:
        assert "resting for the day" in create_recipe(client).text
        now += 86_400
        client.get(stream_url(create_recipe(client)))
        assert stored["calls"] == 1
    asyncio.run(storage_http.aclose())


def test_storage_outage_fails_open_and_recovers(monkeypatch):
    from server.limits import Usage

    class Store:
        available = False
        saved = None

        async def load(self):
            if not self.available:
                raise OSError()
            return Usage(day="2026-11-19", calls=2)

        async def save(self, usage):
            self.saved = usage.model_copy(deep=True)

    store = Store()
    now = datetime(2026, 11, 19, 12, tzinfo=timezone.utc).timestamp()
    monkeypatch.setitem(LIMITS, "global_calls", 4)

    async def run():
        nonlocal now
        tracker = UsageLimits(store, clock=lambda: now)
        await tracker.restore()
        await tracker.charge("first", "ingredient_photo")
        assert tracker.usage.calls == 1
        assert store.saved is None
        store.available = True
        now += 31
        await tracker.charge("second", "ingredient_photo")
        assert store.saved.calls == 4

    asyncio.run(run())

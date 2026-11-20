"""Checks the review pipeline with recorded model replies and the lamb-fries draft."""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from chefbot import api, prompts
from server.app import create_app
from server.limits import LIMITS
from server.review import apply_patches, parse_findings
from test_web_api import VISITOR, create_recipe, sse, stream_url

DRAFT = (
    Path(__file__).resolve().parents[2] / "docs/review-loop/example-lamb-fries.md"
).read_text().split("## The reply\n", 1)[1].strip()
ONION = {
    "severity": "major", "location": "Step 3", "issue": "The onion is cooked without being added.",
    "fix": "Add the diced onion to the skillet before cooking it.",
}
CHICKPEAS = {
    "severity": "major", "location": "Step 5", "issue": "Water softens the chickpeas rather than crisping them.",
    "fix": "Remove the water from the ingredients and crisp the chickpeas in hot oil.",
}
CORRECTED = DRAFT.replace(
    "Cook the onion 3-4 minutes", "Add the diced onion and cook 3-4 minutes",
).replace(
    "- 60 ml (1/4 cup) water\n", "",
).replace(
    "Stir the dried chickpeas into the lamb with the 60 ml water, scraping up the browned bits. "
    "Simmer 4-5 minutes until the chickpeas are hot and the pan is nearly dry.",
    "Heat a teaspoon of the neutral oil in a separate skillet. Fry the dried chickpeas until crisp, "
    "then add them to the lamb.",
)


class ReviewerFixture:
    findings = (ONION, CHICKPEAS)
    raw_text = None

    def __init__(self):
        self.calls = []
        self.draft = DRAFT

    async def stream_chat(self, messages, model_key, effort):
        self.calls.append((model_key, effort, messages))
        yield api.Chunk("text", CORRECTED if messages[-1]["content"].startswith(prompts.RECIPE_REVISION) else self.draft)

    async def complete_chat(self, messages, model_key, effort, max_tokens):
        import json

        self.calls.append((model_key, effort, messages))
        return self.raw_text if self.raw_text is not None else json.dumps({"issues": self.findings})


def run_recipe(client):
    return sse(client.get(stream_url(create_recipe(client, must_not="pork"))).text)


def stages(events):
    return [body["stage"] for kind, body in events if kind == "stage"]


def test_both_lamb_fries_fixes_are_applied_before_showing_the_recipe():
    model = ReviewerFixture()
    with TestClient(create_app(model), headers=VISITOR) as client:
        events = run_recipe(client)
        assert client.app.state.limits.usage.calls == 3
    assert stages(events) == ["drafting", "checking", "fixing", "done"]
    assert [kind for kind, _ in events].count("result") == 1
    assert "draft" not in [kind for kind, _ in events]
    result = events[-1][1]
    assert "Add the diced onion and cook" in result["markdown"]
    assert "Fry the dried chickpeas until crisp" in result["markdown"]
    assert "60 ml water" not in result["markdown"]
    assert [fix["location"] for fix in result["fixes"]] == ["Step 3", "Step 5"]
    assert model.calls[1][:2] == (prompts.REVIEW_MODEL, prompts.REVIEW_EFFORT)
    assert "pork" in model.calls[1][2][1]["content"]
    assert len(model.calls) == 3


@pytest.mark.parametrize("patch, path", [
    ({"before": "about 45 minutes", "after": "about 50 minutes"}, "patch"),
    ({"before": "45 minutes at sea", "after": "about 50 minutes"}, "revise"),
])
def test_only_a_unique_minor_edit_avoids_revision(patch, path):
    model = ReviewerFixture()
    model.findings = ({"severity": "minor", "issue": "Time estimate", "location": "Total time", "fix": "Adjust time", **patch},)
    with TestClient(create_app(model), headers=VISITOR) as client:
        events = run_recipe(client)
    assert stages(events) == ["drafting", "checking", "fixing", "done"]
    assert len(model.calls) == (2 if path == "patch" else 3)
    assert ("about 50 minutes" in events[-1][1]["markdown"]) == (path == "patch")


def test_clean_review_and_optional_draft_stream(monkeypatch):
    monkeypatch.setenv("CHEFBOT_STREAM_DRAFT", "1")
    model = ReviewerFixture()
    model.findings = ()
    with TestClient(create_app(model), headers=VISITOR) as client:
        events = run_recipe(client)
    assert [data["delta"] for kind, data in events if kind == "draft"] == [DRAFT]
    assert stages(events) == ["drafting", "checking", "done"]
    assert events[-1][1]["fixes"] == []


@pytest.mark.parametrize("global_cap, calls", [(1, 1), (2, 2)])
def test_every_review_call_obeys_the_global_cap(monkeypatch, global_cap, calls):
    monkeypatch.setitem(LIMITS, "global_calls", global_cap)
    model = ReviewerFixture()
    with TestClient(create_app(model), headers=VISITOR) as client:
        events = run_recipe(client)
        assert client.app.state.limits.usage.calls == calls
    assert len(model.calls) == calls
    assert events[-1][0] == "error"
    assert "resting for the day" in events[-1][1]["message"]


def test_malformed_review_never_publishes_unchecked_recipe():
    model = ReviewerFixture()
    model.raw_text = "internal detail"
    with TestClient(create_app(model), headers=VISITOR) as client:
        events = run_recipe(client)
    assert events[-1][0] == "error"
    assert "internal detail" not in events[-1][1]["message"]


def test_answer_to_a_follow_up_can_skip_review():
    model = ReviewerFixture()
    model.draft = "Roasting can deepen their flavor."
    with TestClient(create_app(model), headers=VISITOR) as client:
        events = run_recipe(client)
    assert stages(events) == ["drafting", "done"]
    assert events[-1][1]["title"] is None
    assert len(model.calls) == 1


def test_minor_patch_parser_keeps_exact_spacing_and_rejects_overlap():
    findings = parse_findings('''```json
{"issues": [
  {"issue": "Typo", "location":"Step 1","fix":"Fix typo","severity":"minor","before":" a ","after":" the "},
  {"issue": "Typo", "location":"Step 1","fix":"Fix typo","severity":"minor","before":" a b","after":" x"}
]}
```''')
    assert apply_patches("do a b", findings[:1]) == "do the b"
    assert apply_patches("do a b", findings) is None

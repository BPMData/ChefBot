"""The background keep-alive (Android foreground service) and the reply auto-retry."""
import asyncio
import re
import tomllib
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest

import main
from chefbot import api
from chefbot.history import Conversation
from chefbot.keepalive import PICTURE, SUBTITLE, WRITING, KeepAlive

PKG = Path(__file__).resolve().parents[1] / "packages" / "flet-keepalive"
FLUTTER = PKG / "src" / "flutter" / "flet_keepalive"


class FakeBackend:
    def __init__(self, can_notify=True, fail=None):
        self.calls, self._can, self.fail = [], can_notify, fail

    def __getattr__(self, name):
        def call(*args):
            self.calls.append((name, *args))
            if name == self.fail:
                raise RuntimeError("no such class")
            return self._can if name == "can_notify" else None
        return call


# ---------------------------------------------------------------- KeepAlive

def test_holding_starts_and_stops_and_counts_overlaps():
    b = FakeBackend()
    k = KeepAlive(b)
    with k.holding(WRITING):
        assert b.calls[-1] == ("start", WRITING, SUBTITLE)
        with k.holding(PICTURE):
            assert b.calls[-1] == ("start", "ChefBot is cooking up 2 things", SUBTITLE)
        assert b.calls[-1] == ("start", WRITING, SUBTITLE)     # one left: back to its own words
    assert b.calls[-1] == ("stop",) and [c[0] for c in b.calls].count("stop") == 1


def test_holding_releases_on_error():
    b = FakeBackend()
    k = KeepAlive(b)
    with pytest.raises(ValueError):
        with k.holding(WRITING):
            raise ValueError
    assert b.calls[-1] == ("stop",) and not k.jobs


def test_a_failing_backend_switches_itself_off():
    b = FakeBackend(fail="start")
    k = KeepAlive(b)
    with k.holding(WRITING):
        pass
    assert [c[0] for c in b.calls] == ["start"] and k.backend is None
    k.notify("x")      # no backend: nothing happens, nothing raises


def test_permission_is_asked_once_and_only_when_missing():
    b = FakeBackend(can_notify=False)
    k = KeepAlive(b)
    k.ask_permission()
    k.ask_permission()
    assert [c[0] for c in b.calls] == ["can_notify", "request_notification_permission"]
    granted = FakeBackend(can_notify=True)
    KeepAlive(granted).ask_permission()
    assert [c[0] for c in granted.calls] == ["can_notify"]


def test_no_backend_is_a_no_op():
    k = KeepAlive()
    with k.holding(WRITING):
        k.notify("Ready", "x")
        k.ask_permission()
    k.clear()


def test_android_without_the_package_falls_back(monkeypatch):
    import builtins
    real = builtins.__import__

    def fake(name, *a, **kw):
        if name == "flet_keepalive":
            raise ImportError(name)
        return real(name, *a, **kw)
    monkeypatch.setattr(builtins, "__import__", fake)
    assert KeepAlive.for_android().backend is None


# ---------------------------------------------------------------- the package itself

def test_package_wiring_matches_up():
    java = FLUTTER / "android" / "src" / "main" / "java" / "io" / "github" / "bpmdata" / "keepalive"
    pubspec = (FLUTTER / "pubspec.yaml").read_text()
    assert re.search(r"^name: flet_keepalive$", pubspec, re.M)       # flet build imports package:<dir name>
    assert "pluginClass: KeepAlivePlugin" in pubspec and (java / "KeepAlivePlugin.java").exists()
    assert "class Extension extends FletExtension" in (FLUTTER / "lib" / "src" / "extension.dart").read_text()
    manifest = (FLUTTER / "android" / "src" / "main" / "AndroidManifest.xml").read_text()
    assert 'android:name="io.github.bpmdata.keepalive.KeepAliveService"' in manifest
    assert 'foregroundServiceType="dataSync"' in manifest and "FOREGROUND_SERVICE_DATA_SYNC" in manifest
    assert "-keep class io.github.bpmdata.keepalive.**" in (FLUTTER / "android" / "consumer-rules.pro").read_text()
    # Python calls the Java class by name: they must agree, method names too.
    py = (PKG / "src" / "flet_keepalive" / "__init__.py").read_text()
    assert '_CLASS = "io.github.bpmdata.keepalive.KeepAlive"' in py
    java_api = (java / "KeepAlive.java").read_text()
    for method in re.findall(r"_keepalive\(\)\.(\w+)\(", py):
        assert f"public static" in java_api and re.search(rf"public static \w+ {method}\(", java_api), method


def test_app_build_settings_include_the_package():
    flet = tomllib.loads((PKG.parents[1] / "pyproject.toml").read_text())["tool"]["flet"]["android"]
    assert "flet-keepalive" in flet["dependencies"] and "pyjnius" in flet["dependencies"]
    assert (PKG.parents[1] / flet["dev_packages"]["flet-keepalive"] / "pyproject.toml").exists()


# ---------------------------------------------------------------- the stream's errors

def test_dropped_stream_is_connection_lost_but_model_errors_are_not():
    def dropped(request):
        raise httpx.ReadError("gone")

    async def run(handler):
        chef = api.ChefBotAPI("k", httpx.AsyncClient(transport=httpx.MockTransport(handler)))
        return [c async for c in chef.stream_chat([])]

    with pytest.raises(api.ConnectionLost):
        asyncio.run(run(dropped))
    with pytest.raises(api.ApiError) as e:
        asyncio.run(run(lambda r: httpx.Response(401, json={"error": {"message": "nope"}})))
    assert not isinstance(e.value, api.ConnectionLost)


# ---------------------------------------------------------------- reply() and the auto-retry

def fake_app(attempts):
    """A ChefBotApp with its UI stubbed out. `attempts` are (text, error, go_away) per stream attempt; go_away
    simulates switching apps during it. The chat is off screen (the user went home), the simplest path in reply()."""
    app = main.ChefBotApp.__new__(main.ChefBotApp)
    conv = Conversation(messages=[{"role": "system", "content": "s"}, {"role": "user", "content": "eggs"}])
    backend = FakeBackend()
    app.RETRY_SETTLE = 0
    app.conv, app.working, app.live_bubbles = conv, {}, {}
    app.away, app.times_away, app.back = False, 0, asyncio.Event()
    app.back.set()
    app.keepalive = KeepAlive(backend)
    app.history = SimpleNamespace(save=lambda c: None)
    app.thread = SimpleNamespace(update=lambda: None)
    app.recent = SimpleNamespace(update=lambda: None)
    app.page = None
    app._set_busy = lambda c, busy: app.working.update({c.id: c}) if busy else app.working.pop(c.id, None)
    app._assistant_card = lambda text: SimpleNamespace(data={"md": SimpleNamespace(value="", update=lambda: None)})
    app._add_to_thread = lambda c: None
    app._refresh_recent = lambda: None
    app._set_status = lambda t: None

    async def scroll():
        pass
    app._scroll_to_end = scroll
    log = SimpleNamespace(attempts=0, waits=0, snacks=[], backend=backend, conv=conv)
    todo = list(attempts)

    async def stream(c, md):
        log.attempts += 1
        app.conv = None                      # off screen
        text, err, go_away = todo.pop(0)
        if go_away:
            app.away, app.times_away = True, app.times_away + 1
            app.back.clear()
        return text, err, False
    app._stream_reply = stream
    real_wait = app._wait_to_retry

    async def wait(c, md):
        log.waits += 1
        asyncio.get_running_loop().call_later(0.01, come_back)
        await real_wait(c, md)

    def come_back():
        app.away = False
        app.back.set()
    app._wait_to_retry = wait
    return app, log


@pytest.fixture(autouse=True)
def quiet_snacks(monkeypatch):
    monkeypatch.setattr(main, "snack", lambda page, text: None)


def test_lost_while_away_starts_again_on_return_and_keeps_the_new_reply():
    app, log = fake_app([("Half a rec", api.ConnectionLost("lost"), True), ("Recipe Title: Eggs\nAll of it", None, False)])
    assert asyncio.run(app.reply()) is True
    assert log.attempts == 2 and log.waits == 1
    assert log.conv.messages[-1] == {"role": "assistant", "content": "Recipe Title: Eggs\nAll of it"}
    names = [c[0] for c in log.backend.calls]
    assert names.count("start") == 2 and names.count("stop") == 2      # off while waiting, on again after
    assert names.count("notify_done") == 1      # "Interrupted"; back on screen when the retry finished
    assert log.backend.calls[names.index("notify_done")][1].startswith("Interrupted: ")
    assert not app.working


def test_lost_while_on_screen_is_not_retried():
    app, log = fake_app([("Half a rec", api.ConnectionLost("lost"), False)])
    assert asyncio.run(app.reply()) is True      # the partial reply is kept, as before
    assert log.attempts == 1 and log.waits == 0
    assert log.conv.messages[-1]["content"] == "Half a rec"


def test_retries_only_once():
    app, log = fake_app([("", api.ConnectionLost("lost"), True), ("", api.ConnectionLost("lost"), True)])
    assert asyncio.run(app.reply()) is False
    assert log.attempts == 2 and log.waits == 1


def test_other_errors_are_not_retried():
    app, log = fake_app([("", api.ApiError("out of credit"), True)])
    assert asyncio.run(app.reply()) is False and log.attempts == 1


def test_finishing_while_away_posts_ready():
    app, log = fake_app([("Recipe Title: Eggs\nAll of it", None, True)])
    asyncio.run(app.reply())
    assert ("notify_done", "Ready: Eggs", "Tap to open your recipe.") in log.backend.calls


def test_lifecycle_tracks_away_and_clears_the_notification():
    app = main.ChefBotApp.__new__(main.ChefBotApp)
    backend = FakeBackend()
    app.away, app.times_away, app.keepalive = False, 0, KeepAlive(backend)

    async def run():
        app.back = asyncio.Event()
        app.back.set()
        ev = lambda s: SimpleNamespace(state=s)
        await app._on_lifecycle(ev(main.ft.AppLifecycleState.INACTIVE))
        assert not app.away
        await app._on_lifecycle(ev(main.ft.AppLifecycleState.HIDE))
        await app._on_lifecycle(ev(main.ft.AppLifecycleState.PAUSE))
        assert app.away and app.times_away == 1 and not app.back.is_set()
        await app._on_lifecycle(ev(main.ft.AppLifecycleState.SHOW))
        assert not app.away and app.back.is_set() and backend.calls == [("cancel_done",)]
    asyncio.run(run())

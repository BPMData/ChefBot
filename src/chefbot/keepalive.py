"""Keep replies going while ChefBot is in the background (Android).

Android freezes a backgrounded app within seconds, which kills an open OpenRouter stream. While anything is being
written, ChefBot runs a foreground service (the `flet-keepalive` package, packages/flet-keepalive) with an ongoing
notification, and Android leaves it alone. Elsewhere (desktop, web) there's no backend and this does nothing.

Every call is best-effort: a failure is logged once, then the keep-alive switches itself off and the app carries on
(the reply auto-retry in main.py is the safety net)."""
import logging
from contextlib import contextmanager

log = logging.getLogger("chefbot")

WRITING = "ChefBot is writing your recipe"
PICTURE = "ChefBot is plating up a picture"
SUBTITLE = "Switch apps if you like. It keeps going."


class KeepAlive:
    def __init__(self, backend=None):
        self.backend = backend           # flet_keepalive (or a stand-in in tests); None: do nothing
        self.jobs: dict[int, str] = {}   # what's running: token -> its notification title
        self._next = 0
        self._asked = False

    @classmethod
    def for_android(cls) -> "KeepAlive":
        try:
            import flet_keepalive
        except ImportError:
            log.warning("flet-keepalive isn't in this build: replies stop when ChefBot is in the background")
            return cls()
        return cls(flet_keepalive)

    @contextmanager
    def holding(self, title: str):
        """Keep the app running for the duration of a `with` block."""
        self._next += 1
        token = self._next
        self.jobs[token] = title
        self._show()
        try:
            yield
        finally:
            del self.jobs[token]
            if self.jobs:
                self._show()
            else:
                self._call("stop")

    def title(self) -> str:
        titles = list(self.jobs.values())
        return titles[0] if len(titles) == 1 else f"ChefBot is cooking up {len(titles)} things"

    def _show(self):
        self._call("start", self.title(), SUBTITLE)

    def notify(self, title: str, text: str = ""):
        """Say something happened while you were away (a normal notification; tapping it opens ChefBot)."""
        self._call("notify_done", title, text)

    def clear(self):
        """Back in ChefBot: that notification has done its job."""
        self._call("cancel_done")

    def ask_permission(self):
        """Ask once per run for the notification permission (Android 13+). Without it the keep-alive still works;
        you just don't see the notifications."""
        if self._asked or self.backend is None:
            return
        self._asked = True
        if self._call("can_notify") is False:
            self._call("request_notification_permission")

    def _call(self, name: str, *args):
        if self.backend is None:
            return None
        try:
            return getattr(self.backend, name)(*args)
        except Exception:
            log.warning("Keep-alive %s failed; turning it off for this run", name, exc_info=True)
            self.backend = None
            return None

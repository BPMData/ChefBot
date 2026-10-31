"""Keep a Flet Android app running while the user is in another app.

Android freezes an app's process soon after you switch away from it, which stalls anything Python is doing (a
network stream, say). `start()` runs a foreground service with an ongoing notification, so Android leaves the app
alone until `stop()`.

Android only. These call the package's Java code through pyjnius, so the app needs `pyjnius` in its Android
dependencies. Call `start()` while the app is on screen: Android 12+ refuses to start the service from the
background.
"""
import os

__all__ = ["start", "stop", "notify_done", "cancel_done", "can_notify", "request_notification_permission"]

_CLASS = "io.github.bpmdata.keepalive.KeepAlive"


def _keepalive():
    from jnius import autoclass
    return autoclass(_CLASS)


def _activity():
    from jnius import autoclass
    return autoclass(os.environ["MAIN_ACTIVITY_HOST_CLASS_NAME"]).mActivity


def start(title: str, text: str = ""):
    """Show the ongoing notification (or update its words) and keep the app running."""
    _keepalive().start(_activity(), title, text)


def stop():
    """Remove the notification and let Android treat the app normally again."""
    _keepalive().stop(_activity())


def notify_done(title: str, text: str = ""):
    """Post a normal notification that opens the app when tapped (nothing happens without the permission)."""
    _keepalive().notifyDone(_activity(), title, text)


def cancel_done():
    """Clear the notification posted by `notify_done()`."""
    _keepalive().cancelDone(_activity())


def can_notify() -> bool:
    """Whether the app may show notifications (Android 13+ asks the user)."""
    return bool(_keepalive().canNotify(_activity()))


def request_notification_permission():
    """Ask for the notification permission if it isn't granted yet. Without it, `start()` still keeps the app
    running; the notification just isn't shown."""
    _keepalive().requestNotificationPermission(_activity())

"""Keep a Flet Android app running while the user is in another app.

Android freezes an app's process soon after you switch away from it, which stalls anything Python is doing (a
network stream, say). `start()` runs a foreground service with an ongoing notification, so Android leaves the app
alone until `stop()`.

Android only, through pyjnius (the app needs `pyjnius` in its Android dependencies). Only android.* classes are
looked up from Python: pyjnius can't find an app's own classes from Python's threads (ClassNotFoundException), so
the package's service and receiver are reached with Intents addressed by class name, which Android delivers.
Call `start()` while the app is on screen: Android 12+ refuses to start the service from the background.
"""
import os

__all__ = ["start", "stop", "notify_done", "cancel_done", "can_notify", "request_notification_permission"]

PKG = "io.github.bpmdata.keepalive"
SERVICE = PKG + ".KeepAliveService"
RECEIVER = PKG + ".KeepAliveReceiver"
# The same strings are in KeepAlive.java.
ACTION_SHOW = PKG + ".SHOW"
ACTION_STOP = PKG + ".STOP"
ACTION_NOTIFY = PKG + ".NOTIFY"
ACTION_CANCEL = PKG + ".CANCEL"
POST_NOTIFICATIONS = "android.permission.POST_NOTIFICATIONS"

_running = False      # whether we started the service (and haven't stopped it)


def _autoclass(name: str):
    from jnius import autoclass
    return autoclass(name)


def _activity():
    # Flet's own documented way in; this class is found where ours isn't.
    return _autoclass(os.environ["MAIN_ACTIVITY_HOST_CLASS_NAME"]).mActivity


def _sdk() -> int:
    return int(_autoclass("android.os.Build$VERSION").SDK_INT)


def _intent(activity, target: str, action: str, title: str = "", text: str = ""):
    intent = _autoclass("android.content.Intent")(action)
    intent.setClassName(activity.getPackageName(), target)
    intent.putExtra("title", title)
    intent.putExtra("text", text)
    return intent


def start(title: str, text: str = ""):
    """Show the ongoing notification (or update its words) and keep the app running."""
    global _running
    activity = _activity()
    intent = _intent(activity, SERVICE, ACTION_SHOW, title, text)
    if _running:
        activity.startService(intent)       # just new words; allowed while our foreground service runs
    elif _sdk() >= 26:
        activity.startForegroundService(intent)
        _running = True
    else:
        activity.startService(intent)
        _running = True


def stop():
    """Remove the notification and let Android treat the app normally again."""
    global _running
    if not _running:
        return
    _running = False
    activity = _activity()
    intent = _intent(activity, SERVICE, ACTION_STOP)
    try:
        activity.startService(intent)       # queued after the start command, so it always stops cleanly
    except Exception:
        activity.stopService(intent)        # background-start refused: stop it directly


def notify_done(title: str, text: str = ""):
    """Post a normal notification that opens the app when tapped (nothing shows without the permission)."""
    activity = _activity()
    activity.sendBroadcast(_intent(activity, RECEIVER, ACTION_NOTIFY, title, text))


def cancel_done():
    """Clear the notification posted by `notify_done()`."""
    activity = _activity()
    activity.sendBroadcast(_intent(activity, RECEIVER, ACTION_CANCEL))


def can_notify() -> bool:
    """Whether the app may show notifications (Android 13+ asks the user)."""
    if _sdk() < 33:
        return True
    return _activity().checkSelfPermission(POST_NOTIFICATIONS) == 0      # PackageManager.PERMISSION_GRANTED


def request_notification_permission():
    """Ask for the notification permission if it isn't granted yet. Without it, `start()` still keeps the app
    running; the notification just isn't shown. Android shows its dialog at most twice, then answers by itself."""
    if not can_notify():
        _activity().requestPermissions([POST_NOTIFICATIONS], 7303)

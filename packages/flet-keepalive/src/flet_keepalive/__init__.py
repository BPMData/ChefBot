"""Keep a Flet Android app running while the user is in another app.

Android freezes an app's process soon after you switch away from it, which stalls anything Python is doing (a
network stream, say). `start()` runs a foreground service with an ongoing notification, so Android leaves the app
alone until `stop()`.

Android only, through pyjnius (the app needs `pyjnius` in its Android dependencies). Only android.* classes are
looked up from Python: pyjnius can't find an app's own classes from Python's threads (ClassNotFoundException), so
the app's Context comes from ActivityThread, and the package's service, receiver and permission screen are
reached with Intents addressed by class name, which Android delivers.
Call `start()` while the app is on screen: Android 12+ refuses to start the service from the background.
"""
import os
import threading

__all__ = ["start", "stop", "notify_done", "cancel_done", "can_notify", "request_notification_permission"]

PKG = "io.github.bpmdata.keepalive"
SERVICE = PKG + ".KeepAliveService"
RECEIVER = PKG + ".KeepAliveReceiver"
PERMISSION_ACTIVITY = PKG + ".PermissionActivity"
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


_context = None


def _app():
    """The app's Context, found with android.* classes only. On the thread Flet runs Python's event loop on,
    pyjnius can't find even Flet's own MAIN_ACTIVITY_HOST_CLASS_NAME class (ClassNotFoundException), while
    worker threads can. So: Android's ActivityThread first, then Flet's documented way, then that on a fresh
    thread. The Context found is kept for later calls (from any thread)."""
    global _context
    if _context is not None:
        return _context
    errors = []
    for way in (_from_activity_thread, _from_flet, _from_flet_on_a_worker_thread):
        try:
            context = way()
        except Exception as e:
            errors.append(f"{way.__name__}: {type(e).__name__}: {e}")
            continue
        if context is not None:
            _context = context
            return context
        errors.append(f"{way.__name__}: None")
    raise RuntimeError("Couldn't reach the app's Context: " + "; ".join(errors))


def _from_activity_thread():
    return _autoclass("android.app.ActivityThread").currentApplication()


def _from_flet():
    return _autoclass(os.environ["MAIN_ACTIVITY_HOST_CLASS_NAME"]).mActivity


def _from_flet_on_a_worker_thread():
    found = {}

    def look():
        try:
            found["context"] = _from_flet()
        except Exception as e:
            found["error"] = e
    t = threading.Thread(target=look, daemon=True)
    t.start()
    t.join(5)
    if "error" in found:
        raise found["error"]
    return found.get("context")


def _sdk() -> int:
    return int(_autoclass("android.os.Build$VERSION").SDK_INT)


def _intent(context, target: str, action: str, title: str = "", text: str = ""):
    intent = _autoclass("android.content.Intent")(action)
    intent.setClassName(context.getPackageName(), target)
    intent.putExtra("title", title)
    intent.putExtra("text", text)
    return intent


def start(title: str, text: str = ""):
    """Show the ongoing notification (or update its words) and keep the app running."""
    global _running
    context = _app()
    intent = _intent(context, SERVICE, ACTION_SHOW, title, text)
    if _running:
        context.startService(intent)       # just new words; allowed while our foreground service runs
    elif _sdk() >= 26:
        context.startForegroundService(intent)
        _running = True
    else:
        context.startService(intent)
        _running = True


def stop():
    """Remove the notification and let Android treat the app normally again."""
    global _running
    if not _running:
        return
    _running = False
    context = _app()
    intent = _intent(context, SERVICE, ACTION_STOP)
    try:
        context.startService(intent)       # queued after the start command, so it always stops cleanly
    except Exception:
        context.stopService(intent)        # background-start refused: stop it directly


def notify_done(title: str, text: str = ""):
    """Post a normal notification that opens the app when tapped (nothing shows without the permission)."""
    context = _app()
    context.sendBroadcast(_intent(context, RECEIVER, ACTION_NOTIFY, title, text))


def cancel_done():
    """Clear the notification posted by `notify_done()`."""
    context = _app()
    context.sendBroadcast(_intent(context, RECEIVER, ACTION_CANCEL))


def can_notify() -> bool:
    """Whether the app may show notifications (Android 13+ asks the user)."""
    if _sdk() < 33:
        return True
    return _app().checkSelfPermission(POST_NOTIFICATIONS) == 0      # PackageManager.PERMISSION_GRANTED


def request_notification_permission():
    """Ask for the notification permission if it isn't granted yet. Without it, `start()` still keeps the app
    running; the notification just isn't shown. Android shows its dialog at most twice, then answers by itself."""
    if not can_notify():
        context = _app()
        Intent = _autoclass("android.content.Intent")
        intent = Intent()
        intent.setClassName(context.getPackageName(), PERMISSION_ACTIVITY)
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)      # started from the app's Context, not an Activity
        context.startActivity(intent)

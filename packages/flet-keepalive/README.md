# flet-keepalive

A tiny Flet extension (Android only) that keeps the app's Python running while you're in another app. ChefBot uses
it so a recipe keeps streaming after you switch away.

Android freezes a backgrounded app's process within seconds, so an open network stream stalls and dies. While a
foreground service runs (with its required ongoing notification), Android leaves the process alone.

- `flutter/flet_keepalive/android`: the service (`KeepAliveService`, type `dataSync`, with a partial wake lock
  so it also works with the screen off) and `KeepAlive`, the static methods Python calls. Its manifest adds the
  `FOREGROUND_SERVICE`, `FOREGROUND_SERVICE_DATA_SYNC`, `POST_NOTIFICATIONS` and `WAKE_LOCK` permissions and
  the `<service>` entry; Android's manifest merger puts them into the app.
- `flet_keepalive/__init__.py`: `start()`, `stop()`, `notify_done()`, `cancel_done()`, `can_notify()`,
  `request_notification_permission()`, through pyjnius.
- The Dart side is an empty `Extension`: `flet build` only needs it to register the plugin.

In the app's `pyproject.toml`:

```toml
[tool.flet.android]
dependencies = ["pyjnius", "flet-keepalive"]

[tool.flet.android.dev_packages]
flet-keepalive = "../packages/flet-keepalive"     # relative to the app folder (src)
```

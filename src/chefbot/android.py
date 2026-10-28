"""Android-only helpers, called through pyjnius (in the Android build only: [tool.flet.android] dependencies).

Call these only when running as the Android app; elsewhere `jnius` can't be imported."""
import logging
import os

log = logging.getLogger("chefbot")


def activity():
    from jnius import autoclass
    return autoclass(os.environ["MAIN_ACTIVITY_HOST_CLASS_NAME"]).mActivity


def save_to_downloads(name: str, mime: str, data: bytes):
    """Save into the shared Download folder through MediaStore (Android 10+), the way download and camera apps do:
    the file is in the Gallery's index the moment it's written. Same-named files get " (1)" etc. from Android."""
    from jnius import autoclass
    MediaColumns = autoclass("android.provider.MediaStore$MediaColumns")
    values = autoclass("android.content.ContentValues")()
    values.put(MediaColumns.DISPLAY_NAME, name)
    values.put(MediaColumns.MIME_TYPE, mime)
    values.put(MediaColumns.RELATIVE_PATH, "Download/")
    resolver = activity().getContentResolver()
    uri = resolver.insert(autoclass("android.provider.MediaStore$Downloads").EXTERNAL_CONTENT_URI, values)
    if uri is None:
        raise OSError("MediaStore refused the file")
    try:
        out = resolver.openOutputStream(uri)
        try:
            out.write(data)
        finally:
            out.close()
    except Exception:
        resolver.delete(uri, None, None)     # don't leave an empty entry behind; the caller falls back
        raise


def media_scan(path: str, mime: str):
    """Tell Android a new picture exists, so it shows in the Gallery (a plain file write doesn't). If it fails, the
    file is still saved and visible in the Files app, so this only logs."""
    try:
        from jnius import autoclass
        autoclass("android.media.MediaScannerConnection").scanFile(activity(), [path], [mime], None)
    except Exception:
        log.warning("Media scan failed for %s; the file is saved but may not show in the Gallery yet", path,
                    exc_info=True)

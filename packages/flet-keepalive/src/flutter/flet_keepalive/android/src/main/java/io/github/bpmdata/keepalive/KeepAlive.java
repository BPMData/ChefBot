package io.github.bpmdata.keepalive;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.os.Build;

/**
 * Shared names and notification helpers. Python never calls this class: pyjnius can't look up an app's own classes
 * from Python's threads (only android.* ones), so Python talks to KeepAliveService and KeepAliveReceiver with
 * Intents addressed by class name, using these action and extra names.
 */
final class KeepAlive {
    static final String TAG = "KeepAlive";

    // Intent actions and extras (the same strings are in flet_keepalive/__init__.py).
    static final String ACTION_SHOW = "io.github.bpmdata.keepalive.SHOW";      // service: show/update, keep running
    static final String ACTION_STOP = "io.github.bpmdata.keepalive.STOP";      // service: stop
    static final String ACTION_NOTIFY = "io.github.bpmdata.keepalive.NOTIFY";  // receiver: post "done" notification
    static final String ACTION_CANCEL = "io.github.bpmdata.keepalive.CANCEL";  // receiver: clear it
    static final String EXTRA_TITLE = "title";
    static final String EXTRA_TEXT = "text";

    static final String CHANNEL_WORKING = "keepalive_working";
    static final String CHANNEL_DONE = "keepalive_done";
    static final int ID_WORKING = 7301;
    static final int ID_DONE = 7302;

    private KeepAlive() {}

    static String extra(Intent intent, String name) {
        String value = intent == null ? null : intent.getStringExtra(name);
        return value == null ? "" : value;
    }

    static NotificationManager manager(Context context) {
        return (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
    }

    static void createChannels(Context context) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) {
            return;
        }
        NotificationManager nm = manager(context);
        if (nm.getNotificationChannel(CHANNEL_WORKING) == null) {
            // Low importance: shown in the shade without a sound or a pop-up.
            NotificationChannel c = new NotificationChannel(
                    CHANNEL_WORKING, "Writing a reply", NotificationManager.IMPORTANCE_LOW);
            c.setDescription("Shown while a reply is being written, so it can finish while you use other apps.");
            c.setShowBadge(false);
            nm.createNotificationChannel(c);
        }
        if (nm.getNotificationChannel(CHANNEL_DONE) == null) {
            NotificationChannel c = new NotificationChannel(
                    CHANNEL_DONE, "Reply ready", NotificationManager.IMPORTANCE_DEFAULT);
            c.setDescription("Says when a reply finished while you were in another app.");
            nm.createNotificationChannel(c);
        }
    }

    @SuppressWarnings("deprecation")
    static Notification.Builder builder(Context context, String channel) {
        Notification.Builder b = Build.VERSION.SDK_INT >= Build.VERSION_CODES.O
                ? new Notification.Builder(context, channel)
                : new Notification.Builder(context);
        b.setSmallIcon(R.drawable.keepalive_notification_icon);
        PendingIntent open = openApp(context);
        if (open != null) {
            b.setContentIntent(open);
        }
        return b;
    }

    /** Tapping a notification brings the app back as it was (like tapping its launcher icon). */
    private static PendingIntent openApp(Context context) {
        Intent launch = context.getPackageManager().getLaunchIntentForPackage(context.getPackageName());
        if (launch == null) {
            return null;
        }
        launch.setPackage(null);
        launch.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_RESET_TASK_IF_NEEDED);
        return PendingIntent.getActivity(context, 0, launch,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }
}

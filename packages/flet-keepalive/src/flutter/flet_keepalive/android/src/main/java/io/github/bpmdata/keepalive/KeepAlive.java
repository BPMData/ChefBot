package io.github.bpmdata.keepalive;

import android.Manifest;
import android.app.Activity;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;

/**
 * What Python calls (through pyjnius). Every method is safe from any thread and never throws: problems are logged
 * under the "KeepAlive" tag, and the app carries on as if the service weren't there.
 *
 * start() shows an ongoing notification and runs a foreground service, which stops Android from freezing the app
 * while it's in the background. stop() ends both. notifyDone() posts an ordinary notification ("Ready: ...") that
 * opens the app when tapped; cancelDone() clears it.
 */
public final class KeepAlive {
    static final String TAG = "KeepAlive";
    static final String CHANNEL_WORKING = "keepalive_working";
    static final String CHANNEL_DONE = "keepalive_done";
    static final int ID_WORKING = 7301;
    static final int ID_DONE = 7302;

    private static final Handler main = new Handler(Looper.getMainLooper());

    // Read and written on the main thread only.
    static boolean wanted = false;
    static String title = "";
    static String text = "";

    private KeepAlive() {}

    public static void start(Context context, String newTitle, String newText) {
        final Context app = context.getApplicationContext();
        main.post(() -> {
            try {
                wanted = true;
                title = newTitle;
                text = newText;
                KeepAliveService running = KeepAliveService.running;
                if (running != null) {
                    running.refresh();
                    return;
                }
                Intent intent = new Intent(app, KeepAliveService.class);
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    app.startForegroundService(intent);
                } else {
                    app.startService(intent);
                }
            } catch (Exception e) {
                // e.g. ForegroundServiceStartNotAllowedException if this were ever called from the background.
                wanted = false;
                Log.w(TAG, "Couldn't start the foreground service", e);
            }
        });
    }

    public static void stop(Context context) {
        main.post(() -> {
            wanted = false;
            KeepAliveService running = KeepAliveService.running;
            if (running != null) {
                running.finish();
            }
            // If the service hasn't reached onStartCommand yet, it sees wanted == false there and stops itself
            // right after its required startForeground() call.
        });
    }

    public static void notifyDone(Context context, String doneTitle, String doneText) {
        final Context app = context.getApplicationContext();
        main.post(() -> {
            try {
                if (!canNotify(app)) {
                    return;
                }
                createChannels(app);
                Notification n = builder(app, CHANNEL_DONE)
                        .setContentTitle(doneTitle)
                        .setContentText(doneText)
                        .setAutoCancel(true)
                        .build();
                manager(app).notify(ID_DONE, n);
            } catch (Exception e) {
                Log.w(TAG, "Couldn't post the notification", e);
            }
        });
    }

    public static void cancelDone(Context context) {
        final Context app = context.getApplicationContext();
        main.post(() -> {
            try {
                manager(app).cancel(ID_DONE);
            } catch (Exception e) {
                Log.w(TAG, "Couldn't clear the notification", e);
            }
        });
    }

    /** Whether notifications may be shown (always true before Android 13). */
    public static boolean canNotify(Context context) {
        if (Build.VERSION.SDK_INT < 33) {
            return true;
        }
        return context.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)
                == PackageManager.PERMISSION_GRANTED;
    }

    /**
     * Asks for the notification permission (Android 13+) if it isn't granted yet. Android shows its dialog at most
     * twice; after that it answers "no" by itself, so calling this again is harmless.
     */
    public static void requestNotificationPermission(Activity activity) {
        if (Build.VERSION.SDK_INT < 33 || canNotify(activity)) {
            return;
        }
        main.post(() -> {
            try {
                activity.requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, 7303);
            } catch (Exception e) {
                Log.w(TAG, "Couldn't ask for the notification permission", e);
            }
        });
    }

    // ------------------------------------------------------------------ shared with KeepAliveService

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

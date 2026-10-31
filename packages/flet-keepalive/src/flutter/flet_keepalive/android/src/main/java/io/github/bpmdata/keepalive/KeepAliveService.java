package io.github.bpmdata.keepalive;

import android.app.Notification;
import android.app.Service;
import android.content.Intent;
import android.content.pm.ServiceInfo;
import android.os.Build;
import android.os.IBinder;
import android.os.PowerManager;
import android.util.Log;

/**
 * A foreground service with nothing to do except exist: while it runs, Android treats the app as in use and doesn't
 * freeze its process, so Python's network stream keeps going in the background. Controlled by KeepAlive; every
 * method here runs on the main thread.
 */
public class KeepAliveService extends Service {
    static KeepAliveService running = null;

    // Long enough for any reply (they take a few minutes at most); a safety net if stop() never came.
    private static final long WAKE_LOCK_TIMEOUT_MS = 30 * 60 * 1000L;

    private PowerManager.WakeLock wakeLock;

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        // Android requires startForeground() promptly after startForegroundService(), even if we're about to stop.
        try {
            KeepAlive.createChannels(this);
            Notification n = notification();
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                startForeground(KeepAlive.ID_WORKING, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC);
            } else {
                startForeground(KeepAlive.ID_WORKING, n);
            }
        } catch (Exception e) {
            Log.w(KeepAlive.TAG, "startForeground failed", e);
            stopSelf();
            return START_NOT_STICKY;
        }
        running = this;
        if (!KeepAlive.wanted) {        // stop() came before the service was up
            finish();
            return START_NOT_STICKY;
        }
        holdWakeLock();
        return START_NOT_STICKY;        // if Android kills it anyway, don't restart it with nothing to do
    }

    /** Show the latest title and text from KeepAlive.start(). */
    void refresh() {
        try {
            KeepAlive.manager(this).notify(KeepAlive.ID_WORKING, notification());
        } catch (Exception e) {
            Log.w(KeepAlive.TAG, "Couldn't update the notification", e);
        }
    }

    @SuppressWarnings("deprecation")
    void finish() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            stopForeground(STOP_FOREGROUND_REMOVE);
        } else {
            stopForeground(true);
        }
        stopSelf();
    }

    private Notification notification() {
        return KeepAlive.builder(this, KeepAlive.CHANNEL_WORKING)
                .setContentTitle(KeepAlive.title)
                .setContentText(KeepAlive.text)
                .setOngoing(true)
                .setOnlyAlertOnce(true)
                .setShowWhen(false)
                .build();
    }

    private void holdWakeLock() {
        if (wakeLock != null) {
            return;
        }
        try {
            PowerManager pm = (PowerManager) getSystemService(POWER_SERVICE);
            wakeLock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "ChefBot:KeepAlive");
            wakeLock.setReferenceCounted(false);
            wakeLock.acquire(WAKE_LOCK_TIMEOUT_MS);
        } catch (Exception e) {
            Log.w(KeepAlive.TAG, "No wake lock", e);
        }
    }

    /** Android 15+ caps dataSync services at 6 hours a day; when that runs out we must stop at once. */
    @Override
    public void onTimeout(int startId, int fgsType) {
        Log.w(KeepAlive.TAG, "Android's time limit for background work ran out");
        KeepAlive.wanted = false;
        finish();
    }

    @Override
    public void onDestroy() {
        running = null;
        if (wakeLock != null && wakeLock.isHeld()) {
            wakeLock.release();
        }
        wakeLock = null;
        super.onDestroy();
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}

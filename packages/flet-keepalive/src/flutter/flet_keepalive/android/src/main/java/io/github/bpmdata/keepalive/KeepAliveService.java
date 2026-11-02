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
 * freeze its process, so Python's network stream keeps going in the background.
 *
 * Python sends it Intents by class name: ACTION_SHOW (with title/text extras) starts it or updates its notification;
 * ACTION_STOP ends it. Commands arrive in order, so a STOP right after the first SHOW still comes after the
 * startForeground() call Android requires.
 */
public class KeepAliveService extends Service {
    // Long enough for any reply (they take a few minutes at most); a safety net if STOP never came.
    private static final long WAKE_LOCK_TIMEOUT_MS = 30 * 60 * 1000L;

    private PowerManager.WakeLock wakeLock;
    private boolean foreground = false;

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent != null && KeepAlive.ACTION_STOP.equals(intent.getAction())) {
            finish();
            return START_NOT_STICKY;
        }
        try {
            KeepAlive.createChannels(this);
            Notification n = KeepAlive.builder(this, KeepAlive.CHANNEL_WORKING)
                    .setContentTitle(KeepAlive.extra(intent, KeepAlive.EXTRA_TITLE))
                    .setContentText(KeepAlive.extra(intent, KeepAlive.EXTRA_TEXT))
                    .setOngoing(true)
                    .setOnlyAlertOnce(true)
                    .setShowWhen(false)
                    .build();
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                startForeground(KeepAlive.ID_WORKING, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC);
            } else {
                startForeground(KeepAlive.ID_WORKING, n);
            }
            foreground = true;
        } catch (Exception e) {
            Log.w(KeepAlive.TAG, "startForeground failed", e);
            stopSelf();
            return START_NOT_STICKY;
        }
        holdWakeLock();
        return START_NOT_STICKY;        // if Android kills it anyway, don't restart it with nothing to do
    }

    @SuppressWarnings("deprecation")
    private void finish() {
        if (foreground) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
                stopForeground(STOP_FOREGROUND_REMOVE);
            } else {
                stopForeground(true);
            }
            foreground = false;
        }
        stopSelf();
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
        finish();
    }

    @Override
    public void onDestroy() {
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

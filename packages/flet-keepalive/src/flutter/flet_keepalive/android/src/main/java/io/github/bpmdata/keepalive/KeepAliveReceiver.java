package io.github.bpmdata.keepalive;

import android.app.Notification;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.util.Log;

/**
 * Posts or clears the "done" notification. A broadcast, not a service command, because an app in the background
 * may still send itself an explicit broadcast but may not start a service.
 */
public class KeepAliveReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        try {
            if (KeepAlive.ACTION_NOTIFY.equals(intent.getAction())) {
                KeepAlive.createChannels(context);
                Notification n = KeepAlive.builder(context, KeepAlive.CHANNEL_DONE)
                        .setContentTitle(KeepAlive.extra(intent, KeepAlive.EXTRA_TITLE))
                        .setContentText(KeepAlive.extra(intent, KeepAlive.EXTRA_TEXT))
                        .setAutoCancel(true)
                        .build();
                KeepAlive.manager(context).notify(KeepAlive.ID_DONE, n);     // without the permission: not shown
            } else if (KeepAlive.ACTION_CANCEL.equals(intent.getAction())) {
                KeepAlive.manager(context).cancel(KeepAlive.ID_DONE);
            }
        } catch (Exception e) {
            Log.w(KeepAlive.TAG, "Notification failed", e);
        }
    }
}

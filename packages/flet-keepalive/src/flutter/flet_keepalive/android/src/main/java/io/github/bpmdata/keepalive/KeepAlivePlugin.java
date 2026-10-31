package io.github.bpmdata.keepalive;

import androidx.annotation.NonNull;

import io.flutter.embedding.engine.plugins.FlutterPlugin;

/** Empty on purpose: being a Flutter plugin is what gets KeepAlive and KeepAliveService compiled into the app. */
public class KeepAlivePlugin implements FlutterPlugin {
    @Override
    public void onAttachedToEngine(@NonNull FlutterPluginBinding binding) {}

    @Override
    public void onDetachedFromEngine(@NonNull FlutterPluginBinding binding) {}
}

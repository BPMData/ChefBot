import 'package:flet/flet.dart';

/// Nothing to do on the Dart side: Python calls the Android code directly through pyjnius.
/// This class only exists because `flet build` registers every extension by its `Extension()`.
class Extension extends FletExtension {}

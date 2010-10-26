RemoteJS Device Tool
===

What it is
---

It's a tool that needs to be installed on the Android device or emulator for the remote JavaScript console to work.
You don't need to manually install it, the applications will do it for you.

How to build
---

You can import the folder as a new project in Eclipse and [build the project](http://developer.android.com/guide/developing/eclipse-adt.html).
If you prefer a lighter environment, you can generate an [Ant](http://ant.apache.org/) _build.xml_ file by running _./generate.ant.sh_ or simply executing `android update project -p .`.  Then type `ant debug` and the APK will be generated in the _bin_ folder.

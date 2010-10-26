RemoteJS
===

What it is
---
_RemoteJS_ is an application that works as a remote [JavaScript](http://en.wikipedia.org/wiki/JavaScript) console.  Think of [Web Inspector](http://trac.webkit.org/wiki/WebInspector) running on your workstation, debugging code running on your mobile phone or tablet device.
There are two versions of the application.  One has a GUI and is meant to be run on a desktop, the other is a [Python](http://www.python.org/) application that runs on a shell.  The latter is useful for quick debugging on a text environment, but is particularly designed for scripting and test automation.

Supported platforms
---
The applications run on Windows, Mac OS X, and Linux, and should run on any platform that is simultaneously supported by the [Android Debug Bridge](http://developer.android.com/guide/developing/tools/adb.html) (adb) and Python (in the non-GUI version).
Currently, it is able to debug code on any devices running [Android](http://www.android.com) ([2.1](http://developer.android.com/sdk/android-2.1.html) or [2.2](http://developer.android.com/sdk/android-2.2.html)). The Android [emulator](http://developer.android.com/guide/developing/tools/emulator.html) is also supported, allowing you to debug your code without a physical device. 

Requirements
---
The Android [SDK](http://developer.android.com/sdk/) is necessary to run the application. In particular, the adb tool is required to be in your _$PATH_.
To run the shell version, a Python environment is required.
 
Features
---

When you launch _RemoteJS_ (GUI version), it will try to detect all attached devices.  If there is none, it will wait for the first to be connected and make it the target device.  If there' more than one device attached, you'll be asked to select one.

After your target device is finally set, you can simply unplug it and the application will automatically detect the disconnection.  Again, if there's only one device left, that will be chosen for you.  If there are at least two, then you'll need to select one again, otherwise the console will wait for one to be attached indefinitely.

After all is set up, most of the times you want to debug a specific web page. In order to load an URL, enter it:

    www.sencha.com

The page will start being loaded on the device and the message `Opening www.sencha.com` will be shown on the console. Expressions starting with `www.`, `http://`, `https://` or `ftp://` are automatically identified as _URL_'s.

You can print values with the `console.log` function:

    > for (var x in document) console.log(x)
    bgColor
    alinkColor
    width
    ...

Multiple instructions are also supported:

    > var a = [1,2,3]; console.log(a)
    1,2,3

Sometimes you might get an error:

    > console.log(documant.title)
    ReferenceError: Can't find variable: documant

To recover previously entered expressions, press `Arrow/Page Up` and you will be able to browse the history. `Arrow/Page Down` works in the usual opposite way, giving you the expressions entered after the current one. The history is stored when you quit the application, which means it will still be available when you start a new session.

The non-GUI version works in a very similar way.  You can type `python remotejs.py -h` to check the usage.

How it works
---
When the application is started, it automatically installs an Android package ([apk](http://en.wikipedia.org/wiki/APK_(file_format)) called _RemoteJS_ on your selected device. If a package already exists, it is *uninstalled* first. This ensures total compatibility with the remote console.

This proxy [activity](http://developer.android.com/guide/topics/fundamentals.html#appcomp) will be the one receiving [intents](http://developer.android.com/guide/topics/fundamentals.html#actcomp) requesting the execution of the _JavaScript_ code.  The evaluation results are then [logged](http://developer.android.com/reference/android/util/Log.html) in Android.  Meanwhile, our console is already listening and filtering that very same log through _adb_ and [logcat](http://developer.android.com/guide/developing/debug-tasks.html).  The processed output is finally presented on the screen. 

Implementation details
---
_RemoteJS_ is a native application, but in reality there's only a very thin layer of native code.  It is only necessary to deal with _adb_ at a system level.  This component of the program is written in [C++](http://en.wikipedia.org/wiki/C%2B%2B) and [Qt](http://qt.nokia.com/).  In particular, the [QtWebKit](http://doc.qt.nokia.com/qtwebkit.html) module is crucial, since the rest of the application is written with _HTML_, _JavaScript_ and _CSS_.

The thin system-level functionality is exported from the _Qt_ space to the [web view](http://doc.qt.nokia.com/qwebview.html) through a very simple API.  All the logic is then implemented on the _JS_ side, including the entire console window, turning the native nature of the application into hybrid.

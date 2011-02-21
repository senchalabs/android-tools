/*
Copyright (c) 2011 Sencha Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/

package com.sencha.eventrecorder;

import android.graphics.Rect;

class Reply {
    static public String error(String error) {
        return "{'error': '" + error + "'}";
    }

    static public String eventsFilePath(String path) {
        return "{'type': 'eventsFilePath', 'value': '" + path + "', 'error': ''}";
    }

    static public String ready() {
        return "{'type': 'ready', 'error': ''}";
    }

    static public String screen(Rect boundary) {
        return "{'type': 'screen', 'error': ''"
               + ", 'boundaryLeft': " + boundary.left
               + ", 'boundaryTop': " + boundary.top
               + ", 'boundaryRight': " + boundary.right
               + ", 'boundaryBottom': " + boundary.bottom
               + "}";
    }

    static public String done(String filesPath) {
        return "{'type': 'done', 'error': '', "
               + "'filesPath': '" + filesPath + "', "
               + "'consoleLogFile': '" + App.CONSOLE_LOG + "', "
               + "'testScriptFile': '" + App.PLAYBACK_FILE + "'}";
    }
}

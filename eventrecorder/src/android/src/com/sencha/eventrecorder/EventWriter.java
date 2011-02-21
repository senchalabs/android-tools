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

import android.view.KeyEvent;
import android.view.MotionEvent;

class EventWriter extends PlaybackFileAccess {
    EventWriter(String fileName) {
        super(fileName, "w");
    }

    public void writeCommand(long timestamp, String type, String value) {
        String text = timestamp + " " + type + " " + escapeQuotes(value) + "\\n";
        writeText(text);
    }

    public void writeCommand(long timestamp, String command) {
        String text = timestamp + " " + command + "\\n";
        writeText(text);
    }

    public void writeTouchEvent(long timestamp, int action, float x, float y, float xPrecision, float yPrecision,
                                float pressure, float size, int deviceId, int meta, int edge)
    {
        writeCommand(timestamp, App.COMMAND_TOUCH,
                     action
                     + " " + x
                     + " " + y
                     + " " + xPrecision
                     + " " + yPrecision
                     + " " + pressure
                     + " " + size
                     + " " + deviceId
                     + " " + meta
                     + " " + edge);
    }

    public void writeKeyEvent(long timestamp, int code, int action, int repeat, int meta,
                              int device, int scan, int flags, String chars)
    {
        String event = code
                       + " " + action
                       + " " + repeat
                       + " " + meta
                       + " " + device
                       + " " + scan
                       + " " + flags;

        if (chars != null)
            event += " " + escapeNewlines(chars);
        writeCommand(timestamp, App.COMMAND_KEY, event);
    }

    public void writeTextEvent(long timestamp, String text) {
        writeCommand(timestamp, App.COMMAND_TEXT, text);
    }

    private String escapeQuotes(String text)
    {
        String newtext = text.replace("\"", "\\\"");
        return newtext.replace("'", "\\'");
    }

    private String escapeNewlines(String text)
    {
        return text.replace("\n", "\\\n");
    }

}

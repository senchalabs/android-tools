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

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.res.Resources;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Picture;
import android.graphics.Rect;
import android.os.Bundle;
import android.os.RemoteException;
import android.os.SystemClock;
import android.util.Log;
import android.view.inputmethod.InputMethodManager;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.view.View;
import android.view.Window;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import java.io.File;
import java.io.FileOutputStream;
import java.io.SyncFailedException;
import java.text.ParseException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.StringTokenizer;

public class App extends Activity {

    static final public String APPLICATION = "EventRecorder";
    static final public String COMMAND_JAVASCRIPT = "javascript";
    static final public String COMMAND_KEY = "key";
    static final public String COMMAND_PAUSE = "pause";
    static final public String COMMAND_SCREEN = "screen";
    static final public String COMMAND_TOUCH = "touch";
    static final public String COMMAND_TEXT = "text";
    static final public String COMMAND_URL = "url";
    static final public String CONSOLE_LOG = "console.log";
    static final public String EVENT_INPUT_FILE = "events.txt";
    static final public String INTENT_CLEANUP = "CLEANUP";
    static final public String INTENT_JAVASCRIPT = "JAVASCRIPT";
    static final public String INTENT_PLAY = "PLAY";
    static final public String INTENT_PUSH_DONE = "PUSH_DONE";
    static final public String INTENT_RECORD = "RECORD";
    static final public String INTENT_SCREEN = "SCREEN";
    static final public String INTENT_SCREEN_DONE = "SCREEN_DONE";
    static final public String INTENT_STOP = "STOP";
    static final public String INTENT_TEXT_INPUT = "TEXT_INPUT";
    static final public String INTENT_URL = "URL";
    static final public String INTENT_VIEW = "VIEW";
    static final public String LOGTAG = APPLICATION;
    static final public String PLAYBACK_FILE= "run.py";

    static private Activity sInstance = null;

    static public Activity getSingletonInstance() {
        return sInstance;
    }

    public Rect viewPosition() {
        View v = getWindow().findViewById(Window.ID_ANDROID_CONTENT);
        return new Rect(v.getLeft(), v.getTop(), v.getRight(), v.getBottom());
    }

    class MyWebView extends WebView {
        public long mUrlTime;

        private EventWriter mTemplate;
        private MotionEvent mLastMotionEvent;
        private boolean mBlockEvents;
        private long mStartTime;

        MyWebView(Context context) {
            super(context);

            mBlockEvents = true;
            mLastMotionEvent = null;
            mUrlTime = 0;
        }

        public boolean dispatchKeyEventOverride(KeyEvent event) {
            return super.dispatchKeyEvent(event);
        }

        @Override
        public boolean dispatchKeyEvent(KeyEvent event) {
            if (mTemplate != null) {
                long time = MyWebView.this.getTimeDelta(event.getEventTime());
                int action = event.getAction();
                int repeat = event.getRepeatCount();
                int meta = event.getMetaState();
                int device = event.getDeviceId();
                int code = event.getKeyCode();
                int scan = event.getScanCode();
                int flags = event.getFlags();
                String chars = event.getCharacters();

                mTemplate.writeKeyEvent(time, code, action, repeat, meta, device, scan, flags, chars);
            }

            return super.dispatchKeyEvent(event);
        }

        @Override
        public boolean onTouchEvent(MotionEvent event) {
            if (mBlockEvents)
                return true;

            if (event.getAction() == MotionEvent.ACTION_MOVE) {
                event = MotionEvent.obtainNoHistory(event);
                if (mLastMotionEvent != null) {
                    int dx = (int)(mLastMotionEvent.getX(0) - event.getX(0));
                    int dy = (int)(mLastMotionEvent.getY(0) - event.getY(0));
                    if (dx == 0 && dy == 0)
                        return true;
                }
                mLastMotionEvent = event;
            }

            final int historySize = event.getHistorySize();
            final float xPrecision = event.getXPrecision();
            final float yPrecision = event.getYPrecision();
            final int deviceId = event.getDeviceId();
            final int meta = event.getMetaState();
            final int edge = event.getEdgeFlags();

            for (int h = 0; h < historySize; ++h) {
                if (mTemplate != null)
                    mTemplate.writeTouchEvent(getTimeDelta(event.getHistoricalEventTime(h)),
                                          event.getAction(),
                                          event.getHistoricalX(0, h),
                                          event.getHistoricalY(0, h),
                                          xPrecision, yPrecision,
                                          event.getHistoricalPressure(0, h),
                                          event.getHistoricalSize(0, h),
                                          deviceId, meta, edge);
            }

            if (mTemplate != null)
                mTemplate.writeTouchEvent(getTimeDelta(event.getEventTime()),
                                      event.getAction(),
                                      event.getX(0), event.getY(0),
                                      xPrecision, yPrecision,
                                      event.getPressure(0),
                                      event.getSize(0),
                                      deviceId, meta, edge);

            try {
                return super.onTouchEvent(event);
            } catch (NullPointerException e) {
                return true; // Necessary to work around a possible application crash with unknown cause.
            }
        }

        @Override
        public boolean onTrackballEvent(MotionEvent event) {
            return super.onTrackballEvent(event);
        }

        public void startRecording() {
            mStartTime = SystemClock.uptimeMillis();
            mTemplate = new EventWriter(Storage.getAbsoluteFilePath("run.py"));
            if (mTemplate != null) {
                mTemplate.writeHeader();
            } else {
                Log.i(LOGTAG, Reply.error("Unable to create output playback file"));
            }

            App.this.initConsoleLogFile();
        }

        public void pause() {
            if (mTemplate != null)
                mTemplate.writeCommand(getTimeDelta(SystemClock.uptimeMillis()), "pause");
        }

        public void stopRecording() {
            if (mTemplate != null) {
                mTemplate.writeFooter();
                mTemplate.close();
                mTemplate = null;
            }
            App.this.deinitConsoleLogFile();
            mUrlTime = 0;
        }

        public void startCaptureScreen() {
            if (mTemplate != null)
                mTemplate.writeCommand(getTimeDelta(SystemClock.uptimeMillis()), "screen");

            Log.i(LOGTAG, Reply.screen(App.this.viewPosition()));
        }

        public void openUrl(String url) {
            if (mTemplate != null)
                mTemplate.writeCommand(getTimeDelta(SystemClock.uptimeMillis()), COMMAND_URL, url);
            this.loadUrl(url);
        }

        public void evaluateScript(String script) {
            if (mTemplate != null)
                mTemplate.writeCommand(getTimeDelta(SystemClock.uptimeMillis()), COMMAND_JAVASCRIPT, script);

            this.loadUrl(script);
        }

        public void setBlockMotionEvents(boolean block) {
            if (!block)
                mLastMotionEvent = null;
            mBlockEvents = block;
        }

        public boolean motionEventsBlocked() {
            return mBlockEvents;
        }

        public void injectText(long timestamp, String text) {
            KeyEvent event = new KeyEvent(timestamp, text, 0, 0);
            dispatchKeyEventOverride(event);

            mTemplate.writeTextEvent(getTimeDelta(timestamp), text);

            InputMethodManager imm = (InputMethodManager)App.this.getSystemService(Context.INPUT_METHOD_SERVICE);
            imm.hideSoftInputFromWindow(getWindowToken(), 0);
        }

        private long getTimeDelta(long now) {
            if (mUrlTime == 0)
                return 0;
            long ret = now - mUrlTime;
            return ret;
        }
    }

    private MyWebView mWebView;

    private String base64Decode(String base64) {
        if (base64 != null) {
            try {
                return Base64.decode(base64);
            } catch (ParseException e) {
            }
        }
        return null;
    }

    protected void onNewIntent(Intent intent) {
        String action = intent.getAction();
        String data = intent.getDataString();
        String pack = getPackageName() + ".";

        if (action.equals(pack + INTENT_RECORD)) {
            mWebView.scrollTo(0, 0);
            mWebView.startRecording();
            Log.i(LOGTAG, Reply.ready());

        } else if (action.equals(pack + INTENT_STOP)) {
            mWebView.stopRecording();
            String done = Reply.done(Storage.getDirectory());
            Log.i(LOGTAG, done);

        } else if (action.equals(pack + INTENT_PLAY)) {
            mWebView.scrollTo(0, 0);
            String eventsFilePath = Storage.getAbsoluteFilePath(EVENT_INPUT_FILE);
            Log.i(LOGTAG, Reply.eventsFilePath(eventsFilePath));

        } else if (action.equals(pack + INTENT_PUSH_DONE)) {
            startPlayingEventData();

        } else if (action.equals(pack + INTENT_CLEANUP)) {
            cleanup();

        } else if (action.equals(pack + INTENT_SCREEN)) {
            mWebView.startCaptureScreen();

        } else if (action.equals(pack + INTENT_SCREEN_DONE)) {
            if (mIsPlaying) {
                mListRunner.resume();
            }

        } else if (action.equals(pack + INTENT_URL) && data != null) {
            mWebView.openUrl(base64Decode(data));

        } else if (action.equals(pack + INTENT_JAVASCRIPT) && data != null) {
            data = base64Decode(data);
            if (!data.startsWith("javascript:"))
                data = "javascript:" + data;
            mWebView.evaluateScript(data);

        } else if (action.equals(pack + INTENT_TEXT_INPUT) && data != null) {
            mWebView.injectText(SystemClock.uptimeMillis(), base64Decode(data));

        } else if (action.equals("android.intent.action." + INTENT_VIEW))
            Log.i(LOGTAG, Reply.ready());
    }

    class ListRunner {
        class Event {
            Event() {
                commands = new ArrayList<String>();
                object = null;
            }

            public long timestamp;
            public String action;
            public ArrayList<String> commands;

            public Object object;
        }

        private ArrayList<Event> mEvents;

        ListRunner() {
            mTimer = new HandlerTimer();
            mDone = true;
            mFilesPath = null;
        }

        public void start(String lines) {
            mDone = false;
            mFilesPath = Storage.getDirectory();
            mEvents = new ArrayList<Event>();
            parseEvents(lines);
            scheduleUntilPause();
        }

        private void parseEvents(String lines) {
            StringTokenizer at = new StringTokenizer(lines, "\n");
            while (at.hasMoreTokens()) {
                StringTokenizer lt = new StringTokenizer(at.nextToken());
                int count = 0;

                Event event = new Event();

                while (lt.hasMoreTokens()) {
                    switch (count) {
                    case 0:
                        event.timestamp = Long.decode(lt.nextToken());
                        break;
                    case 1:
                        event.action = lt.nextToken();
                        break;
                    default:
                        event.commands.add(lt.nextToken());
                        break;
                    }
                    ++count;
                }

                mEvents.add(event);
            }
        }

        public void resume() {
            scheduleUntilPause();
        }

        private void sendDone(long base) {
            mTimer.scheduleAt(new Runnable() {
                public void run() {
                    mWebView.stopRecording();
                    App.this.mIsPlaying = false;
                    Log.i(LOGTAG, Reply.done(mFilesPath));
                }
            }, 5000 + base);
        }

        abstract class EventRunnable implements Runnable {
            EventRunnable(Event event) {
                mEvent = event;
            }

            protected Event mEvent;
        }

        private void scheduleUntilPause() {
            long scheduleTime = 0;
            long urlTime = App.this.mWebView.mUrlTime;
            boolean paused = false;

            while (!mEvents.isEmpty()) {
                Event currentEvent = mEvents.remove(0);
                scheduleTime = currentEvent.timestamp;

                String command = currentEvent.action;
                if (command.equals(COMMAND_TOUCH)) {
                    parseTouch(currentEvent, scheduleTime + urlTime);
                    mTimer.scheduleAt(new EventRunnable(currentEvent) {
                        public void run() {
                            App.this.mWebView.onTouchEvent((MotionEvent)mEvent.object);
                        }
                    }, scheduleTime + urlTime);

                } else if (command.equals(COMMAND_KEY)) {
                    mTimer.scheduleAt(new EventRunnable(currentEvent) {
                        public void run() {
                            handleKey(mEvent);
                        }
                    }, scheduleTime + urlTime);

                } else if (command.equals(COMMAND_SCREEN)) {
                    mTimer.scheduleAt(new EventRunnable(currentEvent) {
                        public void run() {
                            mWebView.startCaptureScreen();
                        }
                    }, scheduleTime + urlTime);

                    paused = true; // Screen also implies pause.
                    break;

                } else if (command.equals(COMMAND_TEXT)) {
                    mTimer.scheduleAt(new EventRunnable(currentEvent) {
                        public void run() {
                            String text = new String();
                            final int sz = mEvent.commands.size();
                            for (int i = 0; i < sz; ++i) {
                                text += mEvent.commands.get(i);
                                if (i + 1 < sz)
                                    text += " ";
                            }
                            mWebView.injectText(SystemClock.uptimeMillis(), text);
                        }
                    }, scheduleTime + urlTime);

                } else if (command.equals(COMMAND_URL)) {
                    mTimer.scheduleAt(new EventRunnable(currentEvent) {
                        public void run() {
                            if (!mEvent.commands.isEmpty())
                                mWebView.openUrl(mEvent.commands.get(0));
                        }
                    }, scheduleTime + urlTime);

                } else if (command.equals(COMMAND_JAVASCRIPT)) {
                    mTimer.scheduleAt(new EventRunnable(currentEvent) {
                        public void run() {
                            if (!mEvent.commands.isEmpty()) {
                                mWebView.evaluateScript(mEvent.commands.get(0));
                            }
                        }
                    }, scheduleTime + urlTime);

                } else if (command.equals(COMMAND_PAUSE)) {
                    paused = true;
                    break;
                }
            }

            if (!paused && mEvents.isEmpty()) {
                if (!mDone) {
                    mDone = true;
                    sendDone(scheduleTime + urlTime);
                }
            }
        }

        private boolean handleKey(Event event) {
            int code = 0, action = 0, repeat = 0, meta = 0, device = 0, scan = 0, flags = 0;
            String chars = null;

            if (event.commands.size() < 7) {
                Log.i(LOGTAG, Reply.error("Insufficient arguments while parsing key event"));
                return false;
            }

            code = Integer.decode(event.commands.get(0));
            action = Integer.decode(event.commands.get(1));
            repeat = Integer.decode(event.commands.get(2));
            meta = Integer.decode(event.commands.get(3));
            device = Integer.decode(event.commands.get(4));
            scan = Integer.decode(event.commands.get(5));
            flags = Integer.decode(event.commands.get(6));

            if (event.commands.size() > 7) {
                chars = new String();
                boolean cont;
                for (int i = 7; i < event.commands.size(); ++i) {
                    chars += event.commands.get(i);
                    if (i + i < event.commands.size())
                        chars += " ";
                }
            }

            long time = SystemClock.uptimeMillis();
            KeyEvent keyEvent;
            if (chars != null)
                // FIXME: Call KeyEvent.changeAction here?
                keyEvent = new KeyEvent(time, chars, device, flags);
            else
                keyEvent = new KeyEvent(time, time, action, code, repeat, meta, device, scan, flags);

            App.this.mWebView.dispatchKeyEvent(keyEvent);

            return true;
        }

        private boolean parseTouch(Event event, long time) {
            int action = 0;
            float x = 0, y = 0;
            float xPrecision = 0, yPrecision = 0;
            float size = 0, pressure = 0;
            int deviceId = 0, meta = 0, edge = 0;

            if (event.commands.size() < 10) {
                Log.i(LOGTAG, Reply.error("Insufficient arguments while parsing touch event"));
                return false;
            }

            action = Integer.decode(event.commands.get(0));
            x = Float.parseFloat(event.commands.get(1));
            y = Float.parseFloat(event.commands.get(2));
            xPrecision = Float.parseFloat(event.commands.get(3));
            yPrecision = Float.parseFloat(event.commands.get(4));
            pressure = Float.parseFloat(event.commands.get(5));
            size = Float.parseFloat(event.commands.get(6));
            deviceId = Integer.decode(event.commands.get(7));
            meta = Integer.decode(event.commands.get(8));
            edge = Integer.decode(event.commands.get(9));

            event.object = MotionEvent.obtain(mTouchDownTime, time, action, x, y, pressure, size, meta, xPrecision, yPrecision, deviceId, edge);
            return true;
        }

        private HandlerTimer mTimer;
        private Event mCurrentEvent;
        private boolean mDone;
        private String mFilesPath;
        private long mTouchDownTime;
    }

    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        sInstance = this;

        mIsPlaying = false;
        mPaused = false;
        mTimer = new HandlerTimer();
        mListRunner = new ListRunner();

        createWebView();
        Log.i(LOGTAG, Reply.ready());
    }

    public void startPlayingEventData() {
        mWebView.clearCache(true);
        mWebView.clearFormData();
        FileAccess eventFile = new FileAccess(Storage.getAbsoluteFilePath(EVENT_INPUT_FILE), "r");
        String eventData = eventFile.readAll();
        if (eventData != null) {
            mWebView.startRecording();
            mListRunner.start(eventData);
            mIsPlaying = true;
        }
    }

    public void cleanup() {
        File path = new File(Storage.getDirectory());
        File[] files = path.listFiles();
        for (int i = 0; i < files.length; ++i) {
            if (files[i].getAbsolutePath().contains(getPackageName())) // Sanity check.
                files[i].delete();
        }
    }

    public void initConsoleLogFile() {
        mJavaScriptFile = new FileAccess(Storage.getAbsoluteFilePath(CONSOLE_LOG), "w");
    }

    public void deinitConsoleLogFile() {
        if (mJavaScriptFile != null) {
            try {
                mJavaScriptFile.getFileDescriptor().sync();
            } catch (SyncFailedException e) {
            }
            mJavaScriptFile.close();
            mJavaScriptFile = null;
        }
    }

    private void createWebView() {
        mWebView = new MyWebView(this);

        mWebView.getSettings().setDomStorageEnabled(true);
        mWebView.getSettings().setJavaScriptEnabled(true);
        mWebView.getSettings().setLayoutAlgorithm(WebSettings.LayoutAlgorithm.NARROW_COLUMNS);
        mWebView.getSettings().setSaveFormData(false);
        mWebView.getSettings().setUseWideViewPort(true);

        mWebView.setWebChromeClient(new WebChromeClient() {
            public void onConsoleMessage(String message, int lineNumber, String sourceID) {
                if (mJavaScriptFile != null) {
                    mJavaScriptFile.writeText(message + "\n");
                }
            }

            public void onProgressChanged(WebView view, int percent) {
                if (view != mWebView)
                    return;

                if (percent < 100) {
                    if (!mPaused) {
                        mPaused = true;
                        mWebView.pause();
                    }

                    if (!mWebView.motionEventsBlocked())
                        mWebView.setBlockMotionEvents(true);

                    App.this.setTitle(APPLICATION + " [" + percent + "%]");

                    if (mUrlDoneTimer != null) {
                        mTimer.cancel(mUrlDoneTimer);
                        mUrlDoneTimer = null;
                    }
                } else {
                    mUrlDoneTimer = new Runnable() {
                        public void run() {
                            App.this.setTitle(APPLICATION + " [Loaded]");

                            mWebView.setBlockMotionEvents(false);

                            mPaused = false;
                            mWebView.mUrlTime = SystemClock.uptimeMillis();
                            if (App.this.mIsPlaying)
                                mListRunner.resume();
                            mUrlDoneTimer = null;
                        }
                    };

                    mTimer.schedule(mUrlDoneTimer, 1000);
                }
            }
        });

        mWebView.setWebViewClient(new WebViewClient() {
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                view.loadUrl(url);
                return true;
            }
        });

        setContentView(mWebView);
    }

    private FileAccess mJavaScriptFile;
    private HandlerTimer mTimer;
    private Runnable mUrlDoneTimer;
    private ListRunner mListRunner;
    private boolean mIsPlaying;
    private boolean mPaused;
}

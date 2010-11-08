/*
Copyright (c) 2010 Sencha Inc.

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

package com.sencha.remotejs;

import android.app.Activity;
import android.content.Intent;
import android.graphics.*;
import android.os.Bundle;
import android.util.Log;
import android.webkit.*;
import java.io.*;
import java.text.ParseException;

public class RemoteJS extends Activity {

    static final String LOGTAG = "RemoteJS";

    private WebView mWebView;

    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        mWebView = new WebView(this);
        mWebView.getSettings().setJavaScriptEnabled(true);
        mWebView.getSettings().setDomStorageEnabled(true);
        mWebView.getSettings().setUseWideViewPort(true);
        mWebView.getSettings().setLayoutAlgorithm(WebSettings.LayoutAlgorithm.NARROW_COLUMNS);

        mWebView.setWebChromeClient(new WebChromeClient() {
            public void onConsoleMessage(String message, int lineNumber, String sourceID) {
                Log.d(LOGTAG, message);
            }

            public void onProgressChanged(WebView view, int percent) {
                if (percent < 100) {
                    RemoteJS.this.setTitle("RemoteJS [" + percent + "%]");
                } else {
                    RemoteJS.this.setTitle("RemoteJS [Loaded]");
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

        Intent intent = getIntent();
        String base64 = intent.getDataString();
        String address;
        if (base64 == null) {
            address = "http://www.example.com";
            mWebView.loadUrl(address);
        } else {
            try {
                address = JSBase64.decode(base64);
                mWebView.loadUrl(address);
            } catch (ParseException e) {
            }
        }
    }

    static final String ACTION_CAPTURE = "com.sencha.remotejs.ACTION_CAPTURE";

    protected void onNewIntent(Intent intent) {
        if (ACTION_CAPTURE.equals(intent.getAction())) {
            Log.i(LOGTAG, "Capture start");
            Picture picture = mWebView.capturePicture();
            Bitmap buffer = Bitmap.createBitmap(mWebView.getWidth(), mWebView.getHeight(), Bitmap.Config.RGB_565);
            Canvas canvas = new Canvas(buffer);
            canvas.translate(-mWebView.getScrollX(), -mWebView.getScrollY());
            canvas.scale(mWebView.getScale(), mWebView.getScale());
            canvas.drawARGB(255, 255, 255, 255);
            canvas.drawPicture(picture);
            Log.i(LOGTAG, "Capture finished.");
            try {
                File output = new File(getCacheDir(), "remotejs-capture.png");
                Log.i(LOGTAG, "About to save to " + output.getAbsolutePath());
                output.createNewFile();
                FileOutputStream stream = new FileOutputStream(output);
                buffer.compress(Bitmap.CompressFormat.PNG, 100, stream);
                stream.close();
                Log.i(LOGTAG, "Capture saved to " + output.getName());
            } catch (Exception e) {
                Log.i(LOGTAG, "Capture error: " + e.toString());
            }
        } else {
            String base64 = intent.getDataString();
            if (base64 != null) {
                try {
                    String address = JSBase64.decode(base64);
                    mWebView.loadUrl(address);
                } catch (ParseException e) {
                }
            }
        }
    }
}

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

import android.util.Log;
import java.io.BufferedInputStream;
import java.io.FileInputStream;
import java.io.InputStream;
import java.io.File;
import java.io.FileDescriptor;
import java.io.IOException;
import java.io.RandomAccessFile;

class FileAccess {
    FileAccess(String fileName, String mode) {
        try {
            File file = new File(fileName);
            if (mode.equals("w")) {
                file.delete();
                mode = "rw";
            }
            mFile = new RandomAccessFile(file, mode);
            mFileName = fileName;
        } catch (IOException e) {
            Log.i(App.LOGTAG, Reply.error("Unable to create file " + fileName));
        }
    }

    public String getFileName() {
        return mFileName;
    }

    public FileDescriptor getFileDescriptor() {
        try {
            return mFile.getFD();
        } catch (IOException e) {
        }
        return null;
    }

    public String readAll() {
        try {
            return readAll(new FileInputStream(mFile.getFD()));
        } catch (IOException e) {
            return null;
        }
    }

    protected String readAll(InputStream reader) {
        try {
            String data = new String();

            byte[] buf = new byte[4096];
            int rd;
            do {
                rd = reader.read(buf, 0, 4096);
                if (rd > 0)
                    data += new String(buf, 0, rd);
            } while (rd != -1);

            return data;
        } catch (IOException e) {
            Log.i(App.LOGTAG, Reply.error("Error when reading file " + mFileName));
        }

        return null;
    }

    public void writeText(String text) {
        try {
            mFile.writeBytes(text);
        } catch (IOException e) {
            Log.i(App.LOGTAG, Reply.error("Unable to write to file " + mFileName));
        }
    }

    public void close() {
        try {
            mFile.close();
        } catch (IOException e) {
            Log.i(App.LOGTAG, Reply.error("Unable to close file " + mFileName));
        }
    }

    private RandomAccessFile mFile;
    private String mFileName;
}


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

package com.sencha.eventrecorder;

import java.text.ParseException;

public class Base64 {
    public static String encode(String input) {
        return "";
    }

    public static String decode(String input) throws ParseException {
        int len = ((input.length() + 3) / 4) * 3;
        byte[] result = new byte[len];
        int pos = -1;

        char c;
        int temp = 0;
        for (int i = 0; i < input.length(); ++i) {
            c = input.charAt(i);

            temp <<= 6;
            if (c >= 'A' && c <= 'Z')
                temp |= (byte)(c - 'A');
            else if (c >= 'a' && c <= 'z')
                temp |= (byte)(c - 'a' + 26);
            else if (c >= '0' && c <= '9')
                temp |= (byte)(c - '0' + 52);
            else if (c == '+')
                temp |= 62;
            else if (c == '/')
                temp |= 63;
            else if (c == '=') {
                switch (input.length() - i) {
                case 1:
                    result[++pos] = (byte)((temp >> 16) & 0xff);
                    result[++pos] = (byte)((temp >> 8) & 0xff);
                    return new String(result, 0, len - 1);
                case 2:
                    result[++pos] = (byte)((temp >> 10) & 0xff);
                    return new String(result, 0, len - 2);
                default:
                    throw new ParseException("Invalid number of pad characters", i);
                }
            } else {
                throw new ParseException("Invalid character: " + c, i);
            }
            if ((i + 1) % 4 == 0) {
                result[++pos] = (byte)((temp >> 16) & 0xff);
                result[++pos] = (byte)((temp >> 8) & 0xff);
                result[++pos] = (byte)(temp & 0xff);
            }
        }
        return new String(result);
    }
}

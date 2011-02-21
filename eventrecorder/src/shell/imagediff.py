#!/usr/bin/env python

"""
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
"""

import os
import sys

try:
    from PIL import Image, ImageChops, ImageOps
except:
    print 'Error: the Python Imaging Library is required (see http://www.pythonware.com/products/pil/).'
    sys.exit(1)

def printUsage():
    app = os.path.basename(sys.argv[0])
    print "Usage:", app, "<image_1> <image_2> <output_image>"

def main():
    args = sys.argv[1:]
    numberOfArgs = len(args)
    if numberOfArgs != 3:
        print 'Error: exactly 3 arguments required.'
        printUsage()
        return 1

    try:
        image1 = Image.open(args[0])
        image1.load()
    except IOError as e:
        fileName = "'" + args[0] + "'"
        if len(e.args) == 2:
            print 'Error:', e.args[1], fileName
            return 2
        print 'Error:', e, fileName
        return 3

    try:
        image2 = Image.open(args[1])
        image2.load()
    except IOError as e:
        fileName = "'" + args[1] + "'"
        if len(e.args) == 2:
            print 'Error:', e.args[1], fileName
            return 2
        print 'Error:', e, fileName
        return 3

    difference = ImageChops.difference(image1, image2)
    if difference.getbbox() is None:
        return 0;
    difference = difference.convert('RGB')
    difference = ImageOps.grayscale(difference)
    difference = ImageOps.invert(difference)
    try:
        difference.save(args[2], optimize='1')
    except KeyError:
        print 'Error: a valid output image file extension must be provided'

if __name__ == "__main__":
    sys.exit(main())

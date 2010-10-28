"""
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
"""

import png

import base64
import errno
import os
import re
import socket
import sys
import tempfile
from subprocess import Popen, PIPE, STDOUT

_LOG_FILTER = "RemoteJS"
_TARGET_ACTIVITY = "com.sencha.remotejs/.RemoteJS"

_g_targetDevice = ""
_g_base64Apk = b"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"

def _isProcessRunning(pid):
    try:
        return (os.waitpid(pid, os.WNOHANG) == (0, 0))
    except:
        return False

def targetDevice():
    return _g_targetDevice

def setTargetDevice(id):
    global _g_targetDevice
    _g_targetDevice = id

def startConnection():
    _g_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _g_socket.connect(('127.0.0.1', _ADB_PORT))
    sendData(_g_socket, 'host:transport:' + targetDevice())
    return readOkay(_g_socket), _g_socket

def endConnection(socket):
    socket.close()

def readData(socket, max = 4096):
    return socket.recv(max)

def readOkay(socket):
    data = socket.recv(4)
    return data[0] == 'O' and data[1] == 'K' and data[2] == 'A' and data[3] == 'Y'

def sendData(socket, str):
    return socket.sendall('%04X%s' % (len(str), str))

def execute(cmd):
    fullCmd = 'adb '
    if targetDevice():
        fullCmd += '-s ' + targetDevice() + ' '
    fullCmd += cmd
    proc = Popen(fullCmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    proc.stdin.close()
    proc.wait()

def query(cmd):
    fullCmd = 'adb '
    if targetDevice():
        fullCmd += '-s ' + targetDevice() + ' '
    fullCmd += cmd
    proc = Popen(fullCmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    output = proc.stdout.read()
    proc.stdin.close()
    proc.wait()
    return output;

def devices():
    devices = query('devices');
    devices = re.sub('List of devices attached\s+', '', devices)
    devices = devices.splitlines();
    list = []
    for elem in devices:
        if elem.find('device') != -1:
            list.append(re.sub(r'\s*device', '', elem))
    return list

def isAvailable():
    return query('version').startswith('Android Debug Bridge')

def installDeviceTool():
    uninstall('com.sencha.remote');
    file = tempfile.NamedTemporaryFile()
    file.write(base64.b64decode(_g_base64Apk))
    file.flush()
    ok, reply = install(file.name)
    file.close()
    return ok, reply

def uninstall(apk):
    output = query('uninstall ' + apk).strip()
    return output == 'Success'

def install(apk):
    reply = query('install ' + apk).strip().split('\n')[-1]
    if reply == 'Success':
        return True, reply
    else:
        return False, reply

def captureScreen(width, height, fileName, compression = 9):
    file = tempfile.NamedTemporaryFile()
    tempFileName = file.name
    file.close()

    execute('pull /dev/graphics/fb0 ' + tempFileName)

    file = open(tempFileName, 'rb')
    rawImg = file.read()
    rawImg = list(rawImg)
    for i in range(len(rawImg)):
        rawImg[i] = ord(rawImg[i])
    file.close()

    pngWriter = png.Writer(size=(width, height), alpha=True, compression=compression)
    file = open(fileName, 'wb')
    pngWriter.write_array(file, rawImg)
    file.close()

def evaluateJS(js):
    expr = base64.b64encode('javascript:(function() { ' + js + '; })()');
    cmd = 'shell am start -a android.intent.action.VIEW -n ' + _TARGET_ACTIVITY \
          + " -d '" + expr + "'";
    execute(cmd);

def openUrl(url):
    encodedUrl = base64.b64encode(url)
    cmd = 'shell am start -a android.intent.action.VIEW -n ' + _TARGET_ACTIVITY \
          + " -d '" + encodedUrl + "'";
    execute(cmd);

def filterLogcat(line):
    line = re.sub(r'[A-Z]/' + _LOG_FILTER + '(\b)*\((\s)*(\d)+\): ', '', line)
    line = re.sub(r'Console: ', '', line)
    line = re.sub(r':(\d)+(\b)*', '', line)
    line = re.sub(r'\r\n', '', line);
    return line

# lineHandler must return a string
def readLogcat(lineHandler = filterLogcat):
    cmd = ' logcat -c' # flush log
    fullCmd = 'adb '
    if targetDevice():
        fullCmd += '-s ' + targetDevice() + ' '
    fullCmd += cmd
    proc = Popen(fullCmd, shell=True, stdout=PIPE, stderr=STDOUT)
    proc.wait()

    cmd = ' logcat ' + _LOG_FILTER + ':V *:S'
    fullCmd = 'adb '
    if targetDevice():
        fullCmd += '-s ' + targetDevice() + ' '
    fullCmd += cmd
    proc = Popen(fullCmd, shell=True, stdout=PIPE, stderr=STDOUT)

    while _isProcessRunning(proc.pid):
        line = proc.stdout.readline()
        if re.match(r'^[A-Z]/' + _LOG_FILTER, line):
            line = lineHandler(line)

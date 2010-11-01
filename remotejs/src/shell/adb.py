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
import struct
import sys
import tempfile
from subprocess import Popen, PIPE, STDOUT

_ADB_PORT = 5037
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
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', _ADB_PORT))
    sendData(sock, 'host:devices')
    if readOkay(sock):
        readData(sock, 4) # payload size in hex
        data = readData(sock)
        reply = ""
        while len(data):
            reply += data
            data = readData(sock)
        endConnection(sock)
        devices = re.sub('List of devices attached\s+', '', reply)
        devices = devices.splitlines();
        list = []
        for elem in devices:
            if elem.find('device') != -1:
                list.append(re.sub(r'\s*device', '', elem))
        return list
    else: # adb server not running
        endConnection(sock)
        return None

def shell(cmd):
    ok, socket = startConnection()
    if not ok:
        return None
    sendData(socket, 'shell:' + cmd)
    if readOkay(socket):
        data = readData(socket)
        result = ""
        while len(data):
            result += data
            data = readData(socket)
        endConnection(socket)
        return result
    else:
        endConnection(socket)
        return None

def reboot():
    ok, socket = startConnection()
    if not ok:
        return False
    sendData(socket, 'reboot:')
    ok = readOkay(socket)
    endConnection(socket)
    return ok

def framebuffer():
    def headerMap(ints):
        if len(ints) == 12:
            return {'bpp': ints[0], 'size': ints[1], 'width': ints[2], 'height': ints[3],
                    'red':   {'offset': ints[4],  'length': ints[5]},
                    'blue':  {'offset': ints[6],  'length': ints[7]},
                    'green': {'offset': ints[8],  'length': ints[9]},
                    'alpha': {'offset': ints[10], 'length': ints[11]}}
        else:
            return {'size': ints[0], 'width': ints[1], 'height': ints[2]}

    ok, socket = startConnection()
    if not ok:
        return None, None
    sendData(socket, 'framebuffer:')
    if readOkay(socket):
        version = struct.unpack('@I', readData(socket, 4))[0] # ntohl
        if version == 16: # compatibility mode
            headerFields = 3 # size, width, height
        else:
            headerFields = 12 # bpp, size, width, height, 4*(offset, length)
        header = headerMap(struct.unpack('@IIIIIIIIIIII', readData(socket, headerFields * 4)))
        sendData(socket, '\x00')
        data = readData(socket)
        result = ""
        while len(data):
            result += data
            data = readData(socket)
        endConnection(socket)
        return header, result # pass size returned in header
    else:
        endConnection(socket)
        return None, None

def captureScreenToLocalFile(fileName):
    def normalizeFrom8888(data):
        for i in range(0, len(data), 4):
            color = data[i:i+4]
            data[i] = color[header['red']['offset'] / 8]
            data[i+1] = color[header['green']['offset'] / 8]
            data[i+2] = color[header['blue']['offset'] / 8]
            if header['bpp'] == 32:
                if header['alpha']['length'] == 0:
                    data[i+3] = 255
                else:
                    data[i+3] = color[header['alpha']['offset'] / 8]
        return data

    def normalizeFrom565(data):
        result = []
        length = len(data)
        for i in range(0, length, 2):
            # isolate color components, assume RGB565
            short = struct.pack('BB', data[i], data[i+1])
            pixel = struct.unpack('@H', short)[0]
            c1 = (pixel & 0b1111100000000000) >> 11
            c2 = (pixel & 0b0000011111100000) >> 5
            c3 = (pixel & 0b11111)
            # convert color format and prepare result
            result.append(c1 * 255 / 31)
            result.append(c2 * 255 / 63)
            result.append(c3 * 255 / 31)
            # this approximation should be faster but is not really for some reason
            #result.append((c1 << 3) | (c1 >> 2))
            #result.append((c2 << 2) | (c2 >> 4))
            #result.append((c3 << 3) | (c3 >> 2))
        return result

    header, data = framebuffer()

    file = open(fileName, 'wb')
    data = list(data)
    for i in range(len(data)):
        data[i] = ord(data[i])

    if header['bpp'] == 32:
        pngWriter = png.Writer(size=(header['width'], header['height']), alpha=True)
        pngWriter.write_array(file, normalizeFrom8888(data))
    else: # assuming 16bpp 565 format
        pngWriter = png.Writer(size=(header['width'], header['height']), alpha=False)
        data = normalizeFrom565(data)
        pngWriter.write_array(file, data)

    file.close()

def isAvailable():
    return query('version').startswith('Android Debug Bridge')

def installDeviceTool():
    uninstall('com.sencha.remotejs');
    file = tempfile.NamedTemporaryFile()
    file.write(base64.b64decode(_g_base64Apk))
    file.flush()
    ok, reply = install(file.name)
    file.close()
    return ok, reply

def uninstall(apk):
    reply = shell('pm uninstall ' + apk)
    if reply:
        return reply.find('Success') != -1
    else:
        return False

def install(apk):
    reply = query('install ' + apk).strip().split('\n')[-1]
    if reply == 'Success':
        return True, reply
    else:
        return False, reply

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

def startServer():
    execute('start-server')

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

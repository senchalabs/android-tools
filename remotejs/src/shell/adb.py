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

_ADB_PORT            = 5037
_LOG_FILTER          = 'RemoteJS'
_TARGET_ACTIVITY     = 'com.sencha.remotejs/.RemoteJS'
_REMOTE_CAPTURE_PATH = '/data/data/com.sencha.remotejs/cache/remotejs-capture.png'

_g_targetDevice = ""
_g_base64Apk    = b"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"

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
    return output

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
        devices = devices.splitlines()
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

def captureScreen(localFileName):
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

    file = open(localFileName, 'wb')
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

def captureWindow(localFileName):
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

    execute("shell am start -a com.sencha.remotejs.ACTION_CAPTURE -n " + _TARGET_ACTIVITY)
    while _isProcessRunning(proc.pid):
        line = proc.stdout.readline()
        if re.match(r'^I/' + _LOG_FILTER, line):
            if line.find('Capture saved') != -1:
                execute('pull ' + _REMOTE_CAPTURE_PATH + ' ' + localFileName)
                return True
            elif line.find('Capture error') != -1:
                return False

def isAvailable():
    return query('version').startswith('Android Debug Bridge')

def installDeviceTool():
    uninstall('com.sencha.remotejs')
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
    expr = base64.b64encode('javascript:(function() { ' + js + '; })()')
    cmd = 'shell am start -a android.intent.action.VIEW -n ' + _TARGET_ACTIVITY \
          + " -d '" + expr + "'"
    execute(cmd)

def openUrl(url):
    encodedUrl = base64.b64encode(url)
    cmd = 'shell am start -a android.intent.action.VIEW -n ' + _TARGET_ACTIVITY \
          + " -d '" + encodedUrl + "'"
    execute(cmd)

def filterLogcat(line):
    line = re.sub(r'[A-Z]/' + _LOG_FILTER + '(\b)*\((\s)*(\d)+\): ', '', line)
    line = re.sub(r'Console: ', '', line)
    line = re.sub(r':(\d)+(\b)*', '', line)
    line = re.sub(r'\r\n', '', line)
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

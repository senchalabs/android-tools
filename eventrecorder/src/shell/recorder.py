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

import atexit
import base64
import os
import re
import readline
import socket
from subprocess import Popen, PIPE, STDOUT
import sys
import tempfile
import time

_OPTION_HELP = "-h"
_OPTION_SKIP = "-n"

_TARGET_PACKAGE = 'com.sencha.eventrecorder'
_TARGET_ACTIVITY = _TARGET_PACKAGE + '/.App'
_STANDARD_PACKAGE = 'android.intent.action'

_ADB_PORT = 5037
_LOG_FILTER = 'EventRecorder'

_INTENT_JAVASCRIPT = "JAVASCRIPT"
_INTENT_RECORD = "RECORD"
_INTENT_SCREEN = "SCREEN"
_INTENT_STOP = "STOP"
_INTENT_TEXT_INPUT = "TEXT_INPUT"
_INTENT_URL = "URL"
_INTENT_VIEW = "VIEW"

_REPLY_DONE = 'done'
_REPLY_READY = 'ready'

class ExitCode:
    Help                = -10
    Normal              = 0
    AdbNotFound         = 5
    NoDevices           = 15
    DeviceToolFailed    = 25
    MultipleDevices     = 35
    Aborted             = 45
    WrongUsage          = 55
    UnknownDevice       = 65

_g_state = {
    'exitCode': ExitCode.Normal,
    'error': '',
    'targetDevice': '',
    'testName': ''
}

_g_base64Apk = b"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"

def exitCode():
    return _g_state['exitCode']

def setExitCode(err):
    global _g_state
    _g_state['exitCode'] = err

def error():
    return _g_state['error']

def setError(err):
    global _g_state
    _g_state['error'] = err

def targetDevice():
    return _g_state['targetDevice']

def testName():
    return _g_state['testName']

def setTargetDevice(id):
    global _g_state
    _g_state['targetDevice'] = id

def setTestName(name):
    global _g_state
    _g_state['testName'] = name

def startAdbConnection():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', _ADB_PORT))
    sendData(sock, 'host:transport:' + targetDevice())
    return readOkay(sock), sock

def clearLogcat():
    cmd = ' logcat -c '
    fullCmd = 'adb '
    if targetDevice():
        fullCmd += '-s ' + targetDevice() + ' '
    fullCmd += cmd
    proc = Popen(fullCmd, shell=True, stdout=PIPE, stderr=STDOUT)
    time.sleep(1)
    proc.kill()

def waitForReply(type):
    cmd = ' logcat ' + _LOG_FILTER + ':V *:S'
    fullCmd = 'adb '
    if targetDevice():
        fullCmd += '-s ' + targetDevice() + ' '
    fullCmd += cmd
    proc = Popen(fullCmd, shell=True, stdout=PIPE, stderr=STDOUT)

    while True:
        line = proc.stdout.readline()

        if re.match(r'^[A-Z]/' + _LOG_FILTER, line):
            line = re.sub(r'[A-Z]/' + _LOG_FILTER + '(\b)*\((\s)*(\d)+\): ', '', line)
            line = re.sub(r'Console: ', '', line)
            line = re.sub(r':(\d)+(\b)*', '', line)
            line = re.sub(r'\r\n', '', line)

            if (line.startswith("#")):
                print line
                continue

            try:
                reply = eval(line)
            except Exception as e:
                setExitCode(ExitCode.Aborted)
                setError('Error in protocol: unrecognized message "' + line + '"')
                raise e

            error = reply['error']
            if error:
                setExitCode(ExitCode.Aborted)
                setError(error)
                raise Exception()

            if reply['type'] == type:
                proc.kill()
                clearLogcat()
                return reply

def printUsage():
    app = os.path.basename(sys.argv[0])
    print "Usage:   ", app, "<name> [options]\t- record test <name>"
    print "Options:                      <device>\t- use <device> serial number as target"
    print "                             ", _OPTION_SKIP, "\t- keep existing tool on the device (advanced)"

def printCommandHelp():
    print "\tYou can open an URL or execute JavaScript code on the remote device.\n" \
          "\tAn URL is assumed if it starts with 'www.', 'http://' or 'ftp://',\n" \
          "\tJavaScript code is assumed otherwise.\n" \
          "\t\n" \
          "\tAvailable special commands:\n" \
          "\t\ts | screen         - Capture screen (excludes status and title bars).\n" \
          "\t\tEnter | Return     - Finish recording."

def readData(socket, max = 4096):
    return socket.recv(max)

def readOkay(socket):
    data = socket.recv(4)
    return data[0] == 'O' and data[1] == 'K' and data[2] == 'A' and data[3] == 'Y'

def sendData(sock, str):
    return sock.sendall('%04X%s' % (len(str), str))

def execute(cmd):
    fullCmd = 'adb '
    if targetDevice():
        fullCmd += '-s ' + targetDevice() + ' '
    fullCmd += cmd
    proc = Popen(fullCmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    proc.stdin.close()
    proc.wait()

def startAdbServer():
    execute('start-server')

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
    try:
        sock.connect(('127.0.0.1', _ADB_PORT))
    except Exception as e:
        setError('Unable to connect to port %d: %s' % (port, e))
        return None
    sendData(sock, 'host:devices')
    if readOkay(sock):
        readData(sock, 4) # payload size in hex
        data = readData(sock)
        reply = ""
        while len(data):
            reply += data
            data = readData(sock)
        sock.close()
        devices = re.sub('List of devices attached\s+', '', reply)
        devices = devices.splitlines()
        list = []
        for elem in devices:
            if elem.find('device') != -1:
                list.append(re.sub(r'\s*device', '', elem))
        return list
    # adb server not running
    sock.close()
    return None

def isAdbAvailable():
    return query('version').startswith('Android Debug Bridge')

def shell(cmd):
    ok, sock = startAdbConnection()
    if not ok:
        return None
    sendData(sock, 'shell:' + cmd)
    if readOkay(sock):
        data = readData(sock)
        result = ""
        while len(data):
            result += data
            data = readData(sock)
        sock.close()
        return result
    else:
        endConnection(sock)
        return None

def sendIntent(intent, package=_TARGET_PACKAGE, data=''):
    clearLogcat()
    cmd = 'am start -a ' + package + '.' + intent + ' -n ' + _TARGET_ACTIVITY
    if data:
        cmd += " -d '" + data + "'"
    shell(cmd)

def pull(remote, local):
    execute('pull ' + remote + ' ' + local)

def uninstall(apk):
    reply = shell('pm uninstall ' + apk)
    if reply:
        return reply.find('Success') != -1
    else:
        return False

def install(apk):
    reply = query('install ' + apk).strip().split('\n')[-1]
    ok = False
    if reply == 'Success':
        ok = True
    return ok, reply

def installDeviceTool():
    uninstall(_TARGET_PACKAGE);
    file = tempfile.NamedTemporaryFile()
    file.write(base64.b64decode(_g_base64Apk))
    file.flush()
    ok, reply = install(file.name)
    file.close()
    return ok, reply

def openUrlOrExecuteJS(expr):
    fullUrlRe = r'^(ftp|http|https)://(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(/|/([\w#!:.?+=&%@!-/]))?'
    if expr.startswith('www') and re.match(fullUrlRe, 'http://' + expr):
        sendIntent(_INTENT_URL, data=base64.b64encode('http://' + expr))
    elif re.match(fullUrlRe, expr):
        sendIntent(_INTENT_URL, data=base64.b64encode(expr))
    else:
        sendIntent(_INTENT_JAVASCRIPT, data=base64.b64encode(expr))

def sendTextInput(text):
    sendIntent(_INTENT_TEXT_INPUT, data=base64.b64encode(text))

def inputLoop():
    historyFile = os.path.join(os.environ["HOME"], '.eventrecorder-history')
    try:
        readline.read_history_file(historyFile)
    except IOError:
        pass
    atexit.register(readline.write_history_file, historyFile)
    del historyFile

    expr = ""
    while True:
        expr = raw_input('>>> ').strip()
        if expr == 's' or expr == 'screen':
            sendIntent(_INTENT_SCREEN)
        elif expr.startswith('t '):
            sendTextInput(expr[2:])
        elif expr.startswith('text '):
            sendTextInput(expr[5:])
        elif expr == 'h' or expr == 'help':
            printCommandHelp()
        elif expr == '':
            raise Exception()
        else:
            openUrlOrExecuteJS(expr)

def main():
    args = sys.argv[1:]

    if _OPTION_HELP in args:
        printUsage()
        return ExitCode.Help

    if not isAdbAvailable():
        print "'adb' not found, please add its location to $PATH."
        return ExitCode.AdbNotFound

    startAdbServer()
    deviceList = devices()

    if not deviceList or len(deviceList) == 0:
        print "No attached devices."
        return ExitCode.NoDevices

    elif len(args) == 1 and len(deviceList) > 1:
        print "Multiple devices attached, one must be specified."
        return ExitCode.MultipleDevices

    elif len(args) > 3 or len(args) == 0:
        printUsage()
        return ExitCode.WrongUsage

    elif len(args) == 2 and args[1] != _OPTION_SKIP:
        if args[1] not in deviceList:
            print "Device not found."
            return ExitCode.UnknownDevice
        else:
            setTargetDevice(args[1])

    elif len(args) == 3:
        if args[1] not in deviceList and args[2] not in deviceList:
            print "Device not found."
            return ExitCode.UnknownDevice
        elif args[1] in deviceList:
            setTargetDevice(args[1])
        else:
            setTargetDevice(args[2])

    else:
        setTargetDevice(deviceList[0])

    setTestName(args[0])

    print "EventRecorder - Remote Web Application Test Recorder for Android."
    print "Target device is " + targetDevice() + "."

    if not _OPTION_SKIP in args:
        print "Installing device tool..."
        ok, error = installDeviceTool()
        if not ok:
            print "Device tool installation failed -", error
            return ExitCode.DeviceToolFailed

    try:
        print "Launching device tool..."
        sendIntent(_INTENT_VIEW, _STANDARD_PACKAGE)
        reply = waitForReply(_REPLY_READY)

        sendIntent(_INTENT_RECORD)
        reply = waitForReply(_REPLY_READY)

        print "Recording... [press Enter key when done, type 'h' or 'help' for instructions]"
        try:
            inputLoop()
        except:
            print "Stopping recording..."
            sendIntent(_INTENT_STOP)
            reply = waitForReply(_REPLY_DONE)

            localFileName = testName() + '.py'
            print "Fetching playback file as '" + localFileName + "'..."
            prefix = reply['filesPath']
            script = reply['testScriptFile']
            remoteFileName = prefix + '/' + script
            pull(remoteFileName, localFileName)

            print "Done."
    except Exception as e:
        code = exitCode()
        if code == ExitCode.Aborted:
            print _g_state['error']
        return code

if __name__ == "__main__":
    sys.exit(main())

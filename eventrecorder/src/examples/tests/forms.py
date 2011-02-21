#!/usr/bin/env python

_g_isPilAvailable = False
try:
    from PIL import Image
    _g_isPilAvailable = True
except:
    pass

from subprocess import Popen, PIPE, STDOUT
import base64
import math
import os
import re
import socket
import struct
import sys
import tempfile
import thread
import time

_OPTION_DEVICE = "-s"
_OPTION_HELP = "-h"

_TARGET_PACKAGE = 'com.sencha.eventrecorder'
_TARGET_ACTIVITY = _TARGET_PACKAGE + '/.App'
_STANDARD_PACKAGE = 'android.intent.action'

_ADB_PORT = 5037
_LOG_FILTER = 'EventRecorder'

_INTENT_PLAY = "PLAY"
_INTENT_PUSH_DONE = "PUSH_DONE"
_INTENT_SCREEN_DONE = "SCREEN_DONE"
_INTENT_VIEW = "VIEW"

_REPLY_DONE = 'done'
_REPLY_READY = 'ready'
_REPLY_SCREEN = 'screen'
_REPLY_EVENTS_PATH = 'eventsFilePath'

_CONSOLE_LOG_FILE_NAME = "console.log"
_SCREEN_CAPTURE_PREFIX = "screen"
_WINDOW_CAPTURE_PREFIX = "window"

class ExitCode:
    Help                = -10
    Normal              = 0
    AdbNotFound         = 5
    NoDevices           = 15
    DeviceDisconnected  = 25
    MultipleDevices     = 35
    Aborted             = 45
    WrongUsage          = 55
    UnknownDevice       = 65

_g_state = {
    'exitCode': ExitCode.Normal,
    'error': '',
    'screenCaptureCount': 0,
    'targetDevice': ''
}

_g_events = '0 url http://dev.sencha.com/deploy/touch/examples/forms\n0 pause\n2077 touch 0 337.44077 131.49135 7.9125 7.9424996 0.47 0.06666667 131074 0 0\n2088 touch 2 337.31436 131.49135 7.9125 7.9424996 0.48999998 0.06666667 131074 0 0\n2113 touch 2 337.6935 132.7504 7.9125 7.9424996 0.5 0.06666667 131074 0 0\n2162 touch 2 338.83096 133.88354 7.9125 7.9424996 0.26 0.13333334 131074 0 0\n2173 touch 1 338.83096 133.88354 7.9125 7.9424996 0.26 0.13333334 131074 0 0\n4968 text John Smith\n6148 touch 0 329.60504 215.72177 7.9125 7.9424996 0.42999998 0.06666667 131074 0 0\n6161 touch 2 329.73145 215.84766 7.9125 7.9424996 0.47 0.06666667 131074 0 0\n6289 touch 1 329.22592 215.84766 7.9125 7.9424996 0.17 0.06666667 131074 0 0\n10287 text Mypassword\n11348 touch 0 343.25433 366.05228 7.9125 7.9424996 0.45999998 0.06666667 131074 0 0\n11362 touch 2 343.25433 365.92636 7.9125 7.9424996 0.47 0.06666667 131074 0 0\n11441 touch 2 345.40283 367.3113 7.9125 7.9424996 0.21 0.13333334 131074 0 0\n11455 touch 1 345.40283 367.3113 7.9125 7.9424996 0.21 0.13333334 131074 0 0\n15207 text me@sencha\n16565 touch 0 340.6003 420.94684 7.9125 7.9424996 0.26999998 0.06666667 131074 0 0\n16580 touch 2 340.8531 421.07272 7.9125 7.9424996 0.31 0.06666667 131074 0 0\n16609 touch 2 340.22116 422.45767 7.9125 7.9424996 0.45 0.06666667 131074 0 0\n16632 touch 2 339.2101 422.45767 7.9125 7.9424996 0.47 0.06666667 131074 0 0\n16667 touch 2 340.47394 422.3318 7.9125 7.9424996 0.26 0.13333334 131074 0 0\n16691 touch 1 339.9684 422.7095 7.9125 7.9424996 0.14 0.13333334 131074 0 0\n20561 text www.sencha.com\n22542 touch 0 422.62244 562.0863 7.9125 7.9424996 0.39 0.06666667 131074 0 0\n22552 touch 2 422.7488 562.21216 7.9125 7.9424996 0.39999998 0.06666667 131074 0 0\n22654 touch 2 423.5071 563.34534 7.9125 7.9424996 0.41 0.06666667 131074 0 0\n22677 touch 2 424.39178 564.47845 7.9125 7.9424996 0.17999999 0.06666667 131074 0 0\n22691 touch 1 424.39178 564.47845 7.9125 7.9424996 0.17999999 0.06666667 131074 0 0\n23456 touch 0 423.12796 558.30914 7.9125 7.9424996 0.37 0.06666667 131074 0 0\n23471 touch 2 423.25433 557.9314 7.9125 7.9424996 0.39 0.06666667 131074 0 0\n23498 touch 2 423.7599 558.93866 7.9125 7.9424996 0.39999998 0.06666667 131074 0 0\n23544 touch 2 423.88626 560.4495 7.9125 7.9424996 0.39999998 0.06666667 131074 0 0\n23614 touch 1 424.01263 560.7013 7.9125 7.9424996 0.17 0.06666667 131074 0 0\n25194 touch 0 328.21484 558.93866 7.9125 7.9424996 0.38 0.06666667 131074 0 0\n25203 touch 2 328.21484 559.31635 7.9125 7.9424996 0.45 0.06666667 131074 0 0\n25237 touch 2 327.2038 560.1977 7.9125 7.9424996 0.48999998 0.06666667 131074 0 0\n25307 touch 2 328.34122 559.31635 7.9125 7.9424996 0.48999998 0.06666667 131074 0 0\n25344 touch 1 329.22592 558.5609 7.9125 7.9424996 0.21 0.06666667 131074 0 0\n29640 text 25\n33442 touch 0 333.14377 503.41455 7.9125 7.9424996 0.39999998 0.06666667 131074 0 0\n33452 touch 2 332.76462 503.7923 7.9125 7.9424996 0.42999998 0.06666667 131074 0 0\n33543 touch 2 333.3965 504.9254 7.9125 7.9424996 0.25 0.06666667 131074 0 0\n33555 touch 1 333.3965 504.9254 7.9125 7.9424996 0.25 0.06666667 131074 0 0\n34031 screen\n'

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

def setTargetDevice(id):
    global _g_state
    _g_state['targetDevice'] = id

def startConnection(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(('127.0.0.1', port))
        return sock
    except Exception as e:
        setError('Unable to connect to port %d: %s' % (port, e))

def clearLogcat():
    cmd = ' logcat -c '
    fullCmd = 'adb '
    if targetDevice():
        fullCmd += '-s ' + targetDevice() + ' '
    fullCmd += cmd
    proc = Popen(fullCmd, shell=True, stdout=PIPE, stderr=STDOUT)
    time.sleep(1)
    proc.kill()

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

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', _ADB_PORT))
    sendData(sock, 'host:transport:' + targetDevice())
    ok = readOkay(sock)
    if not ok:
        return None, None
    sendData(sock, 'framebuffer:')
    if readOkay(sock):
        version = struct.unpack('@I', readData(sock, 4))[0] # ntohl
        if version == 16: # compatibility mode
            headerFields = 3 # size, width, height
        else:
            headerFields = 12 # bpp, size, width, height, 4*(offset, length)
        header = headerMap(struct.unpack('@IIIIIIIIIIII', readData(sock, headerFields * 4)))
        sendData(sock, '\x00')
        data = readData(sock)
        result = ""
        while len(data):
            result += data
            data = readData(sock)
        sock.close()
        return header, result # pass size returned in header
    else:
        sock.close()
        return None, None

def captureScreen(localFileName, skipLines = 0):
    header, data = framebuffer()
    width = header['width']
    height = header['height']
    dimensions = (width, height)
    if header['bpp'] == 32:
        components = {header['red']['offset']: 'R',
                      header['green']['offset']: 'G',
                      header['blue']['offset']: 'B'}
        alpha = header['alpha']['length'] != 0
        if alpha:
            components[header['alpha']['offset']] = 'A'
        format = '' + components[0] + components[8] + components[16]
        if alpha:
            format += components[24]
            image = Image.fromstring('RGBA', dimensions, data, 'raw', format)
        else:
            image = Image.fromstring('RGBA', dimensions, data)
        r, g, b, a = image.split()
        image = Image.merge('RGB', (r, g, b))
    else: # assuming BGR565
        image = Image.fromstring('RGB', dimensions, data, 'raw', 'BGR;16')
    image = image.crop((0, skipLines, width - 1, height - 1))
    image.save(localFileName, optimize=1)

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

            if reply['type'] == _REPLY_SCREEN:
                if not _g_isPilAvailable:
                    setExitCode(ExitCode.Aborted)
                    setError('Screen capture requested but Python Imaging Library (PIL) not found.')
                    raise Exception()

                _g_state['screenCaptureCount'] += 1
                localFileName = _SCREEN_CAPTURE_PREFIX + `_g_state['screenCaptureCount']` + '.png'
                skipLines = reply['skipLines']
                captureScreen(localFileName, skipLines)
                sendIntent(_INTENT_SCREEN_DONE)

            elif reply['type'] == type:
                proc.kill()
                clearLogcat()
                return reply

def printUsage():
    app = os.path.basename(sys.argv[0])
    print "Usage: ", app, "\t\t- assume one attached device only"
    print "       ", app, _OPTION_DEVICE, "<id>\t- connect to device with serial number <id>"
    print "       ", app, _OPTION_HELP, "\t\t- print this help"

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
    sock = startConnection(_ADB_PORT)
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
    else: # adb server not running
        sock.close()
        return None

def isAvailable():
    return query('version').startswith('Android Debug Bridge')

def sendIntent(intent, package=_TARGET_PACKAGE, data=''):
    clearLogcat()
    cmd = 'shell am start -a ' + package + '.' + intent + ' -n ' + _TARGET_ACTIVITY
    if data:
        cmd += " -d '" + data + "'"
    execute(cmd)

def pull(remote, local):
    execute('pull ' + remote + ' ' + local)

def push(local, remote):
    execute('push ' + local + ' ' + remote)

def runTest():
    def checkError(r):
        error = r['error']
        if error:
            setExitCode(ExitCode.Aborted)
            setError(error)
            raise Exception()

    print "Launching remote application..."
    sendIntent(_INTENT_VIEW, _STANDARD_PACKAGE)
    reply = waitForReply(_REPLY_READY)
    checkError(reply)

    print "Sending playback events..."
    sendIntent(_INTENT_PLAY)
    reply = waitForReply(_REPLY_EVENTS_PATH)
    file = tempfile.NamedTemporaryFile()
    file.write(_g_events)
    file.flush()

    push(file.name, reply["value"])
    file.close()
    sendIntent(_INTENT_PUSH_DONE)

    print "Playing test..."
    reply = waitForReply(_REPLY_DONE)
    checkError(reply)

    prefix = reply['filesPath']
    consoleLogFile = reply['consoleLogFile']

    print "Fetching results..."
    pull(remote=(prefix+'/'+consoleLogFile), local=_CONSOLE_LOG_FILE_NAME)

    print "Done."

def main():
    args = sys.argv[1:]

    if _OPTION_HELP in args:
        printUsage()
        return ExitCode.Help

    if not isAvailable():
        print "'adb' not found, please add its location to $PATH."
        return ExitCode.AdbNotFound

    startAdbServer()
    deviceList = devices()

    if len(deviceList) == 0:
        print "No attached devices."
        return ExitCode.NoDevices

    if _OPTION_DEVICE in args:
        try:
            serial = args[args.index(_OPTION_DEVICE) + 1]
        except IndexError:
            print "Must specify a device serial number."
            return ExitCode.WrongUsage
        if serial in deviceList:
            setTargetDevice(serial)
        else:
            print "Device " + serial + " not found."
            return ExitCode.UnknownDevice
    else:
        if len(deviceList) > 1:
            print "Multiple devices attached, one must be specified."
            return ExitCode.MultipleDevices

    print "EventRecorder - Remote Automated Web Application Testing for Android."
    if not targetDevice():
        setTargetDevice(deviceList[0])

    print "Target device is " + targetDevice() + "."

    try:
        runTest()
    except Exception as e:
        print e
        code = exitCode()
        if code == ExitCode.Normal:
            print "Exiting..."
        elif code == ExitCode.DeviceDisconnected:
            print "Device disconnected."
        elif code == ExitCode.Aborted:
            print _g_state['error']
        return code

if __name__ == "__main__":
    sys.exit(main())

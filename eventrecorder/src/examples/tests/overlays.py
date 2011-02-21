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

_g_events = '0 url http://dev.sencha.com/deploy/touch/examples/overlays/\n0 pause\n4139 screen\n5819 touch 0 99.5079 721.1138 0.0 0.0 0.23921569 0.06666667 65540 0 0\n5850 touch 2 98.49895 715.8324 0.0 0.0 0.25882354 0.06666667 65540 0 0\n5873 touch 2 98.12059 714.8264 0.0 0.0 0.2627451 0.06666667 65540 0 0\n5908 touch 2 97.61611 713.569 0.0 0.0 0.27058825 0.06666667 65540 0 0\n5931 touch 2 97.74223 712.31146 0.0 0.0 0.27058825 0.06666667 65540 0 0\n5989 touch 2 99.12954 719.22754 0.0 0.0 0.27058825 0.06666667 65540 0 0\n6001 touch 1 99.12954 719.22754 0.0 0.0 0.27058825 0.06666667 65540 0 0\n7298 touch 0 109.21906 713.569 0.0 0.0 0.23529412 0.06666667 65540 0 0\n7327 touch 2 109.471306 713.94617 0.0 0.0 0.23529412 0.06666667 65540 0 0\n7351 touch 2 113.25487 722.62274 0.0 0.0 0.23529412 0.06666667 65540 0 0\n7363 touch 1 113.25487 722.62274 0.0 0.0 0.23529412 0.06666667 65540 0 0\n10848 screen\n11942 touch 0 244.41864 261.75797 0.0 0.0 0.23529412 0.06666667 65540 0 0\n11963 touch 2 244.29254 261.25494 0.0 0.0 0.2627451 0.06666667 65540 0 0\n12009 touch 2 244.54475 260.12323 0.0 0.0 0.28235295 0.06666667 65540 0 0\n12102 touch 2 244.1664 261.6322 0.0 0.0 0.29803923 0.06666667 65540 0 0\n12125 touch 2 243.66194 263.7699 0.0 0.0 0.29803923 0.06666667 65540 0 0\n12206 touch 2 243.4097 280.24283 0.0 0.0 0.29803923 0.06666667 65540 0 0\n12218 touch 2 243.28355 283.13504 0.0 0.0 0.29803923 0.06666667 65540 0 0\n12241 touch 2 242.52686 288.16495 0.0 0.0 0.29803923 0.06666667 65540 0 0\n12265 touch 2 242.1485 292.8176 0.0 0.0 0.29803923 0.06666667 65540 0 0\n12299 touch 2 241.64401 298.60196 0.0 0.0 0.29803923 0.06666667 65540 0 0\n12325 touch 2 240.63506 302.50015 0.0 0.0 0.29803923 0.06666667 65540 0 0\n12358 touch 2 238.99553 307.9073 0.0 0.0 0.29803923 0.06666667 65540 0 0\n12381 touch 2 237.98657 311.80548 0.0 0.0 0.29803923 0.06666667 65540 0 0\n12418 touch 2 236.59926 319.22458 0.0 0.0 0.29803923 0.06666667 65540 0 0\n12438 touch 2 235.4642 324.50595 0.0 0.0 0.29803923 0.06666667 65540 0 0\n12462 touch 2 234.70747 331.79935 0.0 0.0 0.29803923 0.06666667 65540 0 0\n12497 touch 2 233.44629 345.6316 0.0 0.0 0.29803923 0.06666667 65540 0 0\n12521 touch 2 232.56346 353.6794 0.0 0.0 0.29803923 0.06666667 65540 0 0\n12557 touch 2 231.42838 363.362 0.0 0.0 0.29803923 0.06666667 65540 0 0\n12579 touch 2 230.54555 369.0206 0.0 0.0 0.29803923 0.06666667 65540 0 0\n12602 touch 2 229.6627 375.43375 0.0 0.0 0.29803923 0.06666667 65540 0 0\n12638 touch 2 229.28436 390.39767 0.0 0.0 0.29803923 0.06666667 65540 0 0\n12661 touch 2 228.65376 402.97244 0.0 0.0 0.29803923 0.06666667 65540 0 0\n12684 touch 2 227.77094 412.7808 0.0 0.0 0.29803923 0.06666667 65540 0 0\n12718 touch 2 226.38362 423.59506 0.0 0.0 0.29803923 0.06666667 65540 0 0\n12741 touch 2 226.00526 432.14587 0.0 0.0 0.29803923 0.06666667 65540 0 0\n12776 touch 2 225.37466 451.00806 0.0 0.0 0.29803923 0.06666667 65540 0 0\n12800 touch 2 225.12244 461.1936 0.0 0.0 0.29803923 0.06666667 65540 0 0\n12837 touch 2 224.61797 471.0019 0.0 0.0 0.29803923 0.06666667 65540 0 0\n12858 touch 2 224.23961 476.66052 0.0 0.0 0.29803923 0.06666667 65540 0 0\n12882 touch 2 224.49184 487.85205 0.0 0.0 0.1882353 0.06666667 65540 0 0\n12894 touch 2 224.11348 501.18134 0.0 0.0 0.09019608 0.06666667 65540 0 0\n12906 touch 1 224.11348 501.18134 0.0 0.0 0.09019608 0.06666667 65540 0 0\n13908 touch 0 401.3107 705.8983 0.0 0.0 0.24313726 0.06666667 65540 0 0\n13928 touch 2 400.30176 706.2756 0.0 0.0 0.24705882 0.06666667 65540 0 0\n14020 touch 2 413.92258 714.7006 0.0 0.0 0.05882353 0.2 65540 0 0\n14032 touch 1 413.92258 714.7006 0.0 0.0 0.05882353 0.2 65540 0 0\n14971 touch 0 404.84204 719.35333 0.0 0.0 0.22745098 0.06666667 65540 0 0\n14992 touch 2 405.59875 720.1078 0.0 0.0 0.23137255 0.06666667 65540 0 0\n15050 touch 2 408.7517 724.7605 0.0 0.0 0.23137255 0.06666667 65540 0 0\n15063 touch 1 408.7517 724.7605 0.0 0.0 0.23137255 0.06666667 65540 0 0\n16106 touch 0 416.82333 719.60486 0.0 0.0 0.1882353 0.06666667 65540 0 0\n16115 touch 2 416.0666 718.4731 0.0 0.0 0.20784314 0.06666667 65540 0 0\n16231 touch 2 415.9405 717.4671 0.0 0.0 0.21568628 0.06666667 65540 0 0\n16289 touch 2 418.08453 718.0959 0.0 0.0 0.21568628 0.06666667 65540 0 0\n16313 touch 1 418.08453 718.0959 0.0 0.0 0.21568628 0.06666667 65540 0 0\n16864 touch 0 397.9055 703.88635 0.0 0.0 0.25490198 0.06666667 65540 0 0\n16873 touch 2 398.28384 703.88635 0.0 0.0 0.25882354 0.06666667 65540 0 0\n16911 touch 2 398.28384 705.14386 0.0 0.0 0.2627451 0.06666667 65540 0 0\n16994 touch 2 398.53607 706.14984 0.0 0.0 0.2627451 0.06666667 65540 0 0\n17017 touch 2 401.18457 708.66473 0.0 0.0 0.2627451 0.06666667 65540 0 0\n17028 touch 2 403.70694 710.42523 0.0 0.0 0.2627451 0.06666667 65540 0 0\n17040 touch 1 403.70694 710.42523 0.0 0.0 0.2627451 0.06666667 65540 0 0\n21356 screen\n23145 touch 0 219.44708 180.52502 0.0 0.0 0.24705882 0.06666667 65540 0 0\n23211 touch 2 220.07767 181.15378 0.0 0.0 0.25490198 0.06666667 65540 0 0\n23223 touch 2 218.81648 183.79446 0.0 0.0 0.105882354 0.06666667 65540 0 0\n23235 touch 1 218.81648 183.79446 0.0 0.0 0.105882354 0.06666667 65540 0 0\n24433 touch 0 63.81622 52.38826 0.0 0.0 0.25882354 0.06666667 65540 0 0\n24457 touch 2 63.437862 52.136765 0.0 0.0 0.2627451 0.06666667 65540 0 0\n24511 touch 2 64.82517 50.6278 0.0 0.0 0.27058825 0.06666667 65540 0 0\n24557 touch 1 64.69905 50.502045 0.0 0.0 0.0627451 0.06666667 65540 0 0\n27380 screen\n'

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

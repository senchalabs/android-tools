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

_g_events = '0 url http://dev.sencha.com/deploy/touch/examples/icons/\n0 pause\n5859 screen\n7696 touch 0 159.83368 682.83636 0.0 0.0 0.21176471 0.2 65538 0 0\n7811 touch 1 159.83368 682.83636 0.0 0.0 0.21176471 0.2 65538 0 0\n10024 touch 0 121.75418 697.36365 0.0 0.0 0.1764706 0.2 65538 0 0\n10055 touch 2 121.75418 697.36365 0.0 0.0 0.22745098 0.25 65538 0 0\n10240 touch 1 121.75418 697.36365 0.0 0.0 0.18431373 0.25 65538 0 0\n11671 touch 0 258.0387 679.41815 0.0 0.0 0.21176471 0.3 65538 0 0\n11731 touch 2 258.0387 679.41815 0.0 0.0 0.25490198 0.3 65538 0 0\n11853 touch 1 258.0387 679.41815 0.0 0.0 0.09803922 0.1 65538 0 0\n12627 touch 0 356.74478 694.8 0.0 0.0 0.22352941 0.3 65538 0 0\n12794 touch 1 356.74478 694.8 0.0 0.0 0.22352941 0.3 65538 0 0\n13533 touch 0 441.92258 687.1091 0.0 0.0 0.1882353 0.2 65538 0 0\n13658 touch 2 441.92258 687.1091 0.0 0.0 0.0627451 0.05 65538 0 0\n13702 touch 1 441.92258 687.1091 0.0 0.0 0.0627451 0.05 65538 0 0\n15992 touch 0 434.90796 43.63636 0.0 0.0 0.22352941 0.3 65538 0 0\n16119 touch 2 434.90796 43.63636 0.0 0.0 0.14117648 0.15 65538 0 0\n16162 touch 1 434.90796 43.63636 0.0 0.0 0.14117648 0.15 65538 0 0\n17293 touch 0 361.75522 36.800003 0.0 0.0 0.24313726 0.3 65538 0 0\n17403 touch 2 361.75522 36.800003 0.0 0.0 0.12156863 0.1 65538 0 0\n17446 touch 1 361.75522 36.800003 0.0 0.0 0.12156863 0.1 65538 0 0\n18079 touch 0 303.13284 29.963638 0.0 0.0 0.25882354 0.3 65538 0 0\n18246 touch 1 303.13284 29.963638 0.0 0.0 0.25882354 0.3 65538 0 0\n18798 touch 0 237.99687 45.34545 0.0 0.0 0.23921569 0.2 65538 0 0\n18907 touch 2 237.99687 45.34545 0.0 0.0 0.17254902 0.2 65538 0 0\n18951 touch 1 237.99687 45.34545 0.0 0.0 0.17254902 0.2 65538 0 0\n19502 touch 0 170.85669 37.65455 0.0 0.0 0.27058825 0.35 65538 0 0\n19596 touch 2 170.85669 37.65455 0.0 0.0 0.09019608 0.05 65538 0 0\n19640 touch 1 170.85669 37.65455 0.0 0.0 0.09019608 0.05 65538 0 0\n20192 touch 0 117.74582 34.236366 0.0 0.0 0.24705882 0.35 65538 0 0\n20302 touch 2 117.74582 34.236366 0.0 0.0 0.07058824 0.05 65538 0 0\n20345 touch 1 117.74582 34.236366 0.0 0.0 0.07058824 0.05 65538 0 0\n20944 touch 0 54.614017 39.363632 0.0 0.0 0.2509804 0.3 65538 0 0\n20990 touch 2 54.614017 39.363632 0.0 0.0 0.29411766 0.35 65538 0 0\n21113 touch 1 54.614017 39.363632 0.0 0.0 0.0627451 0.05 65538 0 0\n21617 touch 0 293.11194 282.05453 0.0 0.0 0.1764706 0.15 65538 0 0\n21664 touch 2 293.11194 282.05453 0.0 0.0 0.21960784 0.2 65538 0 0\n21713 touch 2 287.09937 281.2 0.0 0.0 0.21960784 0.3 65538 0 0\n21743 touch 2 238.99895 278.63638 0.0 0.0 0.21960784 0.25 65538 0 0\n21761 touch 2 225.4707 278.63638 0.0 0.0 0.21960784 0.3 65538 0 0\n21789 touch 2 198.41423 283.76364 0.0 0.0 0.21960784 0.2 65538 0 0\n21821 touch 2 179.87552 286.32727 0.0 0.0 0.21960784 0.25 65538 0 0\n21852 touch 2 165.34518 288.03638 0.0 0.0 0.21960784 0.25 65538 0 0\n21884 touch 2 157.32845 288.89093 0.0 0.0 0.21960784 0.2 65538 0 0\n21900 touch 2 155.32426 289.74545 0.0 0.0 0.21960784 0.25 65538 0 0\n21930 touch 2 144.30125 289.74545 0.0 0.0 0.21960784 0.3 65538 0 0\n21962 touch 2 123.25732 288.89093 0.0 0.0 0.21960784 0.25 65538 0 0\n21993 touch 2 117.74582 288.89093 0.0 0.0 0.21960784 0.25 65538 0 0\n22011 touch 2 112.73535 287.18182 0.0 0.0 0.21960784 0.25 65538 0 0\n22042 touch 2 102.71443 285.47272 0.0 0.0 0.21960784 0.25 65538 0 0\n22071 touch 2 98.70607 282.9091 0.0 0.0 0.21960784 0.35 65538 0 0\n22135 touch 2 103.215485 282.05453 0.0 0.0 0.21960784 0.3 65538 0 0\n22152 touch 2 137.2866 277.78183 0.0 0.0 0.21960784 0.3 65538 0 0\n22182 touch 2 188.39331 276.07272 0.0 0.0 0.21960784 0.3 65538 0 0\n22212 touch 2 222.96547 272.65454 0.0 0.0 0.21960784 0.25 65538 0 0\n22244 touch 2 238.4979 271.80002 0.0 0.0 0.21960784 0.3 65538 0 0\n22275 touch 2 240.5021 272.65454 0.0 0.0 0.21960784 0.35 65538 0 0\n22292 touch 2 241.5042 274.36365 0.0 0.0 0.21960784 0.3 65538 0 0\n22322 touch 2 244.00943 317.0909 0.0 0.0 0.21960784 0.2 65538 0 0\n22353 touch 2 236.99477 368.36362 0.0 0.0 0.16862746 0.15 65538 0 0\n22385 touch 2 230.48117 398.2727 0.0 0.0 0.16862746 0.2 65538 0 0\n22402 touch 2 228.97804 411.94547 0.0 0.0 0.1254902 0.15 65538 0 0\n22432 touch 2 225.97176 419.63635 0.0 0.0 0.078431375 0.1 65538 0 0\n22478 touch 1 225.97176 419.63635 0.0 0.0 0.078431375 0.1 65538 0 0\n24109 touch 0 124.259415 34.236366 0.0 0.0 0.26666668 0.35 65538 0 0\n24360 touch 2 121.253136 35.090904 0.0 0.0 0.26666668 0.4 65538 0 0\n24421 touch 2 120.25105 35.090904 0.0 0.0 0.26666668 0.35 65538 0 0\n24625 touch 2 119.24895 35.090904 0.0 0.0 0.26666668 0.35 65538 0 0\n25741 touch 2 118.24686 35.94545 0.0 0.0 0.26666668 0.4 65538 0 0\n26728 touch 2 117.24477 36.800003 0.0 0.0 0.26666668 0.4 65538 0 0\n26944 touch 2 116.242676 36.800003 0.0 0.0 0.30980393 0.4 65538 0 0\n27116 screen\n27210 touch 2 115.74164 38.509094 0.0 0.0 0.30980393 0.4 65538 0 0\n27478 touch 2 114.73954 38.509094 0.0 0.0 0.30980393 0.4 65538 0 0\n27695 touch 1 114.73954 38.509094 0.0 0.0 0.25490198 0.35 65538 0 0\n'

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

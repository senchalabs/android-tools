#!/usr/bin/env python

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

import adb
import os
import re
import sys
import thread

OPTION_DEVICE = "-s"
OPTION_HELP = "-h"
OPTION_HELP_LONG = "--help"
OPTION_NOHOSTUPDATE = "-n"

class ExitCode:
    Undefined           = -100
    Help                = -10
    Normal              = 0
    AdbNotFound         = 5
    NoDevices           = 15
    DeviceDisconnected  = 25
    MultipleDevices     = 35
    Aborted             = 45
    DeviceToolFailed    = 55
    WrongUsage          = 65
    UnknownDevice       = 75
    BadSleepValue       = 85

_g_exitCode = ExitCode.Undefined

def exitCode():
    return _g_exitCode

def setExitCode(err):
    global _g_exitCode
    _g_exitCode = err

def printError(msg):
    print >> sys.stderr, "#", msg

def printInfo(msg):
    print "#", msg

def printUsage():
    app = os.path.basename(sys.argv[0])
    print "Usage: ", app, "\t\t- assume one attached device only"
    print "       ", app, OPTION_DEVICE, "<id>\t\t- connect to device with serial number <id>"
    print "       ", app, OPTION_NOHOSTUPDATE, "\t\t- keep existing host tool (advanced)"
    print "       ", app, OPTION_HELP, "|", OPTION_HELP_LONG, "\t- print this help"

def logcatHandler(line):
    print adb.filterLogcat(line)

def logcatThread():
    adb.readLogcat(logcatHandler)
    setExitCode(ExitCode.DeviceDisconnected)
    thread.interrupt_main()

def execute(expr):
    fullUrlRe = r"^(ftp|http|https)://(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(/|/([\w#!:.?+=&%@!-/]))?"
    if expr.startswith("www") and re.match(fullUrlRe, "http://" + expr):
        adb.openUrl("http://" + expr)
    elif re.match(fullUrlRe, expr):
        adb.openUrl(expr)
    else:
        adb.evaluateJS(expr)

def inputThread():
    expr = ""
    try:
        while True:
            expr = raw_input().strip()
            if expr == "":
                continue
            else:
                execute(expr)
    except:
        setExitCode(ExitCode.Normal)
        thread.interrupt_main()

def mainThread():
    args = sys.argv[1:]

    if OPTION_HELP in args or OPTION_HELP_LONG in args:
        printUsage()
        return ExitCode.Help

    if not adb.isAvailable():
        printError("'adb' not found, please add its location to $PATH.")
        return ExitCode.AdbNotFound

    adb.startServer()
    devices = adb.devices()

    if len(devices) == 0:
        printError("No attached devices.")
        return ExitCode.NoDevices

    if OPTION_DEVICE in args:
        try:
            serial = args[args.index(OPTION_DEVICE) + 1]
        except IndexError:
            printError("Must specify a device serial number.")
            return ExitCode.WrongUsage
        if serial in devices:
            adb.setTargetDevice(serial)
        else:
            printError("Device " + serial + " not found.")
            return ExitCode.UnknownDevice
    else:
        if len(devices) > 1:
            printError("Multiple devices attached, one must be specified.")
            return ExitCode.MultipleDevices

    printInfo("RemoteJS - Remote JavaScript Console for Android.")
    printInfo("Please wait...")
    if not adb.targetDevice():
        adb.setTargetDevice(devices[0])

    if not OPTION_NOHOSTUPDATE in args:
        error = adb.installDeviceTool()
        if exitCode() > ExitCode.Normal:
            if exitCode() == ExitCode.DeviceToolFailed:
                printError("Device tool installation failed - " + error)
            else:
                printError("Aborted while installing host tool.")
            return exitCode()

    printInfo("Target device is " + adb.targetDevice() + ".")

    thread.start_new_thread(logcatThread, ())
    thread.start_new_thread(inputThread, ())

    try:
        while True:
            pass
    except:
        if exitCode() == ExitCode.Undefined or exitCode() == ExitCode.Normal:
            printInfo("Exiting...")
        elif exitCode() == ExitCode.DeviceDisconnected:
            printError("Device disconnected.")
        return exitCode()

if __name__ == "__main__":
    sys.exit(mainThread())

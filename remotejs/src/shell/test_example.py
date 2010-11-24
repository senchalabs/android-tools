#!/usr/bin/env python

from adb import *
e = evaluateJS

import thread
import time

expected = ['3', 'Map', '0', '1', '2', '1.0.0']
obtained = []

def myFilter(line):
    l = filterLogcat(line)
    global obtained
    obtained += (l,)
    return l

# if there's more than one attached device, one needs to be specified
#setTargetDevice('...')

# can be commented if device already has the tool
installDeviceTool()

thread.start_new_thread(readLogcat, (myFilter,))
openUrl('http://dev.sencha.com/deploy/touch/examples/map/')
time.sleep(5)

e('console.log(1+2)')
e('console.log(document.title)')
e('for (var i = 0; i < 3; ++i) console.log(i)')
e('console.log(Ext.version)')

captureWindow('viewport.png')

errorCount = 0
for i in range(min(len(obtained), len(expected))):
    if expected[i] != obtained[i]:
        print 'Expected[' + `i` + ']: ' + expected[i]
        print 'Obtained[' + `i` + ']: ' + obtained[i]
        errorCount += 1
if errorCount:
    print 'Found ' + `errorCount` + ' errors in ' + `len(expected)` + ' tests'

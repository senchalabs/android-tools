#!/usr/bin/env python

import base64
import os

if __name__ == "__main__":
    fileName = "../android/bin/EventRecorder.apk"
    file = open(fileName, "rb")
    fileContent = file.read()
    file.close()
    apk = base64.b64encode(fileContent)

    fileName = "recorder.py"
    file = open(fileName, "rb")
    fileLines = file.readlines()
    file.close()

    file = open(fileName, "wb")
    for i in range(len(fileLines)):
        if fileLines[i].startswith("_g_base64Apk = "):
            fileLines[i] = '_g_base64Apk = b"' + apk + '"\n'
            break
    file.writelines(fileLines)
    file.close()

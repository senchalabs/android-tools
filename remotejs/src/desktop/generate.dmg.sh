#!/bin/sh
make clean
rm -rf RemoteJS.app
qmake
make
macdeployqt RemoteJS.app -dmg

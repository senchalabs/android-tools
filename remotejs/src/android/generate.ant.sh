#!/bin/sh
if [ ! -f "build.xml" -o ! -f "local.properties" ]; then
    android update project -p .
fi

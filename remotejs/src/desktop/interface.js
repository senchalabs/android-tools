/*
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
*/

var MAX_HISTORY_SIZE = 100;
var DEVICE_RESCAN_TIMEOUT = 2000;

var expressionHistory = [];
var currentExpressionIndex = -1;
var isJustLaunched = true;
var liveExpression = "";
var rescanTimeoutId = null;

window.onresize = function() {
    var header = document.getElementById('header');
    document.body.style.paddingTop = header.offsetHeight;
}

function loadHistory() {
    var i;
    var length = localStorage["HistoryLength"];
    for (i = 0; i < length; ++i)
        expressionHistory.push(localStorage["HistoryExpression" + i]);
}

function addToHistory(s) {
    if (s == expressionHistory[expressionHistory.length - 1])
        return;
    expressionHistory.push(s);
    currentExpressionIndex = -1;
    if (expressionHistory.length > MAX_HISTORY_SIZE)
        expressionHistory.shift();
}

function getPreviousExpression() {
    if (currentExpressionIndex == 0 || expressionHistory.length < 2)
        return expressionHistory[currentExpressionIndex];
    else if (currentExpressionIndex == -1)
        currentExpressionIndex = expressionHistory.length - 1;
    else
        --currentExpressionIndex;
    return expressionHistory[currentExpressionIndex];
}

function getNextExpression() {
    if (currentExpressionIndex == -1)
        return liveExpression;
    else if (currentExpressionIndex == (expressionHistory.length - 1)) {
        currentExpressionIndex = -1;
        return liveExpression;
    } else {
        ++currentExpressionIndex;
        return expressionHistory[currentExpressionIndex];
    }
}

function saveHistory() {
    var i;
    var length = expressionHistory.length;
    for (i = 0; i < length; ++i)
        localStorage["HistoryExpression" + i] = expressionHistory[i];
    localStorage["HistoryLength"] = length;
}

function aboutToQuit() {
    saveHistory();
    remoteConsole.disconnected.disconnect(gotDisconnected);
}

function addHorizontalRule() {
    if (isJustLaunched)
        return;
    var hr = document.createElement('hr');
    hr.setAttribute('size', '1');
    hr.setAttribute('color', '#F0F0F0');
    document.getElementById('content').appendChild(hr);
}

function addJSCommand(s) {
    addHorizontalRule();
    var content = document.getElementById('content');
    var e = document.createElement('code');
    highlightText('> ' + s, e);
    content.appendChild(e);
    window.scrollTo(0, 1e9);
}

function addJSResult(s) {
    var content = document.getElementById('content');
    var e = document.createElement('code');
    if (s.match("^[a-z A-Z]*Error:")) {
        e.setAttribute('style', 'color: red');
        e.innerText = s;
    } else
        highlightText(s, e);
    content.appendChild(e);
    window.scrollTo(0, 1e9);
}

function addLaunchURL(s) {
    addHorizontalRule();
    var e = document.createElement('p');
    e.setAttribute('style', 'color: deepskyblue');
    e.appendChild(document.createTextNode('Opening ' + s));
    document.getElementById('content').appendChild(e);
    window.scrollTo(0, 1e9);
}

function execute() {
    var cmd = document.getElementById('userinput').value.replace(/^\s\s*/, '').replace(/\s\s*$/, ''); // trim
    if (cmd == "")
        return false;
    var regexp = /(ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/
    if (cmd.match("^www.") || regexp.test(cmd)) {
        addLaunchURL(cmd);
        remoteConsole.openUrl(cmd);
    } else {
        remoteConsole.evaluateJavaScript(cmd);
        addJSCommand(cmd);
    }
    addToHistory(cmd);
    document.getElementById('userinput').value = "";
    if (isJustLaunched)
        isJustLaunched = !isJustLaunched;
    return false;
}

function handleKey(e) {
    var evt = e || window.event;

    // Hack to work around Shift-9 (opening paranthesis) reporting keycode 40
    if (evt.shiftKey)
        return;

    switch (evt.keyCode) {
    case 33: // page up
    case 38: // arrow up
        var s = getPreviousExpression();
        document.getElementById('userinput').value = s;
        break;
    case 34: // page down
    case 40: // arrow down
        var s = getNextExpression();
        document.getElementById('userinput').value = s;
        break;
    case 37: // arrow left
    case 39: // arrow right
        break;
    default:
        var element = document.getElementById('userinput');
        var value = element.value;
        var caret = element.selectionStart;
        var char = String.fromCharCode(evt.charCode);
        liveExpression = value.substring(0, caret) + char + value.substring(caret);
        currentExpressionIndex = -1;
    }
    window.scrollTo(0, 1e9);
}

function showError(msg) {
    var e = document.getElementById('error');
    if (!e) {
        e = document.createElement('p');
        e.setAttribute('style', 'color: orangered');
        e.setAttribute('id', 'error');
        e.appendChild(document.createTextNode(msg));
        document.getElementById('header').appendChild(e);
    } else {
        e.firstChild.nodeValue = msg;
        e.style.display = 'block';
    }
    window.onresize();
}

function hideError() {
    var e = document.getElementById('error');
    if (e)
        e.style.display = 'none';
}

function gotDisconnected() {
    remoteConsole.dataAvailable.disconnect(addJSResult);
    remoteConsole.aboutToQuit.disconnect(aboutToQuit);
    remoteConsole.disconnected.disconnect(gotDisconnected);
    remoteConsole.targetDevice = '';

    showError('adb (Android Debug Bridge) is disconnected!');

    document.getElementById('entry').style.display = 'none';
    document.getElementById('help').style.display = 'none';
    var dev = document.getElementById('devicename');
    if (dev)
        dev.style.display = 'none';

    showDeviceMenu();
}

function selectDevice(device) {
    remoteConsole.dataAvailable.connect(addJSResult);
    remoteConsole.aboutToQuit.connect(aboutToQuit);
    remoteConsole.disconnected.connect(gotDisconnected);
    remoteConsole.targetDevice = device;

    var devicename = document.getElementById('devicename');
    if (devicename) {
        devicename.style.display = 'block';
        devicename.firstChild.nodeValue = "Target device is " + device + ".";
    } else {
        devicename = document.createElement('p');
        devicename.setAttribute('style', 'color: lightgreen');
        devicename.setAttribute('id', 'devicename');
        devicename.appendChild(document.createTextNode("Target device is " + device + "."));
        document.getElementById('header').appendChild(devicename);
    }

    document.getElementById('devicelist').style.display = 'none';
    document.getElementById('entry').style.display = 'inline';
    document.getElementById('help').style.display = 'inline';
    document.getElementById('userinput').onkeydown = handleKey;
    document.getElementById('userinput').onkeypress = handleKey;

    hideError();

    var msg = remoteConsole.installDeviceTool();
    if (msg && msg != "Success")
        showError("Unable to auto-install host tool: " + msg);
}

function showDeviceMenu() {
    document.getElementById('devicelist').style.display = 'inline';
    var menu = document.getElementById('devicemenu');
    var list = remoteConsole.deviceList;

    if (list.length == 0) {
        showError('No devices found. Please connect your device.');
        document.getElementById('devices').style.display = 'none';

        while (menu.hasChildNodes())
            menu.removeChild(menu.firstChild);

        rescanTimeoutId = setTimeout("showDeviceMenu()", DEVICE_RESCAN_TIMEOUT);
    } else {
        if (rescanTimeoutId != null) {
            clearTimeout(rescanTimeoutId);
            rescanTimeoutId = null;
        }

        if (list.length == 1) {
            selectDevice(list[0]);
        } else {
            // Remove any old children added by a previous call to this function
            while (menu.hasChildNodes())
                menu.removeChild(menu.firstChild);

            for (i = 0; i < list.length; ++i) {
                var b = document.createElement('button');
                b.setAttribute('onClick', 'selectDevice("' + list[i] + '")');
                b.className = "device";
                var t = document.createTextNode(list[i]);
                b.appendChild(t);
                menu.appendChild(b);
            }
        }
        loadHistory();
    }
    window.onresize();
}

var adbPath = localStorage.adbPath;
if (adbPath != undefined) {
    remoteConsole.adbPath = adbPath;
}

if (!remoteConsole.isAdbAvailable) {
    adbPath = remoteConsole.chooseAdbPath();
    remoteConsole.adbPath = adbPath;
    if (!remoteConsole.isAdbAvailable) {
        showError('adb (Android Debug Bridge) is not available. Please set PATH to the Android SDK installation!');
    } else {
        showDeviceMenu();
        localStorage.adbPath = adbPath;
    }
} else {
    showDeviceMenu();
}

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

_g_events = '0 url http://dev.sencha.com/deploy/touch/examples/picker/\n0 pause\n4291 touch 0 289.66824 378.89456 7.9125 7.9424996 0.47 0.06666667 131074 0 0\n4306 touch 2 288.90994 378.89456 7.9125 7.9424996 0.52 0.06666667 131074 0 0\n4322 touch 2 287.64612 378.13916 7.9125 7.9424996 0.56 0.06666667 131074 0 0\n4345 touch 2 287.01422 376.75418 7.9125 7.9424996 0.58 0.06666667 131074 0 0\n4380 touch 2 287.26697 375.49515 7.9125 7.9424996 0.58 0.06666667 131074 0 0\n4394 touch 2 287.77252 372.3475 7.9125 7.9424996 0.29 0.06666667 131074 0 0\n4406 touch 1 287.77252 372.3475 7.9125 7.9424996 0.29 0.06666667 131074 0 0\n8147 screen\n9344 touch 0 162.65402 655.50775 7.9125 7.9424996 0.31 0.06666667 131074 0 0\n9353 touch 2 162.65402 656.3891 7.9125 7.9424996 0.34 0.06666667 131074 0 0\n9364 touch 2 162.52765 657.3963 7.9125 7.9424996 0.37 0.06666667 131074 0 0\n9376 touch 2 162.1485 658.40356 7.9125 7.9424996 0.39999998 0.06666667 131074 0 0\n9386 touch 2 161.89574 659.5367 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n9398 touch 2 161.76935 660.54395 7.9125 7.9424996 0.44 0.06666667 131074 0 0\n9479 touch 2 162.52765 654.6264 7.9125 7.9424996 0.51 0.06666667 131074 0 0\n9491 touch 2 163.15956 649.84204 7.9125 7.9424996 0.52 0.06666667 131074 0 0\n9502 touch 2 163.41232 645.0576 7.9125 7.9424996 0.52 0.06666667 131074 0 0\n9514 touch 2 163.79147 640.27325 7.9125 7.9424996 0.52 0.06666667 131074 0 0\n9525 touch 2 164.54976 635.48883 7.9125 7.9424996 0.52 0.06666667 131074 0 0\n9538 touch 2 165.43443 630.20087 7.9125 7.9424996 0.52 0.06666667 131074 0 0\n9548 touch 2 166.19273 624.40924 7.9125 7.9424996 0.52 0.06666667 131074 0 0\n9561 touch 2 167.07741 617.9881 7.9125 7.9424996 0.52 0.06666667 131074 0 0\n9571 touch 2 167.83571 610.4338 7.9125 7.9424996 0.52 0.06666667 131074 0 0\n9583 touch 2 168.72038 602.6277 7.9125 7.9424996 0.52 0.06666667 131074 0 0\n9594 touch 2 169.73143 595.4511 7.9125 7.9424996 0.52 0.06666667 131074 0 0\n9606 touch 2 170.86888 589.40765 7.9125 7.9424996 0.52 0.06666667 131074 0 0\n9652 touch 2 176.17694 571.27734 7.9125 7.9424996 0.52 0.06666667 131074 0 0\n9698 touch 2 181.48499 550.7548 7.9125 7.9424996 0.52 0.06666667 131074 0 0\n9732 touch 2 185.15009 537.7866 7.9125 7.9424996 0.52 0.06666667 131074 0 0\n9744 touch 2 186.16113 534.639 7.9125 7.9424996 0.52 0.06666667 131074 0 0\n9779 touch 2 188.56241 528.34375 7.9125 7.9424996 0.52 0.06666667 131074 0 0\n9790 touch 2 188.94154 526.8329 7.9125 7.9424996 0.52 0.06666667 131074 0 0\n9826 touch 2 190.079 523.68524 7.9125 7.9424996 0.52 0.06666667 131074 0 0\n9849 touch 2 190.20537 521.9226 7.9125 7.9424996 0.52 0.06666667 131074 0 0\n9906 touch 2 190.33176 519.6563 7.9125 7.9424996 0.52 0.06666667 131074 0 0\n9940 touch 2 190.83728 518.3973 7.9125 7.9424996 0.52 0.06666667 131074 0 0\n9998 touch 2 190.7109 517.39 7.9125 7.9424996 0.52 0.06666667 131074 0 0\n10116 touch 2 190.83728 516.38275 7.9125 7.9424996 0.52 0.06666667 131074 0 0\n10194 touch 2 193.99684 517.8936 7.9125 7.9424996 0.28 0.06666667 131074 0 0\n10205 touch 2 192.73302 517.39 7.9125 7.9424996 0.13 0.13333334 131074 0 0\n10217 touch 1 192.73302 517.39 7.9125 7.9424996 0.13 0.13333334 131074 0 0\n10624 touch 0 166.4455 692.9015 7.9125 7.9424996 0.21 0.06666667 131074 0 0\n10638 touch 2 166.19273 691.3906 7.9125 7.9424996 0.39 0.06666667 131074 0 0\n10657 touch 2 165.93997 690.2575 7.9125 7.9424996 0.48 0.06666667 131074 0 0\n10680 touch 2 166.06635 688.9985 7.9125 7.9424996 0.51 0.06666667 131074 0 0\n10714 touch 2 166.95102 684.9695 7.9125 7.9424996 0.51 0.06666667 131074 0 0\n10725 touch 2 168.08847 680.5628 7.9125 7.9424996 0.51 0.06666667 131074 0 0\n10739 touch 2 169.3523 674.6453 7.9125 7.9424996 0.51 0.06666667 131074 0 0\n10748 touch 2 170.36334 665.58014 7.9125 7.9424996 0.51 0.06666667 131074 0 0\n10766 touch 2 171.75356 655.13 7.9125 7.9424996 0.52 0.06666667 131074 0 0\n10772 touch 2 173.39653 644.9317 7.9125 7.9424996 0.53 0.06666667 131074 0 0\n10783 touch 2 175.41864 635.23706 7.9125 7.9424996 0.53 0.06666667 131074 0 0\n10795 touch 2 177.69353 624.91284 7.9125 7.9424996 0.53 0.06666667 131074 0 0\n10806 touch 2 180.34755 612.7001 7.9125 7.9424996 0.53 0.06666667 131074 0 0\n10882 touch 2 195.13428 565.3598 7.9125 7.9424996 0.53 0.06666667 131074 0 0\n10894 touch 2 196.27173 561.8345 7.9125 7.9424996 0.53 0.06666667 131074 0 0\n10929 touch 2 199.17851 552.3916 7.9125 7.9424996 0.53 0.06666667 131074 0 0\n10963 touch 2 200.44234 547.6072 7.9125 7.9424996 0.53 0.06666667 131074 0 0\n10975 touch 2 200.56873 546.2222 7.9125 7.9424996 0.53 0.06666667 131074 0 0\n11022 touch 2 201.70616 542.3192 7.9125 7.9424996 0.53 0.06666667 131074 0 0\n11056 touch 2 201.95892 540.68243 7.9125 7.9424996 0.53 0.06666667 131074 0 0\n11102 touch 2 202.46445 539.1716 7.9125 7.9424996 0.53 0.06666667 131074 0 0\n11206 touch 2 202.46445 538.03845 7.9125 7.9424996 0.53 0.06666667 131074 0 0\n11403 touch 2 202.8436 537.0312 7.9125 7.9424996 0.53999996 0.06666667 131074 0 0\n11483 touch 2 204.10742 537.283 7.9125 7.9424996 0.53999996 0.06666667 131074 0 0\n11506 touch 2 206.12955 536.27576 7.9125 7.9424996 0.31 0.06666667 131074 0 0\n11517 touch 1 206.12955 536.27576 7.9125 7.9424996 0.31 0.06666667 131074 0 0\n12377 touch 0 276.65088 690.7611 7.9125 7.9424996 0.35 0.06666667 131074 0 0\n12388 touch 2 276.3981 690.50934 7.9125 7.9424996 0.39 0.06666667 131074 0 0\n12420 touch 2 276.3981 689.5021 7.9125 7.9424996 0.45 0.06666667 131074 0 0\n12445 touch 2 276.27173 687.8653 7.9125 7.9424996 0.45999998 0.06666667 131074 0 0\n12456 touch 2 276.27173 686.48035 7.9125 7.9424996 0.45999998 0.06666667 131074 0 0\n12466 touch 2 276.14532 684.5918 7.9125 7.9424996 0.45999998 0.06666667 131074 0 0\n12479 touch 2 276.52448 681.8219 7.9125 7.9424996 0.45999998 0.06666667 131074 0 0\n12490 touch 2 276.65088 678.2966 7.9125 7.9424996 0.45999998 0.06666667 131074 0 0\n12504 touch 2 276.65088 674.01575 7.9125 7.9424996 0.45999998 0.06666667 131074 0 0\n12512 touch 2 276.52448 667.7205 7.9125 7.9424996 0.45999998 0.06666667 131074 0 0\n12524 touch 2 276.27173 659.6626 7.9125 7.9424996 0.47 0.06666667 131074 0 0\n12535 touch 2 276.14532 651.6047 7.9125 7.9424996 0.48 0.06666667 131074 0 0\n12547 touch 2 276.52448 644.1763 7.9125 7.9424996 0.48 0.06666667 131074 0 0\n12560 touch 2 276.90363 637.7551 7.9125 7.9424996 0.48 0.06666667 131074 0 0\n12570 touch 2 277.40915 631.5858 7.9125 7.9424996 0.48 0.06666667 131074 0 0\n12581 touch 2 278.16745 624.661 7.9125 7.9424996 0.48 0.06666667 131074 0 0\n12593 touch 2 278.67297 617.10675 7.9125 7.9424996 0.48 0.06666667 131074 0 0\n12605 touch 2 279.3049 609.5524 7.9125 7.9424996 0.48 0.06666667 131074 0 0\n12662 touch 2 281.20062 584.37146 7.9125 7.9424996 0.48999998 0.06666667 131074 0 0\n12708 touch 2 282.0853 576.6912 7.9125 7.9424996 0.5 0.06666667 131074 0 0\n12744 touch 2 282.33807 573.2918 7.9125 7.9424996 0.5 0.06666667 131074 0 0\n12789 touch 2 282.46445 570.6478 7.9125 7.9424996 0.5 0.06666667 131074 0 0\n12836 touch 2 283.34912 566.36707 7.9125 7.9424996 0.5 0.06666667 131074 0 0\n12882 touch 2 284.48657 561.58264 7.9125 7.9424996 0.5 0.06666667 131074 0 0\n12893 touch 2 284.86572 559.94586 7.9125 7.9424996 0.5 0.06666667 131074 0 0\n12939 touch 2 285.49762 555.791 7.9125 7.9424996 0.5 0.06666667 131074 0 0\n12951 touch 2 285.87677 554.40607 7.9125 7.9424996 0.5 0.06666667 131074 0 0\n12997 touch 2 286.63507 549.3699 7.9125 7.9424996 0.5 0.06666667 131074 0 0\n13043 touch 2 286.88785 546.47406 7.9125 7.9424996 0.5 0.06666667 131074 0 0\n13089 touch 2 287.39337 544.08185 7.9125 7.9424996 0.5 0.06666667 131074 0 0\n13136 touch 2 288.02527 542.4451 7.9125 7.9424996 0.5 0.06666667 131074 0 0\n13181 touch 2 289.16272 539.1716 7.9125 7.9424996 0.5 0.06666667 131074 0 0\n13216 touch 2 289.66824 537.1571 7.9125 7.9424996 0.5 0.06666667 131074 0 0\n13262 touch 2 290.6793 535.14264 7.9125 7.9424996 0.5 0.06666667 131074 0 0\n13320 touch 2 291.81674 534.2613 7.9125 7.9424996 0.5 0.06666667 131074 0 0\n13366 touch 2 293.08057 533.88354 7.9125 7.9424996 0.5 0.06666667 131074 0 0\n13400 touch 2 295.48184 533.37994 7.9125 7.9424996 0.35999998 0.06666667 131074 0 0\n13424 touch 2 294.47076 532.4986 7.9125 7.9424996 0.13 0.13333334 131074 0 0\n13435 touch 1 294.47076 532.4986 7.9125 7.9424996 0.13 0.13333334 131074 0 0\n14102 touch 0 266.66666 687.2358 7.9125 7.9424996 0.34 0.06666667 131074 0 0\n14118 touch 2 266.2875 686.8581 7.9125 7.9424996 0.39 0.06666667 131074 0 0\n14139 touch 2 265.78198 685.3472 7.9125 7.9424996 0.42999998 0.06666667 131074 0 0\n14153 touch 2 265.78198 683.9623 7.9125 7.9424996 0.42999998 0.06666667 131074 0 0\n14163 touch 2 265.78198 681.696 7.9125 7.9424996 0.42999998 0.06666667 131074 0 0\n14175 touch 2 266.03476 678.67426 7.9125 7.9424996 0.42999998 0.06666667 131074 0 0\n14186 touch 2 266.16113 674.14166 7.9125 7.9424996 0.42999998 0.06666667 131074 0 0\n14198 touch 2 266.4139 667.34283 7.9125 7.9424996 0.44 0.06666667 131074 0 0\n14209 touch 2 266.79306 659.5367 7.9125 7.9424996 0.45999998 0.06666667 131074 0 0\n14220 touch 2 267.42496 651.47876 7.9125 7.9424996 0.48 0.06666667 131074 0 0\n14232 touch 2 267.93048 644.0504 7.9125 7.9424996 0.48999998 0.06666667 131074 0 0\n14246 touch 2 268.68878 637.7551 7.9125 7.9424996 0.48999998 0.06666667 131074 0 0\n14258 touch 2 269.57346 631.4599 7.9125 7.9424996 0.48999998 0.06666667 131074 0 0\n14266 touch 2 270.83728 624.661 7.9125 7.9424996 0.48999998 0.06666667 131074 0 0\n14277 touch 2 271.72195 616.6031 7.9125 7.9424996 0.48999998 0.06666667 131074 0 0\n14289 touch 2 272.8594 607.53796 7.9125 7.9424996 0.48999998 0.06666667 131074 0 0\n14335 touch 2 275.6398 582.60876 7.9125 7.9424996 0.48999998 0.06666667 131074 0 0\n14383 touch 2 278.67297 570.77374 7.9125 7.9424996 0.48999998 0.06666667 131074 0 0\n14416 touch 2 280.18958 564.10077 7.9125 7.9424996 0.48999998 0.06666667 131074 0 0\n14428 touch 2 280.31595 562.8417 7.9125 7.9424996 0.48999998 0.06666667 131074 0 0\n14462 touch 2 280.6951 561.70856 7.9125 7.9424996 0.48999998 0.06666667 131074 0 0\n14508 touch 2 280.56873 560.3236 7.9125 7.9424996 0.48999998 0.06666667 131074 0 0\n14589 touch 2 280.44235 559.1905 7.9125 7.9424996 0.48999998 0.06666667 131074 0 0\n14844 touch 2 279.43127 559.0646 7.9125 7.9424996 0.48999998 0.06666667 131074 0 0\n14902 touch 2 280.6951 560.4495 7.9125 7.9424996 0.32 0.06666667 131074 0 0\n14919 touch 2 280.94788 559.0646 7.9125 7.9424996 0.17 0.13333334 131074 0 0\n14925 touch 1 280.94788 559.0646 7.9125 7.9424996 0.17 0.13333334 131074 0 0\n15895 touch 0 418.95734 691.01294 7.9125 7.9424996 0.35999998 0.06666667 131074 0 0\n15909 touch 2 418.95734 690.887 7.9125 7.9424996 0.38 0.06666667 131074 0 0\n15928 touch 2 418.7046 689.8798 7.9125 7.9424996 0.39 0.06666667 131074 0 0\n15950 touch 2 418.5782 688.74664 7.9125 7.9424996 0.39999998 0.06666667 131074 0 0\n15973 touch 2 418.7046 686.48035 7.9125 7.9424996 0.39999998 0.06666667 131074 0 0\n15985 touch 2 418.4518 684.9695 7.9125 7.9424996 0.39999998 0.06666667 131074 0 0\n15997 touch 2 418.32544 682.8291 7.9125 7.9424996 0.39999998 0.06666667 131074 0 0\n16011 touch 2 418.19907 679.9333 7.9125 7.9424996 0.39999998 0.06666667 131074 0 0\n16020 touch 2 417.9463 675.6525 7.9125 7.9424996 0.39999998 0.06666667 131074 0 0\n16031 touch 2 417.6935 668.09827 7.9125 7.9424996 0.39999998 0.06666667 131074 0 0\n16043 touch 2 417.188 659.6626 7.9125 7.9424996 0.39999998 0.06666667 131074 0 0\n16055 touch 2 416.68246 651.6047 7.9125 7.9424996 0.39999998 0.06666667 131074 0 0\n16065 touch 2 416.4297 644.0504 7.9125 7.9424996 0.41 0.06666667 131074 0 0\n16077 touch 2 416.17694 636.87384 7.9125 7.9424996 0.41 0.06666667 131074 0 0\n16089 touch 2 415.41864 629.6972 7.9125 7.9424996 0.41 0.06666667 131074 0 0\n16100 touch 2 414.66034 622.3947 7.9125 7.9424996 0.41 0.06666667 131074 0 0\n16118 touch 2 413.14377 613.9591 7.9125 7.9424996 0.41 0.06666667 131074 0 0\n16192 touch 2 402.9068 577.069 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n16203 touch 2 401.5166 572.9141 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n16238 touch 2 399.2417 558.43506 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n16279 touch 2 399.74722 547.2295 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n16291 touch 2 399.87363 544.71136 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n16325 touch 2 400.0 540.80835 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n16360 touch 2 399.49448 539.04565 7.9125 7.9424996 0.42999998 0.06666667 131074 0 0\n16430 touch 2 399.36807 537.91254 7.9125 7.9424996 0.44 0.06666667 131074 0 0\n16487 touch 2 398.98895 536.77936 7.9125 7.9424996 0.45 0.06666667 131074 0 0\n16672 touch 2 400.37915 535.77216 7.9125 7.9424996 0.45999998 0.06666667 131074 0 0\n16752 touch 2 403.6651 534.8908 7.9125 7.9424996 0.22 0.06666667 131074 0 0\n16766 touch 1 403.6651 534.8908 7.9125 7.9424996 0.22 0.06666667 131074 0 0\n17393 touch 0 399.87363 693.27924 7.9125 7.9424996 0.29 0.06666667 131074 0 0\n17405 touch 2 398.86255 693.6569 7.9125 7.9424996 0.32999998 0.06666667 131074 0 0\n17441 touch 2 397.72513 693.6569 7.9125 7.9424996 0.39999998 0.06666667 131074 0 0\n17462 touch 2 397.21957 692.6497 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n17497 touch 2 398.35703 689.8798 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n17508 touch 2 399.11533 687.9912 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n17520 touch 2 399.49448 685.8508 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n17531 touch 2 400.37915 683.33276 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n17542 touch 2 400.88467 680.1851 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n17560 touch 2 400.7583 675.77844 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n17578 touch 2 400.88467 660.418 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n17588 touch 2 400.88467 652.486 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n17600 touch 2 401.3902 645.5613 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n17612 touch 2 401.64297 639.5178 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n17625 touch 2 402.52765 634.60754 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n17634 touch 2 403.41232 630.07495 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n17646 touch 2 404.04422 625.7942 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n17658 touch 2 404.67615 620.8839 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n17669 touch 2 405.6872 615.5959 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n17715 touch 2 407.45654 594.31793 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n17761 touch 2 408.594 583.86786 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n17784 touch 2 409.09952 579.9648 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n17809 touch 2 410.1106 575.3063 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n17842 touch 2 411.5008 567.24835 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n17854 touch 2 412.1327 564.35254 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n17888 touch 2 413.27014 555.53925 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n17900 touch 2 413.14377 553.65063 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n17934 touch 2 413.27014 549.8735 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n17981 touch 2 412.76462 547.4813 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n18027 touch 2 412.51184 545.34094 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n18315 touch 2 412.38547 546.34814 7.9125 7.9424996 0.42 0.06666667 131074 0 0\n18415 touch 2 413.77567 546.85175 7.9125 7.9424996 0.31 0.06666667 131074 0 0\n18437 touch 1 413.3965 547.1036 7.9125 7.9424996 0.17999999 0.06666667 131074 0 0\n21223 screen\n22557 touch 0 440.18958 456.2002 7.9125 7.9424996 0.32 0.06666667 131074 0 0\n22568 touch 2 439.55765 456.07428 7.9125 7.9424996 0.41 0.06666667 131074 0 0\n22588 touch 2 437.66193 456.07428 7.9125 7.9424996 0.47 0.06666667 131074 0 0\n22634 touch 2 436.65088 455.6966 7.9125 7.9424996 0.48999998 0.06666667 131074 0 0\n22669 touch 1 436.65088 455.6966 7.9125 7.9424996 0.29999998 0.06666667 131074 0 0\n24202 javascript javascript:console.log(Ext.getCmp(\'ext-comp-1004\').getValue())\n25931 touch 0 258.4518 403.06833 7.9125 7.9424996 0.48999998 0.06666667 131074 0 0\n25942 touch 2 257.9463 403.19424 7.9125 7.9424996 0.51 0.06666667 131074 0 0\n25965 touch 2 256.93524 402.81653 7.9125 7.9424996 0.52 0.06666667 131074 0 0\n26011 touch 2 260.72668 403.19424 7.9125 7.9424996 0.31 0.06666667 131074 0 0\n26023 touch 2 263.5071 402.0611 7.9125 7.9424996 0.17 0.06666667 131074 0 0\n26035 touch 1 263.5071 402.0611 7.9125 7.9424996 0.17 0.06666667 131074 0 0\n27259 touch 0 261.9905 374.86563 7.9125 7.9424996 0.55 0.06666667 131074 0 0\n27269 touch 2 261.485 375.24335 7.9125 7.9424996 0.57 0.06666667 131074 0 0\n27326 touch 2 264.39178 372.85114 7.9125 7.9424996 0.26999998 0.06666667 131074 0 0\n27338 touch 2 268.18326 373.48065 7.9125 7.9424996 0.13 0.06666667 131074 0 0\n27349 touch 1 268.18326 373.48065 7.9125 7.9424996 0.13 0.06666667 131074 0 0\n30293 screen\n32492 javascript javascript:console.log(Ext.getCmp(\'ext-comp-1004\').getValue())\n'

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

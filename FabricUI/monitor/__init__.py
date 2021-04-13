#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 02.01.2020
Updated on 04.12.2021

Author: haoshuai@handaotech.com
'''

import platform
from .time_monitor import TimeMonitor
from .fps_monitor import FPSMonitor
from .save_worker import SaveWorker

system = platform.system()

if system == "Windows":
    from .rev_monitor_win import RevMonitor
elif system == "Linux":
    from .rev_monitor_trt import RevMonitor
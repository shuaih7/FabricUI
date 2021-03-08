#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 02.01.2020
Updated on 03.03.2021

Author: haoshaui@handaotech.com
'''

import platform
from .time_monitor import TimeMonitor
from .fps_monitor import FPSMonitor

system = platform.system()

if system == "Windows":
    from .rev_monitor_win import RevMonitor
elif system == "Linux":
    from .rev_monitor_trt import RevMonitor
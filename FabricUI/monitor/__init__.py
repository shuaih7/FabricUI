#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 02.01.2020
Updated on 02.05.2021

Author: haoshaui@handaotech.com
'''

import platform

system = platform.system()

if system == "Windows":
    from .rev_monitor_win import RevMonitor
elif system == "Linux":
    from .rev_monitor_trt import RevMonitor
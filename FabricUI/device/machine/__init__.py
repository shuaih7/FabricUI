#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 03.19.2021
Updated on 03.19.2021

Author: haoshuai@handaotech.com
'''

import platform

system = platform.system()

if system == "Windows":
    from .machine_win import Machine
elif system == "Linux":
    from .machine_trt import Machine


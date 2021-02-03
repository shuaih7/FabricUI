#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 02.01.2020
Updated on 02.01.2021

Author: haoshaui@handaotech.com
'''

import platform

system = platform.system()

if system == "Windows":
    from .rev_win_worker import RevWorker
elif system == "Linux":
    from .rev_worker import RevWorker
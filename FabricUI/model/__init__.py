#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.20.2020
Updated on 01.28.2021

Author: haoshaui@handaotech.com
'''

import platform

system = platform.system()

if system == "Windows":
    from .win import CudaModel
elif system == "Linux":
    from .trt import CudaModel



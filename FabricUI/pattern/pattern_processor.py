#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 03.02.2021
Updated on 03.09.2021

Author: haoshuai@handaotech.com
'''


import os
import sys
import cv2
import numpy as np
from .pattern_filter import PatternFilter
from .pattern_recorder import PatternRecorder


class PatternProcessor(object):
    def __init__(self, params):
        self.updateParams(params)
        
    def updateParams(self, params):
        self.filter = PatternFilter(params)
        self.recorder = PatternRecorder(params)
        self.params = params
        
    def __call__(self, results):
        results = self.recorder(results)
        results = self.filter(results)
        return results
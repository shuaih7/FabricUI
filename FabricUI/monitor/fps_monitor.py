#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 03.08.2020
Updated on 03.11.2021

Author: haoshuai@handaotech.com
'''


import os
import time
from .data_struct import MonitorQueue


class FPSMonitor(object):
    def __init__(self, params):
        self.updateParams(params)
        
    def updateParams(self, params):
        qlen = params['queue_length']
        self.fps_queue = MonitorQueue(qlen)
        self.start = 0
        self.params = params
        
    def initTimer(self):
        self.start = time.time()
        
    def startTimer(self):
        self.start = time.time()
        
    def countTime(self):
        return time.time() - self.start
        
    def countLoop(self):
        end_time = time.time()
        intv = end_time - self.start
        self.start = end_time
        # self.fps_queue.append(intv)
        return intv
        
    def updateFPSStatus(self, fps):
        self.fps_queue.append(fps)
        
    def updateIntvStatus(self, intv):
        self.fps_queue.append(intv)
        
    def getAverage(self):
        return self.fps_queue.getAverage()
    
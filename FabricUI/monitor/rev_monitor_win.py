#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.20.2020
Updated on 04.25.2021

Author: haoshuai@handaotech.com
'''


import os
import time

from PyQt5.QtCore import QThread, pyqtSignal

from .data_struct import MonitorQueue


class RevMonitor(QThread):
    revSignal = pyqtSignal(float)

    def __init__(self, params, parent=None):
        super(RevMonitor, self).__init__(parent)
        self.updateParams(params)
        
    def updateParams(self, params):
        self.params = params
        
        self.is_steady = False
        self.steady_turns = params["steady_turns"]
        self.rev_offset = params["rev_offset"]
        self.rev_queue = MonitorQueue(self.steady_turns)
        
        self.recent_time = time.time()
        self.recent_rev = 0.0001
        
    def checkRevStatus(self):
        interval = time.time() - self.recent_time
        max_cycle_intv = 60.0 / max(0.001, self.recent_rev-self.rev_offset) + 1.0
        
        if interval > max_cycle_intv:
            self.is_steady = False
            temp_rev = max(0.0, self.recent_rev-self.rev_offset-0.001)
            self.revSignal.emit(round(temp_rev, 3))
            self.rev_queue.append(temp_rev)
            
    def updateRevStatus(self, rev):
        self.rev_queue.append(rev)
        
        if rev <= self.rev_offset:
            self.is_steady = False
        elif not self.rev_queue.is_full:
            self.is_steady = False
        elif self.rev_queue.getDiff() < self.rev_offset:
            self.is_steady = True
        else:
            self.is_steady = False

    def run(self):
        cur_cycle = 0
        while True:
            self.checkRevStatus()
            self.recent_time = time.time()
            time.sleep(3)
            cur_cycle += 1
            
            rev = 19.6
            self.updateRevStatus(rev)
            self.revSignal.emit(rev)
            self.recent_rev = rev
            if cur_cycle % 6 == 0: time.sleep(3)

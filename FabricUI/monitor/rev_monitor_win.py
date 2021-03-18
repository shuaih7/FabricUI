#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.20.2020
Updated on 03.18.2021

Author: haoshuai@handaotech.com
'''


import os
import time

from PyQt5.QtCore import QThread, pyqtSignal


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
        self.rev_queue = list()

    def run(self):
        cur_cycle = 0
        while True:
            time.sleep(3)
            cur_cycle += 1
            self.revSignal.emit(20.001)
            if cur_cycle == self.steady_turns: self.is_steady = True
#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.20.2020
Updated on 03.02.2021

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
        self.revSignal.emit(0.0)
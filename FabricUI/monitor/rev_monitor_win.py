#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.20.2020
Updated on 12.30.2020

Author: haoshaui@handaotech.com
'''


import os
import time

from PyQt5.QtCore import QThread, pyqtSignal


class RevMonitor(QThread):
    revSignal = pyqtSignal(float)

    def __init__(self, params, parent=None):
        super(RevMonitor, self).__init__(parent)
        self.params = params

    def run(self):
        self.revSignal.emit(0.0)
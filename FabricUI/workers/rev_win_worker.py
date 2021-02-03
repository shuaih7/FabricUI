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


class RevWorker(QThread):
    revSignal = pyqtSignal(float)

    def __init__(self, config_matrix, logger, parent=None):
        super(RevWorker, self).__init__(parent)
        self.config_matrix = config_matrix
        self.logger = logger

    def run(self):
        pass
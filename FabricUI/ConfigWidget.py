#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on 03.17.2020
Updated on 04.19.2020

Author: 212780558
"""

import os, sys
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QTabWidget, QFileDialog

class ConfigWidget(QTabWidget):
    camConfigRequest = pyqtSignal(str)
    opListUpdateRequest = pyqtSignal(bool)
    bleSettingRequest = pyqtSignal(bool)
    
    def __init__(self, config_matrix):
        super(ConfigWidget, self).__init__()
        loadUi(os.path.join(os.path.abspath(os.path.dirname(__file__)), "ConfigWidget.ui"), self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.config_matrix = config_matrix
        
        self.snLine.setText(config_matrix["Camera"]["DeviceSerialNumber"])
        self.exposeLine.setValidator(QIntValidator(0,1000000))
        self.exposeLine.setText(config_matrix["Camera"]["ExposureTime"])
        self.gainLine.setValidator(QIntValidator(0,1000))
        self.gainLine.setText(config_matrix["Camera"]["Gain"])
        self.binningLine.setValidator(QIntValidator(1,4))
        self.binningLine.setText(config_matrix["Camera"]["Binning"])
        
    @pyqtSlot()    
    def save(self):
        pass
        

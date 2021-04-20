#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 03.18.2021
Updated on 04.17.2021

Author: haoshuai@handaotech.com
'''

import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QLabel


class TextAlertLabel(QLabel):
    def __init__(self, parent=None):
        super(TextAlertLabel, self).__init__(parent)
        self.normal_style = r'font: bold;font-size: 25px;height: 36px;width: 100px; background-color:rgb(207,207,207)'
        self.infer_style = r'font: bold;font-size: 25px;height: 36px;width: 100px; background-color:rgb(20,255,20)'
        self.alert_style = r'font: bold;font-size: 25px;height: 36px;width: 100px; background-color:rgb(255,0,0)'
        self.setAlignment(Qt.AlignCenter)
        
    def setAlert(self, def_info):
        self.setStyleSheet(self.alert_style)
        self.setText(def_info)
        
    def setInfer(self):
        self.setStyleSheet(self.infer_style)
        self.setText('检测中...')
        
    def reset(self):
        self.setStyleSheet(self.normal_style)
        self.setText('')
        

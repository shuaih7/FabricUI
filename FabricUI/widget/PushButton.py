#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 01.17.2021
Updated on 02.07.2021

Author: haoshaui@handaotech.com
'''

import os
import sys
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QPushButton


class PushButton(QPushButton):
    
    def __init__(self, parent=None):
        super(PushButton, self).__init__(parent)
        self.main_style = "font: bold; font-size: 35px;height: 36px;width: 100px; border:2px groove gray; border-radius:15px;padding:2px 4px;background-color:rgb(180,180,180);"
        self.cfg_style = "font: bold; font-size: 20px;height: 30px;width: 80px; border:2px groove gray;border-radius:10px;padding:2px 4px;"
        self.color = "background-color:rgb(180,180,180)"
        self.press_color = "background-color: rgb(140,140,140)"
        
        self.mainBtnList = ["btnLive", "btnConfig"]

    def mousePressEvent(self, event):
        super(PushButton, self).mousePressEvent(event)
        if self.objectName() in self.mainBtnList:
            self.setStyleSheet(self.main_style+self.press_color)
        else:
            self.setStyleSheet(self.cfg_style+self.press_color)
        super(PushButton, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super(PushButton, self).mouseReleaseEvent(event)
        if self.objectName() in self.mainBtnList:
            self.setStyleSheet(self.main_style+self.color)
        else:
            self.setStyleSheet(self.cfg_style+self.color)
        super(PushButton, self).mouseReleaseEvent(event)
        

            
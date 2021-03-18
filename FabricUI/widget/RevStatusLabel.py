#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 03.17.2021
Updated on 03.17.2021

Author: haoshuai@handaotech.com
'''

import os
from PyQt5.QtWidgets import QLabel


class RevStatusLabel(QLabel):
    def __init__(self, parent=None):
        super(RevStatusLabel, self).__init__(parent)
        self.unsteady_style = 'border:2px groove gray; border-radius:15px;padding:1px 4px;background-color:rgb(255,0,0)'
        self.steady_style = 'border:2px groove gray; border-radius:15px;padding:1px 4px;background-color:rgb(0,255,0)'
        
    def setSteady(self, is_steady):
        if is_steady:
            self.setStyleSheet(self.steady_style)
        else:
            self.setStyleSheet(self.unsteady_style)
        

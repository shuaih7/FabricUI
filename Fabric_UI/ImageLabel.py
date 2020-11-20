#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.20.2020
Updated on 11.20.2020

Author: haoshaui@handaotech.com
'''

import os
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QPoint, QRect, QLineF
from PyQt5.QtGui import QPixmap

class ImageLabel(QLabel):
    def __init__(self, parent=None):
        super(ImageLabel, self).__init__(parent)
        
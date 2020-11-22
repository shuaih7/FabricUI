#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.20.2020
Updated on 11.20.2020

Author: haoshaui@handaotech.com
'''

import os
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QPoint, QRect, QLineF, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap

class ImageLabel(QLabel):
    def __init__(self, config_matrix, parent=None):
        super(ImageLabel, self).__init__(parent)
        self.config_matrix = config_matrix
        self.pixmap = None
        
    @pyqtSlot(dict)
    def updateResult(self, resDict):
        image = resDict["image"]
        boxes = resDict["boxes"]
        labels = resDict["labels"]
        scores = resDict["scores"]
        
        print("Received!")
        
        h, w, ch = image.shape
        bytesPerLine = ch*w
        convertToQtFormat = QImage(image.data, w, h, bytesPerLine, QImage.Format_RGB888)
        
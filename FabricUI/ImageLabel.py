#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.20.2020
Updated on 11.20.2020

Author: haoshaui@handaotech.com
'''

import os
from PyQt5.QtWidgets import QLabel, QApplication
from PyQt5.QtCore import Qt, QPoint, QRect, QLineF, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen

from utils import draw_boxes

class ImageLabel(QLabel):
    def __init__(self, parent=None):
        super(ImageLabel, self).__init__(parent)
        self.config_matrix = None
        self.pixmap = None
        self.scale = None
        
    def setConfig(self, config_matrix):
        self.config_matrix = config_matrix
        
    def refresh(self, image, boxes=[], labels=[], scores=[]):
        if self.scale is None: self.getScale(image)
        image = draw_boxes(image, boxes, scale=self.scale)
        
        h, w, ch = image.shape
        bytesPerLine = ch*w
        convertToQtFormat = QImage(image.data, w, h, bytesPerLine, QImage.Format_RGB888)
        self.pixmap = QPixmap.fromImage(convertToQtFormat).scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.update()
        
    def getScale(self, image):
        h, w = image.shape[:2]
        input_h = self.config_matrix["Model"]["input_h"]
        input_w = self.config_matrix["Model"]["input_w"]
        self.scale = (h/input_h, w/input_w)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        
        if self.pixmap is not None: 
            off_x = (self.size().width() - self.pixmap.width()) / 2
            off_y = (self.size().height() - self.pixmap.height()) / 2
            painter.drawPixmap(off_x, off_y, self.pixmap)
        

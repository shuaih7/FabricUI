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
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen

from utils import draw_boxes

class ImageLabel(QLabel):
    def __init__(self, config_matrix, parent=None):
        super(ImageLabel, self).__init__(parent)
        self.config_matrix = config_matrix
        self.pixmap = None
        
    @pyqtSlot(dict)
    def refresh(self, resDict):
        image = resDict["image"]
        boxes = resDict["boxes"]
        labels = resDict["labels"]
        scores = resDict["scores"]
        
        image = draw_boxes(image, boxes)
        h, w, ch = image.shape
        bytesPerLine = ch*w
        convertToQtFormat = QImage(image.data, w, h, bytesPerLine, QImage.Format_RGB888)
        self.pixmap = QPixmap.fromImage(convertToQtFormat).scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        
        if self.pixmap is not None: 
            off_x = (self.size().width() - self.pixmap.width()) / 2
            off_y = (self.size().height() - self.pixmap.height()) / 2
            painter.drawPixmap(off_x, off_y, self.pixmap)
        
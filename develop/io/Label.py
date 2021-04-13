#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 03.31.2020
Updated on 03.31.2020

Author: haoshuai@handaotech.com
'''

import os
import cv2

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QApplication
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen


class Label(QLabel):
    def __init__(self, parent=None):
        super(Label, self).__init__(parent)
        self.pixmap = None
        
    def refresh(self, image):
        h, w, ch = image.shape[:3]
        bytesPerLine = ch*w
        convertToQtFormat = QImage(image.data.tobytes(), w, h, bytesPerLine, QImage.Format_RGB888)
        self.pixmap = QPixmap.fromImage(convertToQtFormat).scaled(self.size(), Qt.KeepAspectRatio, 
            Qt.SmoothTransformation)
        self.update()
        
    def resizeEvent(self, event):
        super(Label, self).resizeEvent(event)
        if self.pixmap is not None:
            self.pixmap = self.pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        
        if self.pixmap is not None: 
            off_x = (self.size().width() - self.pixmap.width()) / 2
            off_y = (self.size().height() - self.pixmap.height()) / 2
            painter.drawPixmap(off_x, off_y, self.pixmap)
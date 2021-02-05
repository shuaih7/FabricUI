#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.20.2020
Updated on 02.05.2021

Author: haoshaui@handaotech.com
'''

import os
import cv2
from PyQt5.QtWidgets import QLabel, QApplication
from PyQt5.QtCore import Qt, QPoint, QRect, QLineF, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen


colors = [(255,0,0), (255,165,0)]
font = cv2.FONT_HERSHEY_SIMPLEX


def draw_results(image, results):
    if results is None: return image
    
    boxes = results['boxes']
    labels = results['labels']
    scores = results['scores']
    if len(boxes) == 0: return image
    
    for box, label, score in zip(boxes, labels, scores):
        xmin, ymin, xmax, ymax = box
        image = cv2.rectangle(image, (xmin,ymin), (xmax,ymax), colors[label], thickness=3)
        #image = cv2.putText(image, str(round(score,3)), (xmin,ymin), fontFace=font, 
        #    fontScale=0.5, color=color[label], thickness=2)
            
    return image


class Canvas(QLabel):
    def __init__(self, parent=None):
        super(Canvas, self).__init__(parent)
        self.config_matrix = None
        self.pixmap = None
        self.scale = None
        
    def setConfig(self, config_matrix):
        self.config_matrix = config_matrix
        
    def refresh(self, image, results=None):
        image = draw_results(image, results)
        
        h, w, ch = image.shape[:3]
        bytesPerLine = ch*w
        convertToQtFormat = QImage(image.data.tobytes(), w, h, bytesPerLine, QImage.Format_RGB888)
        self.pixmap = QPixmap.fromImage(convertToQtFormat).scaled(self.size(), Qt.KeepAspectRatio, 
            Qt.SmoothTransformation)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        
        if self.pixmap is not None: 
            off_x = (self.size().width() - self.pixmap.width()) / 2
            off_y = (self.size().height() - self.pixmap.height()) / 2
            painter.drawPixmap(off_x, off_y, self.pixmap)
        

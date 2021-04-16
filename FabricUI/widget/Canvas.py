#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.20.2020
Updated on 04.15.2021

Author: haoshuai@handaotech.com
'''

import os
import cv2
import copy
from PyQt5.QtWidgets import QLabel, QApplication
from PyQt5.QtCore import Qt, QPoint, QRect, QLineF, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor


colors = [QColor(255,0,0), QColor(255,165,0), QColor(0,0,255)]
font = cv2.FONT_HERSHEY_SIMPLEX


def draw_results(image, results):
    image = format_image(image)
    if results is None or len(results)==0: return image
    
    boxes = results['boxes']
    labels = results['labels']
    scores = results['scores']
    if len(boxes) == 0: return image
    
    for box, label, score in zip(boxes, labels, scores):
        xmin, ymin, xmax, ymax = box
        image = cv2.rectangle(image, (int(xmin), int(ymin)), (int(xmax),int(ymax)), colors[label], thickness=3)
        #image = cv2.putText(image, str(round(score,3)), (xmin,ymin), fontFace=font, 
        #    fontScale=0.5, color=color[label], thickness=2)
            
    return image
    
    
def format_image(image): # Gray to RGB
    if image.shape[-1] == 4: 
        image = image[:,:,:3]
    elif image.shape[-1] != 3: 
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

    return image
    

class Canvas(QLabel):
    def __init__(self, parent=None):
        super(Canvas, self).__init__(parent)
        self.config_matrix = None
        self.pixmap = None
        self.results = None
        
    def setConfig(self, config_matrix):
        self.config_matrix = config_matrix
        
    def refresh(self, image, results=None):
        #image = draw_results(image, results)
        if image is None: return
        else: image = format_image(image)
        self.results = copy.deepcopy(results)
        
        h, w, ch = image.shape[:3]
        bytesPerLine = ch*w
        convertToQtFormat = QImage(image.data.tobytes(), w, h, bytesPerLine, QImage.Format_RGB888)
        self.pixmap = QPixmap.fromImage(convertToQtFormat).scaled(self.size(), Qt.KeepAspectRatio, 
            Qt.SmoothTransformation)
        self.update()
        
    def resizeEvent(self, event):
        super(Canvas, self).resizeEvent(event)
        if self.pixmap is not None:
            self.pixmap = self.pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        
        if self.pixmap is not None: 
            off_x = (self.size().width() - self.pixmap.width()) / 2
            off_y = (self.size().height() - self.pixmap.height()) / 2
            painter.drawPixmap(off_x, off_y, self.pixmap)
            
            if self.results is None: return
            else: results = self.results
            boxes = results['boxes']
            labels = results['labels']
            scale_w = self.pixmap.width() / self.config_matrix['Camera']['resolution_w']
            scale_h = self.pixmap.height() / self.config_matrix['Camera']['resolution_h']
            
            for box, label in zip(boxes, labels):
                xmin, ymin, xmax, ymax = box
                pxmin, pymin = int(xmin*scale_w+off_x), int(ymin*scale_h+off_y)
                draw_w, draw_h = int((xmax-xmin)*scale_w), int((ymax-ymin)*scale_h)
                painter.setPen(QPen(colors[label], 5))
                painter.drawRect(pxmin, pymin, draw_w, draw_h)

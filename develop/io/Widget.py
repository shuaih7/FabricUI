#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 03.31.2020
Updated on 03.31.2020

Author: haoshuai@handaotech.com
'''

import os
import sys
import cv2
import time
import asyncio
import glob as gb

abs_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(abs_path)

from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QApplication

from Worker import SaveWorker


class Widget(QWidget):
    
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)
        loadUi(os.path.join(os.path.abspath(os.path.dirname(__file__)), "Widget.ui"), self)
        self.length = 50
        self.loadImages()
        self.saver_worker = SaveWorker()
        self.saver_worker.start()
        
    def loadImages(self):
        img_path = r'E:\Projects\Fabric_Defect_Detection\model_dev\v1.0.0\dataset\train'
        img_list = gb.glob(img_path + r'/*.bmp')
        
        self.image_list = []
        for img_file in img_list[:self.length]:
            image = cv2.imread(img_file, cv2.IMREAD_COLOR)
            self.image_list.append(image)
    
    @pyqtSlot()
    def start(self):
        start = time.time()
        for image in self.image_list:
            self.label.refresh(image)
            self.saver_worker.save(image)
            time.sleep(0.08)
            QApplication.processEvents()
        end = time.time()
        
        print('The avergaed processing time is', (end-start)/self.length)
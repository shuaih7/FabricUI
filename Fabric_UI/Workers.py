#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.20.2020
Updated on 11.20.2020

Author: haoshaui@handaotech.com
'''

import time, cv2
import functools
import numpy as np
import os, sys, json, time, cv2

from PyQt5.Qt import QMutex
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, pyqtSlot, QTimer


class testInferWorker(QThread):
    resSignal = pyqtSignal(dict)

    def __init__(self, model, img_list, parent=None):
        super(testInferWorker, self).__init__(parent)
        self.img_list = img_list
        self.model = model

    def run(self):
        for img_file in img_list:
            pass
            
            """
            rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgbImage.shape
            bytesPerLine = ch*w
            convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
            self.changePixmap.emit(convertToQtFormat)
            time.sleep(0.05)  # Note: This is the temperory method
            """


    

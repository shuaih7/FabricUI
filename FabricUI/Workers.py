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
import glob as gb
import os, sys, json, time, cv2

from PyQt5.Qt import QMutex
from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, pyqtSlot

from model import inferModel


class testInferWorker(QThread):
    resSignal = pyqtSignal(dict)
    stopSignal = pyqtSignal()

    def __init__(self, config_matrix, logger, parent=None):
        super(testInferWorker, self).__init__(parent)
        valid_dir = config_matrix["valid_dir"]
        valid_suffix = config_matrix["valid_suffix"]
        self.img_list = gb.glob(valid_dir + r"/*"+valid_suffix)
        self.model = inferModel(config_matrix, logger)
        self.isRunning = False

    def run(self):
        img_list = self.img_list
        
        for img_file in img_list:
            if self.isRunning:
                image = cv2.imread(img_file, cv2.IMREAD_COLOR)
                boxes, labels, scores = self.model.infer(image)
                resDict = {
                    "image":  image,
                    "boxes":  boxes,
                    "labels": labels,
                    "scores": scores}
                self.resSignal.emit(resDict)
                QApplication.processEvents()
        self.stopSignal.emit()


    

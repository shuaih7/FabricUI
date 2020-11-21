#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.19.2020
Updated on 11.20.2020

Author: haoshaui@handaotech.com
'''

import os, sys
import json, time
import numpy as np
import glob as gb

abs_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(abs_path)

from model import inferModel
from device import getLogger, getLighting
from Workers import *
from PyQt5.uic import loadUi
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QEvent, QSize
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QFileDialog, QMessageBox


class MainWindow(QMainWindow):
    videoStart = pyqtSignal(bool) # Signal to communicate with the video thread
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        loadUi(os.path.join(os.path.abspath(os.path.dirname(__file__)), "HMI.ui"), self)
        
        # Load the configuration matrix
        config_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), "config.json")
        with open (config_file, "r") as f: 
            self.config_matrix = json.load(f)
        
        # Initialize the crucial parameters
        self.is_run = False
        self.inferThread = None
        self.testInferThread = None
        
        self.logger = getLogger(os.path.join(os.path.abspath(os.path.dirname(__file__)),"log"), log_name="logging")
        self.camera = None #getCamera(self.config_matrix, self.logger)
        self.lighting = getLighting(self.config_matrix, self.logger)
        self.model = inferModel(self.config_matrix, self.logger)
        
        self.logger_flags = {
            "debug":    self.logger.debug,
            "info":     self.logger.info,
            "warning":  self.logger.warning,
            "error":    self.logger.error,
            "critical": self.logger.critical
        }
        
    @pyqtSlot()    
    def runInfer(self):
        if self.camera is None: 
            self.message("相机连接失败，请检查相机设置并重试。", flag="info")
            
        else: 
            message = "相机连接成功，开始检测..."
            # Do inference ...
            
        
    @pyqtSlot()    
    def runTestInfer(self):
        valid_dir = self.config_matrix["valid_dir"]
        valid_suffix = self.config_matrix["valid_suffix"]
        
        self.testInferThread = testInferWorker(self.model, valid_dir, valid_suffix)
        self.testInferThread.resSignal.connect(self.imageLabel.updateResult)
        self.testInferThread.stopSignal.connect(self.stopTestInfer)
        self.message("开始测试检测...\n检测文件夹： " + valid_dir, flag="info")
        #self.testBtn.text("停止检测")
        self.testInferThread.run()
        
        
    @pyqtSlot()
    def stopTestInfer(self):
        if self.testInferThread is not None and self.testInferThread.isRunning():
            self.testInferThread.exit()
        self.message("检测完成", flag="info")
        #self.testBtn.text("开始检测")
        
    def message(self, msg, flag="info"): pass
        #self.logger_flags[flag](msg)
        #self.statusLabel.text(msg)
      
        
        
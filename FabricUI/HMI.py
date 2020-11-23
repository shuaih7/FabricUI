#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.19.2020
Updated on 11.23.2020

Author: haoshaui@handaotech.com
'''

import os, sys, cv2
import json, time
import numpy as np
import glob as gb

abs_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(abs_path)

from device import getLogger, getLighting
from model import cudaModel
from utils import draw_boxes
from PyQt5.uic import loadUi
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QEvent, QSize
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QFileDialog, QMessageBox


class MainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        loadUi(os.path.join(os.path.abspath(os.path.dirname(__file__)), "HMI.ui"), self)
        
        # Load the configuration matrix
        config_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), "config.json")
        with open (config_file, "r") as f: 
            self.config_matrix = json.load(f)
        
        # Config the devices
        self.logger = getLogger(os.path.join(os.path.abspath(os.path.dirname(__file__)),"log"), log_name="logging.log")
        self.camera = None #getCamera(self.config_matrix, self.logger)
        self.lighting = getLighting(self.config_matrix, self.logger)
        self.model = cudaModel(self.config_matrix, self.logger)
        
        # Initialize the crucial parameters
        self.isRunning = False
        self.btn_list = [self.startBtn, self.testBtn, self.configBtn]
        self.label_list = [self.imageLabel, self.statusLabel]
        self.logger_flags = {
            "debug":    self.logger.debug,
            "info":     self.logger.info,
            "warning":  self.logger.warning,
            "error":    self.logger.error,
            "critical": self.logger.critical}
        self.initGUIFormat()
        
    def initGUIFormat(self):
        btnFont = QFont()
        btnFont.setFamily("Arial") #括号里可以设置成自己想要的其它字体
        btnFont.setPointSize(18)   #括号里的数字可以设置成自己想要的字体大小
        
    @pyqtSlot()    
    def runInfer(self):
        if self.camera is None: 
            self.message("相机连接失败，请检查相机设置并重试。", flag="info")
            
        else: 
            message = "相机连接成功，开始检测..."
            # Do inference ...
              
    @pyqtSlot()    
    def runTestInfer(self):
        if self.isRunning:
            self.stopTestInfer()  
        else:
            self.message("开始测试检测...", flag="info")
            self.testBtn.setText("结束测试")
            self.isRunning = True
            
            valid_dir = self.config_matrix["valid_dir"]
            valid_suffix = self.config_matrix["valid_suffix"]
            img_list = gb.glob(valid_dir + "/*"+valid_suffix)
            
            for img_file in img_list:
                if self.isRunning:
                    image = cv2.imread(img_file, cv2.IMREAD_COLOR)
                    boxes, labels, scores = self.model.infer(image)
                    self.imageLabel.refresh(image, boxes, labels, scores)
                    QApplication.processEvents() # Refresh the MainWindow
            self.stopTestInfer()

    def stopTestInfer(self):
        self.isRunning = False
        self.message("测试检测完成！", flag="info")
        self.testBtn.setText("开始测试")
        
    def message(self, msg, flag="info"): 
        self.logger_flags[flag](msg)
        self.statusLabel.setText(msg)
      
        
        

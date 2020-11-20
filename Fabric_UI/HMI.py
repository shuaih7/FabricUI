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

from model import *
from device import *
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
        config_file = os.path.join(os.path.join(os.path.abspath(os.path.dirname(__file__)), "config"), "config.json")
        with open (config_file, "r") as f: 
            self.config_matrix = json.load(f)
        
        self.is_run = False
        
        self.logger = getLogger(os.path.join(os.path.abspath(os.path.dirname(__file__)),"log"), log_name="logging")
        self.camera = getCamera(self.config_matrix, self.logger)
        self.lighting = getLighting(self.config_matrix, self.logger)
        self.model = cudaModel(self.config_matrix, self.logger)
        
    @pyqtSlot()    
    def runInfer(self):
        if self.camera is None: 
            message = "相机连接失败，请检查相机设置并重试。"
            self.logger.info(message)
            self.statusLabel.text(message)
        else: 
            message = "相机连接成功，开始检测..."
            # Do inference ...
            
        
    @pyqtSlot()    
    def runTest(self):
        valid_dir = self.config_matrix["valid_dir"]
        valid_suffix = self.config_matrix["valid_suffix"]
        
        message = "开始测试检测...\n检测文件夹： " + valid_dir
        self.logger.info(message)
        self.statusLabel.text(message)
        
        img_list = gb.glob(valid_dir + r"/*"+valid_suffix)
        for img_file in img_list:
            self.model.infer(img_file, mode="test")
        
        
        
#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.19.2020
Updated on 02.07.2021

Author: haoshaui@handaotech.com
'''

import os
import sys
import cv2
import datetime
import json
import time
import numpy as np
import glob as gb

abs_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(abs_path)

from PyQt5.uic import loadUi
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QEvent, QSize
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QFileDialog, QMessageBox

from log import getLogger
from device import GXCamera as Camera
from model import CudaModel as Model
from monitor import RevMonitor as RevMonitor
from widget import ConfigWidget


class MainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        loadUi(os.path.join(os.path.abspath(os.path.dirname(__file__)), "HMI.ui"), self)
        
        # Load the configuration matrix and make it visible to all sub-widgets
        config_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), "config.json")
        with open (config_file, "r") as f: 
            self.config_matrix = json.load(f)
            f.close()
        
        self.initParams()
        self.initLogger()
        self.initCamera()
        self.initLight()
        self.initModel()
        self.initWidget()
        self.initRevMonitor()
        self.initDatabase()
        self.messager("\nFabricUI 已开启。", flag="info")
        
    def initParams(self):
        self.is_live = False   # Whether images are showing on the label
        self.is_infer = False # Whether the livestream inference is on
        
    def initLogger(self):
        self.logger = getLogger(os.path.join(os.path.abspath(os.path.dirname(__file__)),"log"), 
            log_name="logging.log")
            
        self.logger_flags = {
            "debug":    self.logger.debug,
            "info":     self.logger.info,
            "warning":  self.logger.warning,
            "error":    self.logger.error,
            "critical": self.logger.critical}
        
    def initCamera(self):
        self.messager("初始化相机，正在连接...")
        try:
            camera_params = self.config_matrix["Camera"]
            self.camera = Camera(camera_params)
            self.messager("相机初始化成功。")
        except Exception as expt:
            self.messager(str(expt), flag="error")
            self.camera = None
            
    def initLight(self):
        self.messager("光源初始化成功")
        
    def initModel(self):
        self.messager("正在初始化模型...")
        try:
            model_params = self.config_matrix["Model"]
            self.model = Model(model_params)
            self.messager("模型初始化成功。")
        except Exception as expt:
            self.messager(str(expt), flag="error")
            self.model = None
            
    def initWidget(self):
        self.canvas.setConfig(self.config_matrix)
        
        self.configWidget = ConfigWidget(self.config_matrix)
        self.configWidget.configSignal.connect(self.generalConfig)
        self.configWidget.configSignal.connect(self.cameraConfig)
        self.configWidget.configSignal.connect(self.lightConfig)
        self.configWidget.configSignal.connect(self.modelConfig)
        
    def initRevMonitor(self):
        rev_params = self.config_matrix['RevMonitor']
        self.rev_monitor = RevMonitor(rev_params)
        self.rev_monitor.revSignal.connect(self.revReceiver)
        self.rev_monitor.start()
        
    def initDatabase(self):
        pass
    
    def live(self):
        # Abnormal Case 1 - Already running live view
        if self.is_live: 
            self.shiftInferStatus()
            return
        
        # Abnormal Case 2 - Camera initialized with error
        if self.camera is None:
            self.initCamera()
            if self.camera is not None: self.live()
            return 

        # Normal Case - Start livestream:
        self.is_live = True
        self.is_infer = False
        self.btnLive.setText("开始检测")
        
        while self.is_live: 
            try:
                image = self.camera.getImage()
            except: 
                liveInterruption()
                return

            if self.is_infer:
                image, results = self.model(image)
                self.canvas.refresh(image, results)
            else: 
                self.canvas.refresh(image)
                
            QApplication.processEvents()
            
        # Make sure to stop the steam and close the device before exit
        cam.stream_off()
        cam.close_device()
        
    def shiftInferStatus(self):
        if not self.is_live: 
            return 
        elif self.model is None:
            self.is_infer = False
            self.messager("检测模型异常，请检查相关模型设置", flag="warning")
            return
        
        if self.is_infer:
            self.is_infer = False
            self.btnLive.setText("开始检测")
            self.messager("检测中止")
        else:
            self.is_infer = True
            self.btnLive.setText("停止检测")
            self.messager("检测中...")
            
    def liveInterruption(self):
        self.messager("相机连接中断，请检查链接并重试", flag="error")
        self.is_live = False
        self.is_infer = False
        self.btnLive.setText("连接相机")
        self.camera = None
    
    @pyqtSlot(float)
    def revReceiver(self, rev):
        self.rev = rev
        self.revLabel.setText(str(rev))
    
    @pyqtSlot()
    def systemConfig(self):
        self.configWidget.showConfig()
        
    @pyqtSlot()
    def reset(self):
        pass
        
    @pyqtSlot(str)
    def generalConfig(self, module):
        if module != "General": return
        params = self.config_matrix[module]
        self.messager("已更新常规设置。")
        
    @pyqtSlot(str)
    def cameraConfig(self, module):
        if module != "Camera": return 
        params = self.config_matrix[module]
        self.camera.updateParams(params)
        self.messager("已更新相机设置。")
        
    @pyqtSlot(str)
    def lightConfig(self, module):
        if module != "Light": return
        params = self.config_matrix[module]
        
    @pyqtSlot(str)
    def modelConfig(self, module):
        if module != "Model": return 
        params = self.config_matrix[module]
        
    def messager(self, msg, flag="info"): 
        self.logger_flags[flag.lower()](msg)
        self.statusLabel.setText(msg)
        
    def closeEvent(self, ev):   
        reply = QMessageBox.question(
            self,
            "退出程序",
            "您确定要退出吗?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)

        if reply == QMessageBox.Yes: 
            self.messager("FabricUI 已关闭。\n", flag="info")
            sys.exit()
        else: ev.ignore()
      
        
        

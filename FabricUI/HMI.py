#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.19.2020
Updated on 03.02.2021

Author: haoshuai@handaotech.com
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
from widget import ConfigWidget
from device import GXCamera as Camera
from model import CudaModel as Model
from monitor import RevMonitor as RevMonitor
from pattern import PatternFilter as PatternFilter


class MainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        loadUi(os.path.join(os.path.abspath(os.path.dirname(__file__)), "HMI.ui"), self)
        
        # Load the configuration matrix and make it visible to all sub-widgets
        config_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), "config.json")
        with open (config_file, "r") as f: 
            self.config_matrix = json.load(f)
            f.close()
        
        # Initializations
        self.initParams()
        self.initLogger()
        self.initCamera()
        self.initLight()
        self.initModel()
        self.initWidget()
        self.initRevMonitor()
        self.initPatternFilter()
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
        
    def initPatternFilter(self):
        self.cur_rev_num = 0
        self.init_rev_num = 2
        self.steady_rev_num = 5
        self.rev_offset = 0.5
        self.rev_queue = list()
        self.is_rev_steady = False
        
        self.intv_queue = list()
        self.start_queue = list()
        self.cir_start_time = -1
        
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
        t_start = 0.0
        self.is_live = True
        self.is_infer = False
        self.btnLive.setText("开始检测")
        
        while self.is_live: 
            try:
                t_intv = time.time() - t_start
                t_start = time.time()
                image = self.camera.getImage()
            except: 
                self.liveInterruption()
                break

            if self.is_infer:
                image, results = self.model(image)
                results = self.patternStudy(results, t_intv)
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
            self.initPatternFilter()
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
        
    def patternStudy(self, results, t_intv):
        if not self.is_rev_steady: return 
        
        print("The current time interval is", t_intv)
        
        boxes = results["boxes"]
        labels = results["labels"]
        cir_time = 60 / self.rev
        
        num_def
        for i, label in enumerate(labels):
            if label == 0: num_def += 1
            
        if len(self.start_queue) > 0 and num_def != 3:
            self.cir_start_time = sum(self.start_queue)/len(self.start_queue)
            self.start_queue = list()
            
        elif num_def == 3:
            self.start_queue.append(time.time())
            c_intv = time.time() - self.cir_start_time
            if abs(c_intv-cir_time) <= 1.5*t_intv:
                self.messager("检测到一整圈!!!!!!!!")
                for i, label in enumerate(labels):
                    if label == 0: results["labels"][i] = 2
            
        """
        if self.cir_start_time < 0:
            if len(centers) == 3:
                self.messager("开始计时...")
                self.cir_start_time = time.time()
        else:
            c_intv = time.time() - self.cir_start_time
            if abs(c_intv-cir_time) <= 1.5*t_intv and len(centers) == 3:
                self.messager("检测到一整圈!!!!!!!!")
                for i, label in enumerate(labels):
                    if label == 0: results["labels"][i] += 2
                    
            elif c_intv - cir_time > 1.5*t_intv:
                self.cir_start_time = -1
                self.messager("计时中止")
            else: 
                self.messager("正在计时...")
        """
        return results
    
    @pyqtSlot(float)
    def revReceiver(self, rev):
        self.updateRevStatus(rev)
        self.revLabel.setText(str(rev))
        
    def updateRevStatus(self, rev):
        if not self.is_infer: return
        
        if self.cur_rev_num < self.init_rev_num:
            # self.messager("初始化圈速信息，请稍候...", flag="info")
            self.cur_rev_num += 1
            return 
         
        self.rev = rev
        self.rev_queue.append(rev)
        if len(self.rev_queue) == self.steady_rev_num:
            if max(self.rev_queue)-min(self.rev_queue) <= self.rev_offset:
                self.is_rev_steady = True
                self.rev_queue.pop(0)
                # self.messager("转速已稳定，正在检测...", flag="info")
            else:
                self.initPatternFilter()
                # self.messager("正在等待转速稳定...", flag="info")

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
      
        
        

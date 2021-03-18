#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.19.2020
Updated on 03.18.2021

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
from device import Machine as Machine
from model import CudaModel as Model
from monitor import FPSMonitor, RevMonitor 
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
        self.initCache()
        self.initParams()
        self.initLogger()
        self.initMachine()
        self.initCamera()
        self.initLight()
        self.initModel()
        self.initWidget()
        self.initRevMonitor()
        self.initFPSMonitor()
        self.initPatternFilter()
        self.messager("\nFabricUI 已开启。", flag="info")
        
    def initCache(self):
        self.normal_pixmap = QPixmap(os.path.join(abs_path, 'icon/pass.png'))
        self.alert_pixmap = QPixmap(os.path.join(abs_path, 'icon/warn.png'))
        
    def initParams(self):
        self.rev = -1
        self.status = 'normal' # Init the current inspection status
        self.is_live = False   # Whether images are showing on the label
        self.is_infer = False  # Whether the livestream inference is on
        self.cur_patient_turns = 0
        self.patient_turns = self.config_matrix['General']['patient_turns']
        self.resetDefectMatrix()
        
    def initLogger(self):
        self.logger = getLogger(os.path.join(os.path.abspath(os.path.dirname(__file__)),"log"), 
            log_name="logging.log")
            
        self.logger_flags = {
            "debug":    self.logger.debug,
            "info":     self.logger.info,
            "warning":  self.logger.warning,
            "error":    self.logger.error,
            "critical": self.logger.critical}
            
    def initMachine(self):
        machine_params = self.config_matrix['Machine']
        self.machine = Machine(machine_params)
        self.machine_size_mapdict = machine_params['size_mapdict']
        
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
        
    def initFPSMonitor(self):
        fps_params = self.config_matrix['FPSMonitor']
        self.fps_monitor = FPSMonitor(fps_params)
        
    def initPatternFilter(self):
        pattern_params = self.config_matrix['Pattern']
        
        machine_size = self.config_matrix['Machine']['size']
        machine_type = self.config_matrix['Machine']['type']
        machine_diameter = self.machine_size_mapdict[machine_type][str(machine_size)]
        pattern_params['camera_field'] = self.config_matrix['Camera']['field']
        pattern_params['machine_diameter'] = machine_diameter
        pattern_params['resolution_w'] = self.config_matrix['Camera']['resolution_w']
        pattern_params['resolution_h'] = self.config_matrix['Camera']['resolution_h']
        self.pattern_filter = PatternFilter(pattern_params)
        
    def resetDefectMatrix(self):
        self.defect_matrix = {
            'is_defect': False,
            'details': {
                'defect': False,
                'striation': False
            }
        } 
        
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
        self.setStatus('normal')
        self.btnLive.setText("开始检测")
        
        while self.is_live: 
            try:
                t_intv = self.fps_monitor.countLoop()
                image = self.camera.getImage()
            except: 
                self.liveInterruption()
                break

            if self.is_infer:
                image, results = self.model(image)
                if self.rev_monitor.is_steady:
                    results['rev'] = self.rev
                    results['intv'] = t_intv
                    results = self.pattern_filter(results)
                    self.processResults(results)
                else:
                    self.pattern_filter.reset()
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
            self.pattern_filter.reset()
        else:
            self.is_infer = True
            self.setStatus('normal')
            self.btnLive.setText("停止检测")
            self.messager("检测中...")
            
    def liveInterruption(self):
        self.messager("相机连接中断，请检查链接并重试", flag="error")
        self.is_live = False
        self.is_infer = False
        self.btnLive.setText("连接相机")
        self.camera = None
        
    def processResults(self, results):
        labels = results['labels']
        pattern = results['pattern']
        
        if 'num_tailors' in pattern:
            self.lbTailor.setText(str(pattern['num_tailors']))
        
        if 'is_defect' in pattern:
            self.defect_matrix['details']['defect'] = True
            self.defect_matrix['is_defect'] = True
        if 1 in labels:
            self.defect_matrix['details']['striation'] = True
            self.defect_matrix['is_defect'] = True
        
    def alert(self):
        self.machine.stop() # Stop the weaving machine
        self.setStatus('alert')
        self.is_infer = False
        self.btnLive.setText("开始检测")
        self.pattern_filter.reset()
        
    def setStatus(self, status):
        if status == self.status: return
        elif status == 'alert':
            self.lbStatus.setPixmap(self.alert_pixmap)
            def_info_text = '检测到 '
            
            if self.defect_matrix['details']['defect']:
                def_info_text += '长疵' + ' '
            if self.defect_matrix['details']['striation']:
                def_info_text += '横纹' + ' '
                    
            def_info_text += '缺陷！'
            self.lbTextAlert.setAlert(def_info_text)
            self.messager(def_info_text, flag="error")
            
        elif status == 'normal':
            self.lbStatus.setPixmap(self.normal_pixmap)
            self.lbTextAlert.reset()
        self.status = status
    
    @pyqtSlot(float)
    def revReceiver(self, rev):
        self.rev = rev
        is_rev_steady = self.rev_monitor.is_steady
        self.updateDefectStatus(is_rev_steady)
        self.lbRev.setText(str(rev))
        
        if is_rev_steady:
            self.messager("转速已稳定，检测中...", flag="info")
            self.lbRevStatus.setSteady(True)
        else:
            self.messager("正在等待转速稳定...", flag="info")
            self.lbRevStatus.setSteady(False)
            
    def updateDefectStatus(self, is_rev_steady):
        if not self.defect_matrix['is_defect']: return
        
        elif not is_rev_steady:
            self.resetDefectMatrix()
            self.cur_patient_turns = 0
            
        elif self.cur_patient_turns == self.patient_turns:
            self.cur_patient_turns = 0
            self.resetDefectMatrix()
            self.alert()
            
        else:
            self.cur_patient_turns += 1

    @pyqtSlot()
    def systemConfig(self):
        self.configWidget.showConfig()
        
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
      
        
        

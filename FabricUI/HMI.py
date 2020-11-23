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

from device import getCamera, getLogger, getLighting
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
        self.camera = getCamera(self.config_matrix, self.logger)
        self.lighting = getLighting(self.config_matrix, self.logger)
        self.model = cudaModel(self.config_matrix, self.logger)
        
        # Initialize the crucial parameters
        self.isRunning = False # whether images are showing on the label
        self.isInferring = False
        self.logger_flags = {
            "debug":    self.logger.debug,
            "info":     self.logger.info,
            "warning":  self.logger.warning,
            "error":    self.logger.error,
            "critical": self.logger.critical}

        self.configDevice()
        self.liveStream()
    
    def configDevice(self):
        # Config the camera
        self.camera.ExposureTime.set(ExposureTime)
        self.camera.Gain.set(Gain)
        self.camera.BinningHorizontal.set(Binning)
        self.camera.BinningVertical.set(Binning)

        # set trigger mode and trigger source
        # cam.TriggerMode.set(gx.GxSwitchEntry.OFF)
        self.camera.TriggerMode.set(gx.GxSwitchEntry.ON)
        self.camera.TriggerSource.set(gx.GxTriggerSourceEntry.SOFTWARE)

        # start data acquisition
        self.camera.stream_on()
    
    def liveStream(self):
        if self.camera is None: 
            self.message("相机连接失败，请检查相机设置并重试。", flag="info")
            return

        # Config the camera, this cannot be done in another function or class

        self.isRunning = True

        while self.isRunning:
            self.camera.TriggerSoftware.send_command()

            image_raw = self.camera.data_stream[0].get_image()
            if image_raw is None: continue
            image = image_raw.get_numpy_array()
            if image is None: continue
            # image segment here ...

            if self.isInferring:
                boxes, labels, scores = self.model.infer(image)
                self.imageLabel.refresh(image,boxes,labels,scores)
            else: 
                self.imageLabel.refresh(image)
            QApplication.processEvents()
        self.stopInfer()


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
            self.stopInfer()  
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
            self.stopInfer()

    def stopInfer(self):
        self.isRunning = False
        self.message("测试检测完成！", flag="info")
        self.testBtn.setText("开始测试")
        
    def message(self, msg, flag="info"): 
        self.logger_flags[flag](msg)
        self.statusLabel.setText(msg)
      
        
        

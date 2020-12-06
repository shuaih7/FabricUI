#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.19.2020
Updated on 11.24.2020

Author: haoshaui@handaotech.com
'''

import os, sys, cv2, datetime
import json, time
import numpy as np
import glob as gb

abs_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(abs_path)

from third_party import gxipy as gx
from log import getLogger
from model import cudaModel
from utils import draw_boxes
from ConfigWidget import ConfigWidget

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
        self.imageLabel.setConfig(self.config_matrix)
        
        # Config the devices
        self.logger = getLogger(os.path.join(os.path.abspath(os.path.dirname(__file__)),"log"), log_name="logging.log")
        self.camera = None
        self.lighting = None
        self.model = cudaModel(self.config_matrix, self.logger)
        
        # Define the system configuration widget
        self.configWidget = ConfigWidget(self.config_matrix)
        self.configWidget.generalCfgSignal.connect(self.generalConfig)
        self.configWidget.cameraCfgSignal.connect(self.cameraConfig)
        self.configWidget.lightCfgSignal.connect(self.lightConfig)
        self.configWidget.modelCfgSignal.connect(self.modelConfig)
        
        # Initialize the crucial parameters
        self.isRunning = False   # Whether images are showing on the label
        self.isInferring = False # Whether the livestream inference is on
        self.logger_flags = {
            "debug":    self.logger.debug,
            "info":     self.logger.info,
            "warning":  self.logger.warning,
            "error":    self.logger.error,
            "critical": self.logger.critical}

        self.checkSaveStatus()
        self.message("\nFabricUI 已开启。", flag="info")
    
    def liveStream(self):
        """
        Re-config the camera when the liveStream function is called
        
        Todo: integrate the device from the raw third_party module
        Note:
            1. Make sure to stream on the camera before capturing and stream_off before closing the device
            2. The integration is not done here because the camera object device_manager.update_device_list()
               will lose all of its configurations if returned or passed to another function
        Logics:
            1. 
        """
        # self.startBtn.setText("连接相机")
        camera_config = self.config_matrix["Camera"]
    
        # Fetch the config parameters
        SN = camera_config['DeviceSerialNumber']
        ExposureTime = camera_config['ExposureTime']
        Gain = camera_config['Gain']
        Binning = camera_config['Binning']

        # create a device manager
        device_manager = gx.DeviceManager()
        dev_num, dev_info_list = device_manager.update_device_list()
        
        if dev_num == 0: 
            self.message("未搜寻到相机，请检查相机设置并重试。", flag="warning")
            return
        else:
            self.message("搜寻到相机，连接中...", flag="info")
        
        # open the camera device by serial number
        try:
            cam = device_manager.open_device_by_sn(SN)
            self.camera = cam
            
            # set exposure & gain
            cam.ExposureTime.set(ExposureTime)
            cam.Gain.set(Gain)
            try: # Because some DH cameras do not support "binning"
                cam.BinningHorizontal.set(Binning)
                cam.BinningVertical.set(Binning)
            except: pass

            # set trigger mode and trigger source
            # cam.TriggerMode.set(gx.GxSwitchEntry.OFF)
            cam.TriggerMode.set(gx.GxSwitchEntry.ON)
            cam.TriggerSource.set(gx.GxTriggerSourceEntry.SOFTWARE)
            
            # Set the status to the capturing mode
            cam.stream_on()
            self.message("相机连接成功。", flag="info")
            
            self.isRunning = True
            self.isInterrupt = False
            if self.isInferring: self.startBtn.setText("停止检测") # Maintain the inferring status
            else: self.startBtn.setText("开始检测")
            
        except Exception as expt:
            self.startBtn.setText("连接相机")
            self.message("未连接到相机，请检查相机序列号是否正确并重试。", flag="error")
            return

        while self.isRunning: 
            try:
                self.camera.TriggerSoftware.send_command()
                image_raw = self.camera.data_stream[0].get_image()
                if image_raw is None: continue
                image = image_raw.get_numpy_array()
                if image is None: continue
                else: # Convert gray scale to BGR
                    c = image.shape[-1]
                    if c != 3: image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

            except: 
                self.interruptStop("相机连接中断，请检查链接并重试。", flag="error")
                # Todo: stream_off, close device ...
                return

            if self.isInferring:
                #try:
                image, boxes, labels, scores = self.model.infer(image)
                image, boxes, labels, scores = self.imageLabel.refresh(image,boxes,labels,scores)
                self.save(image, boxes, labels, scores)
                #except Exception as expt:
                #    self.stopInferring("模型无法运行，请检查模型参数并重试。", flag="error")
            else: 
                self.imageLabel.refresh(image)
            QApplication.processEvents()
            
        # Make sure to stop the steam and close the device before exit
        cam.stream_off()
        cam.close_device()

    @pyqtSlot()    
    def startInferring(self):
        """
        Start the video thread and run inspection
        
        Logics:
            Case 1. Camera disconnected (interrupted): Restart the livestrea and maintain the infer status
            Case 2. Camera is running but inspection not running: start inferring
            Case 3. Camera is running and inspection is running: stop inferring
        """
        if not self.isRunning:
            self.liveStream()
        else: 
            if self.isInferring: 
                self.stopInferring("检测中止。", flag="info")
            else: 
                self.isInferring = True
                self.message("开始检测...", flag="info")
                self.startBtn.setText("停止检测")
                
    """         
    @pyqtSlot()    
    def startTestInferring(self):
        if self.isRunning:
            self.stopRunning("正在结束当前检测...\n请再次点击开始测试检测。", flag="info")  
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
            self.stopRunning("测试检测完成。", flag="info")
            self.testBtn.setText("开始测试")
    """
    
    @pyqtSlot()
    def systemConfig(self):
        self.configWidget.show()
        
    @pyqtSlot()
    def reset(self):
        pass
        
    @pyqtSlot(dict)
    def generalConfig(self, cfg_matrix):
        """
        Receive the config_matrix from ConfigWidget, update the config_matrix, and update general configurations
        """
        self.config_matrix = cfg_matrix
        self.checkSaveStatus()
        self.message("已更新常规设置。")
        
    @pyqtSlot(dict)
    def cameraConfig(self, cfg_matrix):
        """
        Receive the config_matrix from ConfigWidget, update the config_matrix, and re-config the camera
        """
        self.config_matrix = cfg_matrix
        self.stopRunning(msg="更新相机配置，正在重启相机...", flag="info")
        self.liveStream()
        
    @pyqtSlot(dict)
    def lightConfig(self, cfg_matrix):
        """
        Receive the config_matrix from ConfigWidget, update the config_matrix, and re-config the light       
        """
        self.config_matrix = cfg_matrix
        
    @pyqtSlot(dict)
    def modelConfig(self, cfg_matrix):
        """
        Receive the config_matrix from ConfigWidget, update the config_matrix, and re-config the model
        """
        self.config_matrix = cfg_matrix
        self.stopInferring(msg="更新相机配置，正在重启模型...", flag="info")
        self.model = cudaModel(self.config_matrix, self.logger)
        self.message("模型配置完成，请点击“开始检测”按钮以开始布匹的检测。")
        
    def stopInferring(self, msg=None, flag="info"):
        self.isInferring = False
        self.startBtn.setText("开始检测")
        if msg is not None: self.message(msg, flag=flag)

    def stopRunning(self, msg=None, flag="info"):
        self.isRunning = False
        self.isInferring = False
        self.startBtn.setText("开始检测")
        if msg is not None: self.message(msg, flag=flag)
        
    def interruptStop(self, msg=None, flag="error"):
        self.isRunning = False
        self.startBtn.setText("连接相机")
        if msg is not None: self.message(msg, flag=flag)
        
    def checkSaveStatus(self):
        if self.config_matrix["save_mode"] not in [0, 1, 2]:
            raise ValueError("Invalid save mode.")
        else: self.save_mode = self.config_matrix["save_mode"]

        if not os.path.exists(self.config_matrix["save_dir"]):
            os.mkdir(self.config_matrix["save_dir"])
        else: self.save_dir = self.config_matrix["save_dir"]
        
    def save(self, image, boxes, labels, scores):
        if self.save_mode == 0: return
        
        save_name = os.path.join(self.save_dir, datetime.datetime.now()+".png")
        
        if self.save_mode == 1: # Save all
            cv2.imwrite(save_name, image)
            
        elif self.save_mode == 2: # Only save the defect image
            if len(boxes) > 0: cv2.imwrite(save_name, image)
        
    def message(self, msg, flag="info"): 
        self.logger_flags[flag](msg)
        self.statusLabel.setText(msg)
        
    def closeEvent(self, ev):   
        reply = QMessageBox.question(
            self,
            "退出程序",
            "您确定要退出吗?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)

        if reply == QMessageBox.Yes: 
            #if self.isInferring: self.isInferring = False
            #if self.isRunning: self.isRunning = False
            self.message("FabricUI 已关闭。\n", flag="info")
            sys.exit()
            #ev.accept()
        else: ev.ignore()
      
        
        

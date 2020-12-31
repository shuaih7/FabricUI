#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on 11.25.2020
Updated on 11.26.2020

Author: haoshuai@handaotech.com
"""

import os, sys, json
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QTabWidget, QFileDialog

abs_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(abs_path)


class ConfigWidget(QTabWidget):
    generalCfgSignal = pyqtSignal(dict)
    cameraCfgSignal = pyqtSignal(dict)
    lightCfgSignal = pyqtSignal(dict)
    modelCfgSignal = pyqtSignal(dict)
    
    def __init__(self, config_matrix):
        super(ConfigWidget, self).__init__()
        loadUi(os.path.join(os.path.abspath(os.path.dirname(__file__)), "ConfigWidget.ui"), self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.config_matrix = config_matrix
        
        # Load the general configurations
        self.save_mode = config_matrix["save_mode"]
        self.setSaveMode(config_matrix["save_mode"])
        self.saveDirLine.setText(config_matrix["save_dir"])
        self.pinLine.setText(str(config_matrix["Pattern"]["input_pin"]))
        self.revNumLine.setText(str(config_matrix["Pattern"]["steady_turns"]))
        self.revOffsetLine.setText(str(config_matrix["Pattern"]["steady_offset"]))
        
        # Load the current camera configurations
        self.snLine.setText(str(config_matrix["Camera"]["DeviceSerialNumber"]))
        #self.exposeLine.setValidator(QIntValidator(0,1000000))
        self.exposeLine.setText(str(config_matrix["Camera"]["ExposureTime"]))
        #self.gainLine.setValidator(QIntValidator(0,1000))
        self.gainLine.setText(str(config_matrix["Camera"]["Gain"]))
        #self.binningLine.setValidator(QIntValidator(1,4))
        self.binningLine.setText(str(config_matrix["Camera"]["Binning"]))
        
        # Load the current lighting configurations
        # ......
        
        # Load the current model configurations
        off_left, off_right, off_top, off_bottom = config_matrix["Model"]["offsets"]
        self.offLeftLine.setText(str(off_left))
        self.offRightLine.setText(str(off_right))
        self.offTopLine.setText(str(off_top))
        self.offBottomLine.setText(str(off_bottom))
        
        self.widthLine.setText(str(config_matrix["Model"]["input_w"]))
        self.heightLine.setText(str(config_matrix["Model"]["input_h"]))
        self.threshLine.setText(str(config_matrix["Model"]["obj_threshold"]))
        self.nmsLine.setText(str(config_matrix["Model"]["nms_threshold"]))
        
    @pyqtSlot()    
    def generalConfig(self):
        self.config_matrix["save_mode"] = self.getSaveMode()
        self.config_matrix["save_dir"] = self.saveDirLine.text()
        self.config_matrix["Pattern"]["input_pin"] = int(self.pinLine.text())
        self.config_matrix["Pattern"]["steady_turns"] = int(self.revNumLine.text())
        self.config_matrix["Pattern"]["steady_offset"] = float(self.revOffsetLine.text())
    
        self.generalCfgSignal.emit(self.config_matrix)
        self.saveConfig()
        
    @pyqtSlot()    
    def cameraConfig(self):
        # Save the camera configurations
        self.config_matrix["Camera"]["DeviceSerialNumber"] = self.snLine.text()
        self.config_matrix["Camera"]["ExposureTime"] = int(self.exposeLine.text())
        self.config_matrix["Camera"]["Gain"] = int(self.gainLine.text())
        self.config_matrix["Camera"]["Binning"] = int(self.binningLine.text())
        
        self.cameraCfgSignal.emit(self.config_matrix)
        self.saveConfig()
    
    @pyqtSlot()    
    def lightConfig(self):    
        # Save the lighting configurations
        # ......
        self.lightCfgSignal.emit(self.config_matrix)
        self.saveConfig()
    
    @pyqtSlot()    
    def modelConfig(self):    
        # Save the model configurations
        off_left = int(self.offLeftLine.text())
        off_right = int(self.offRightLine.text())
        off_top = int(self.offTopLine.text())
        off_bottom = int(self.offBottomLine.text())
        self.config_matrix["Model"]["offsets"] = [off_left, off_right, off_top, off_bottom]
        self.config_matrix["Model"]["input_w"] = int(self.widthLine.text())
        self.config_matrix["Model"]["input_h"] = int(self.heightLine.text())
        self.config_matrix["Model"]["obj_threshold"] = float(self.threshLine.text())
        self.config_matrix["Model"]["nms_threshold"] = float(self.nmsLine.text())
        
        self.modelCfgSignal.emit(self.config_matrix)
        self.saveConfig()
    
    @pyqtSlot()    
    def setSaveDir(self):
        save_dir = QFileDialog.getExistingDirectory()
        self.saveDirLine.setText(save_dir)
        
    def setSaveMode(self, mode=0):
        """
        Set the save mode: 0 for not saving, 1 for saving all, 2 for saving the defect images
        """
        self.save_mode = mode
        
        if mode == 1: 
            self.saveAllBtn.setChecked(True)
            self.saveDefBtn.setChecked(False)
        elif mode == 2: 
            self.saveAllBtn.setChecked(False)
            self.saveDefBtn.setChecked(True)
        else:
            self.saveAllBtn.setChecked(False)
            self.saveDefBtn.setChecked(False)
            
    def getSaveMode(self):
        mode = 0
        if self.saveDefBtn.isChecked(): mode = 2
        elif self.saveAllBtn.isChecked(): mode = 1
        
        return mode
    
    @pyqtSlot()    
    def setSaveAll(self):
        if self.save_mode == 1: self.setSaveMode(0)
        else: self.setSaveMode(1)
    
    @pyqtSlot()
    def setSaveDefect(self):
        if self.save_mode == 2: self.setSaveMode(0)
        else: self.setSaveMode(2)
       
    @pyqtSlot()
    def exitConfig(self):
        self.close()
    
    def saveConfig(self):
        json_file = os.path.join(abs_path, "config.json")
        with open(json_file, "w", encoding="utf-8") as f:
            cfg_obj = json.dumps(self.config_matrix, indent=4)
            f.write(cfg_obj)
            f.close()
            
    
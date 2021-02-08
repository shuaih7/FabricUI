#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on 11.25.2020
Updated on 02.07.2020

Author: haoshuai@handaotech.com
"""

import os, sys, json
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QTabWidget, QFileDialog


abs_path = os.path.abspath(os.path.dirname(__file__))
cfg_path = os.path.abspath(os.path.join(abs_path, ".."))


def dtype_cast(value, dtype):
    if dtype == 'int':
        return int(value)
    elif dtype == 'float':
        return float(value)
    elif dtype == 'str':
        return str(value)
    elif dtype in ['list', 'dict']:
        return eval(value)
    else:
        return value
    

class ConfigWidget(QTabWidget):
    configSignal = pyqtSignal(str)
    
    def __init__(self, config_matrix):
        super(ConfigWidget, self).__init__()
        loadUi(os.path.join(os.path.abspath(os.path.dirname(__file__)), "ConfigWidget.ui"), self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.config_matrix = config_matrix
        
        self.func_dict = {
            'General': {
                'save_mode': [self.getSaveMode, self.setSaveMode, 'str'],
                'save_dir': [self.lnSaveDir.text, self.lnSaveDir.setText, 'str']
            },
            'Camera': {
                'serial_number': [self.lnSN.text, self.lnSN.setText, 'str'],
                'exposure_time': [self.lnExpose.text, self.lnExpose.setText, 'int'],
                'gain': [self.lnGain.text, self.lnGain.setText, 'int'],
                'binning': [self.lnBinning.text, self.lnBinning.setText, 'int']
            },
            'Light': {
            
            },
            'Model': {
                'offsets': [self.getOffsets, self.setOffsets, 'list'],
                'input_h': [self.lnInputHeight.text, self.lnInputHeight.setText, 'int'],
                'input_w': [self.lnInputWidth.text, self.lnInputWidth.setText, 'int'],
                'obj_threshold': [self.lnThresh.text, self.lnThresh.setText, 'float'],
                'nms_threshold': [self.lnNMS.text, self.lnNMS.setText, 'float']
            }
        }
        
    def showConfig(self):
        for module in self.func_dict:
            params = self.config_matrix[module]
            funcs = self.func_dict[module]
            self.loadConfig(params, funcs)
        self.show()
        
    def loadConfig(self, params, funcs):
        for item in funcs:
            value = params[item]
            func_get, func_set, data_type = funcs[item]
            func_set(str(value))
    
    @pyqtSlot()    
    def updateConfig(self):
        for module in self.func_dict:
            params = self.config_matrix[module]
            funcs = self.func_dict[module]
            self.setConfig(params, funcs, module)
        self.exitConfig()
        
    def setConfig(self, params, funcs, module):
        flag = False
        for item in funcs:
            func_get, func_set, data_type = funcs[item]
            pre_value = str(params[item])
            cur_value = str(func_get())
            
            if pre_value != cur_value:
                params[item] = dtype_cast(cur_value, data_type)
                flag = True
        
        if flag: 
            self.writeConfig()
            self.configSignal.emit(module)
        
    @pyqtSlot()
    def exitConfig(self):
        self.close()
        
    def writeConfig(self):
        json_file = os.path.join(cfg_path, "config.json")
        with open(json_file, "w", encoding="utf-8") as f:
            cfg_obj = json.dumps(self.config_matrix, indent=4)
            f.write(cfg_obj)
            f.close()
    
    @pyqtSlot()    
    def setSaveDir(self):
        save_dir = QFileDialog.getExistingDirectory()
        if not os.path.exists(save_dir):
            save_dir = self.config_matrix['General']['save_dir']
        self.lnSaveDir.setText(save_dir)
        
    def setSaveMode(self, mode="1"):
        """Set the save mode: 0 for not saving, 1 for saving all, 2 for saving the defect images
        """
        self.save_mode = mode
        
        if str(mode) == "1": 
            self.btnSaveAll.setChecked(True)
            self.btnSaveDef.setChecked(False)
        elif str(mode) == "2": 
            self.btnSaveAll.setChecked(False)
            self.btnSaveDef.setChecked(True)
        else:
            self.btnSaveAll.setChecked(False)
            self.btnSaveDef.setChecked(False)
            
    def getSaveMode(self):
        mode = "0"
        if self.btnSaveDef.isChecked(): mode = "2"
        elif self.btnSaveAll.isChecked(): mode = "1"
        
        return mode
    
    @pyqtSlot()    
    def setSaveAll(self):
        if str(self.save_mode) == "1": self.setSaveMode("0")
        else: self.setSaveMode("1")
    
    @pyqtSlot()
    def setSaveDefect(self):
        if str(self.save_mode) == "2": self.setSaveMode("0")
        else: self.setSaveMode("2")
        
    def getOffsets(self):
        offLeft = int(self.lnOffLeft.text())
        offRight = int(self.lnOffRight.text())
        offTop = int(self.lnOffTop.text())
        offBottom = int(self.lnOffBottom.text())
        
        return str([offLeft, offRight, offTop, offBottom])
        
    def setOffsets(self, offsets):
        if isinstance(offsets, str):
            offsets = eval(offsets)
        
        offLeft, offRight, offTop, offBottom = offsets
        self.lnOffLeft.setText(str(offLeft))
        self.lnOffRight.setText(str(offRight))
        self.lnOffTop.setText(str(offTop))
        self.lnOffBottom.setText(str(offBottom))
    
            
    
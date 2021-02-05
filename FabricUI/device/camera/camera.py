#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 02.05.2021
Updated on 02.05.2021

Author: haoshaui@handaotech.com
'''


import os
import sys
from abc import ABC, abstractmethod


class CameraNotFoundError(Exception):
    def __init__(self, ErrorInfo):
        super().__init__(self) 
        self.errorinfo = ErrorInfo
    def __str__(self):
        return self.errorinfo


class Camera(ABC):
    def __init__(self, params):
        self.params = params
        
    @abstractmethod
    def connect(self):
        return
    
    @abstractmethod
    def getImage(self):
        return
        
    @abstractmethod
    def updateParams(self, params):
        return
        
        
    





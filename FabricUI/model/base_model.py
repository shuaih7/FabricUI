#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 01.28.2021
Updated on 01.28.2021

Author: haoshaui@handaotech.com
'''

import os
import sys
from abc import ABC, abstractmethod


class BaseModel(ABC):
    def __init__(self, config_matrix, messager):
        self.config_matrix = config_matrix
        self.messager = messager
        
    @abstractmethod
    def preprocess(image):
        return image
    
    @abstractmethod    
    def infer(self, image):
        results = []
        return results
        
    @abstractmethod
    def postprocess(self, image, results):
        boxes = []
        labels = []
        scores = []
        return image, boxes, labels, scores
    
    @abstractmethod    
    def __call__(self, image):
        image = self.preprocess(image)
        results = self.infer(image)
        image, boxes, labels, scores = self.postprocess(image, results)
        
        return image, boxes, labels, scores


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


class Model(ABC):
    def __init__(self, params):
        self.params = params
        
    @abstractmethod
    def preprocess(image):
        return image
    
    @abstractmethod    
    def infer(self, image):
        outputs = []
        return outputs
        
    @abstractmethod
    def postprocess(self, origin, outputs):
        results = {'image': origin}
        return results
    
    @abstractmethod    
    def __call__(self, image):
        image = self.preprocess(image)
        results = self.infer(image)
        image, results = self.postprocess(image, results)
        
        return image, results


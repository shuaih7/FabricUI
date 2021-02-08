#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 02.01.2021
Updated on 02.08.2021

Author: haoshaui@handaotech.com
'''

import os
import sys
import cv2
import numpy as np
from PIL import Image
    
    
def convertRGB(image):
    if image.shape[-1] == 4: 
        image = image[:,:,:3]
    elif image.shape[-1] != 3: 
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    return image

    
class PreprocessYOLO(object):
    def __init__(self, params):
        self.updateParams(params)
    
    def updateParams(self, params):
        self.input_h = params['input_h']
        self.input_w = params['input_w']
        self.offsets = params['offsets']

    def __call__(self, image): 
        image = self.load_image(image)
        image = self.crop_image(image)
        origin, image = self.resize_image(image)
        image = self.normalize_image(image)
        return origin, image
        
    def load_image(self, image):
        if isinstance(image, str):
            image = cv2.imread(image, cv2.IMREAD_COLOR)
            if image is None: raise ValueError("Input image should be numpy array, not None.")
        
        return convertRGB(image)
        
    def crop_image(self, image):
        off_left, off_right, off_top, off_bottom = self.offsets
        h, w = image.shape[:2]
        return image[off_top:h-off_bottom, off_left:w-off_right]

    def resize_image(self, image):
        resolution = (self.input_w, self.input_w)
            
        image_resized = Image.fromarray(image)
        image_resized = image_resized.resize(resolution, resample=Image.BILINEAR)
        image_resized = np.array(image_resized, dtype=np.float32)
        
        return image, image_resized

    def normalize_image(self, image):
        image -= 127.5
        image *= 0.007843
        # HWC to CHW format:
        image = np.transpose(image, [2, 0, 1])
        # CHW to NCHW format:
        image = np.expand_dims(image, axis=0)
        # Convert the image to row-major order, also known as "C order":
        image = np.array(image, dtype=np.float32, order='C')
        return image


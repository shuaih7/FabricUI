#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 02.01.2021
Updated on 02.01.2021

Author: haoshaui@handaotech.com
'''

import os
import sys
import cv2
import numpy as np


def map_boxes(boxes, input_shape, image_shape):
    h, w = input_shape
    img_h, img_w = image_shape
    ratio_h, ratio_w = img_h/h, img_w/w
    
    map_boxes = []
    for box in boxes:
        xmin, ymin, xmax, ymax = int(box[0]*ratio_w), int(box[1]*ratio_h), \
            int(box[2]*ratio_w), int(box[3]*ratio_h)
        map_boxes.append([xmin, ymin, xmax, ymax])
        
    return map_boxes


def crop_image(img, offsets):
    off_left, off_right, off_top, off_bottom = offsets
    h, w = img.shape[:2]
    return img[off_top:h-off_bottom, off_left:w-off_right]


def resize_image(img, target_size):
    h, w = target_size
    img = cv2.resize(img, (w, h), interpolation = cv2.INTER_LINEAR)

    return img


def normalize_image(img, input_size): # image is an numpy array
    """ Normalize the input image 
    
    Args:
        img: Input image as the format of numpy array
        input_size: Target input shape for model input of (h, w)
        
    Returns:
        img: Normalized img ready for inference
    """
    if img.shape[-1] == 4: 
        img = img[:,:,:3]
    elif img.shape[-1] != 3: 
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    
    origin = img.copy()
    img = resize_image(img, input_size)
    img = np.array(img).astype('float32').transpose((2, 0, 1))  # HWC to CHW
    img -= 127.5
    img *= 0.007843
    img = img[np.newaxis, :]
    return origin, img


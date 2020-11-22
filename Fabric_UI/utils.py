#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.20.2020
Updated on 11.20.2020

Author: haoshaui@handaotech.com
'''

import os
import cv2

def draw_boxes(image, boxes, color=(255,0,0), thickness=2):
    if len(boxes) == 0: return image
    for box in boxes:
        start_point = (box[0], box[1])
        end_point = (box[2], box[3])
        image = cv2.rectangle(image, start_point, end_point, color=color, thickness=thickness)
    return image
#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.20.2020
Updated on 11.24.2020

Author: haoshaui@handaotech.com
'''

import os
import cv2
import sys
import numpy as np


abs_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(abs_path)


def draw_boxes(image, boxes=[], color=(255,0,0), thickness=2):
    if len(boxes) == 0: return image
    for box in boxes:
        start_point = (int(box[0]), int(box[1]))
        end_point = (int(box[2]), int(box[3]))
        image = cv2.rectangle(image, start_point, end_point, color=color, thickness=thickness)
    return image
    
def create_background(size, seed=0):
    image = np.ones(size, dtype=np.uint8) * seed
    save_dir = os.path.join(abs_path, "icon")
    save_name = os.path.join(save_dir, "background.jpg")
    

if __name__ == "__main__":
    create_background((352,352))

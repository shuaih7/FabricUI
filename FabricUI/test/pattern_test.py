#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 03.02.2021
Updated on 03.02.2021

Author: haoshuai@handaotech.com
'''

import os
import sys
import cv2
import numpy as np
import glob as gb

file_path = os.path.abspath(os.path.dirname(__file__))
abs_path = os.path.abspath(os.path.join(file_path, ".."))
sys.path.append(abs_path)

from pattern.pattern_recorder import PatternRecorder


if __name__ == "__main__":
    data_folder = r"F:\TGData\20210223-horizantal-gain8"
    img_list = gb.glob(data_folder + r"/*.bmp")
    
    for img_file in img_list:
        image = cv2.imread(img_file, -1)
        cv2.imshow("image", image)
        cv2.waitKey(50)
#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.20.2020
Updated on 11.25.2020

Author: haoshaui@handaotech.com
'''

import os
import cv2
import sys
import numpy as np


abs_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(abs_path)


def draw_boxes(image, boxes=[], scale=(1.0,1.0), color=(255,0,0), thickness=2):
    if len(boxes) == 0: return image
    for box in boxes:
        start_point = (int(box[0]*scale[1]), int(box[1]*scale[0]))
        end_point = (int(box[2]*scale[1]), int(box[3]*scale[0]))
        image = cv2.rectangle(image, start_point, end_point, color=color, thickness=thickness)
    return image
    
def create_background(size, seed=0):
    image = np.ones(size, dtype=np.uint8) * seed
    save_dir = os.path.join(abs_path, "icon")
    save_name = os.path.join(save_dir, "background.jpg")
    cv2.imwrite(save_name, image)
    
def transparent_background(img_file, save_name, thresh=10):
    image = cv2.imread(img_file, cv2.IMREAD_COLOR)
    image_gray = cv2.imread(img_file, cv2.IMREAD_GRAYSCALE)
    
    trans_image = np.zeros((image.shape[0],image.shape[1],4), dtype=np.uint8)
    alpha = np.ones(image_gray.shape, dtype=np.uint8) * 255
    
    alpha[image_gray>(255-thresh)] = 0
    trans_image[:,:,:3] = image
    trans_image[:,:,-1] = alpha
    
    cv2.imwrite(save_name, trans_image)
    
    print("Done")
    

def resize_image(img_file, save_name, size=(100,100)):
    image = cv2.imread(img_file, -1)
    image = cv2.resize(image, size, interpolation=cv2.INTER_CUBIC)
    cv2.imwrite(save_name, image)
    
    print("Done")

if __name__ == "__main__":
    #create_background((352,352))
    img_file = r"C:\Users\shuai\Documents\GitHub\FabricUI\FabricUI\icon\folder.jpg"
    save_name = r"C:\Users\shuai\Documents\GitHub\FabricUI\FabricUI\icon\folder_icon.png"
    #resize_image(img_file, save_name)
    transparent_background(img_file, save_name)

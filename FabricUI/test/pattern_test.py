#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 03.09.2021
Updated on 03.10.2021

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

from PascalVocParser import PascalVocXmlParser
from pattern.pattern_filter import PatternFilter
from pattern.pattern_recorder import PatternRecorder


def drawBoxes(img, boxes, color=220, thickness=2):
    for box in boxes:
        img = cv2.rectangle(img, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), color=color, thickness=thickness)
    return img


def getTimeInfo(img_file):
    _, filename = os.path.split(img_file)
    sec = filename[46:48]
    msec = filename[49:52]
    
    if sec[0] == "0": sec = sec[1]
    if msec[0] == "0": msec = msec[1:]
    if msec[0] == "0": msec = msec[1]
    
    return float(sec), float(msec)
    
    
def getTimeInterval(pre_img_file, img_file) -> float:
    cur_sec, cur_msec = getTimeInfo(img_file)
    pre_sec, pre_msec = getTimeInfo(pre_img_file)
    
    if cur_sec < pre_sec: 
        intv_sec = 60.0 + cur_sec - pre_sec
    else: 
        intv_sec = cur_sec - pre_sec
        
    intv_msec = cur_msec - pre_msec
    intv = (intv_sec * 1000.0 + intv_msec) / 1000.0
    
    # print("The current time interval is", intv, "second(s).")
    
    return intv


class PatternTest(object):
    def __init__(self, params):
        self.pvoc_parser = PascalVocXmlParser()
        self.recorder = PatternRecorder(params)
        self.filter = PatternFilter(params)
        self.updateParams(params)
    
    def updateParams(self, params):
        self.recorder.updateParams(params)
        self.filter.updateParams(params)
        self.params = params
        
    def loadLabels(self, xml_file):
        labels = list()
        scores = list()
        boxes = self.pvoc_parser.get_boxes(xml_file)
        
        for box in boxes:
            labels.append(0)
            scores.append(0.99)
        
        return boxes, labels, scores
        
    def getResults(self, img_file, intv):
        results = {
            'boxes': [],
            'labels': [],
            'scores': [],
            'rev': self.params['rev'],
            'intv': intv
        }
        
        fileinfo, _ = os.path.splitext(img_file)
        xml_file = fileinfo + '.xml'
        if os.path.isfile(xml_file):
            boxes, labels, scores = self.loadLabels(xml_file)
            results['boxes'] = boxes
            results['labels'] = labels
            results['scores'] = scores
            
        return results
        
    def __call__(self):
        data_folder = self.params['data_folder']
        img_list = sorted(gb.glob(data_folder + r"/*.bmp"), key=os.path.getmtime)
        
        for i in range(1, len(img_list), 1):
            pre_file, img_file = img_list[i-1], img_list[i]
            intv = getTimeInterval(pre_file, img_file)
            
            image = cv2.imread(img_file, -1)
            results = self.getResults(img_file, intv)
            results = self.recorder(results)
            #results = self.filter(results)
            
            if 'num_tailors' in results['pattern']:
                print("The number of tailors is", results['pattern']['num_tailors'])
            else:
                print("Waiting for recording ...")
            
            cv2.imshow("image", drawBoxes(image, results['boxes']))
            cv2.waitKey(80)
        

if __name__ == "__main__":
    params = {
        'rev': 19.,
        'blank_fields': 1.2,
        'resolution_w': 720,
        'resolution_h': 540,
        'machine_diameter': 70,
        'camera_field': 14,
        'data_folder': r"F:\TGData\20210223-horizantal-gain8"
    }

    pattern_test = PatternTest(params)
    pattern_test()
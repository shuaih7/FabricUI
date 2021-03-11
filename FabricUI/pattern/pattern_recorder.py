#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 03.09.2021
Updated on 03.11.2021

Author: haoshuai@handaotech.com
'''


import os
import sys
import cv2
import time
import copy
import numpy as np


def preprocessResults(results, index=0):
    boxes = results['boxes']
    labels = results['labels']
    
    boxes_info = list()
    boxes_index = list()
    width, height, num = 0, 0, 0
    for i, box in enumerate(boxes):
        label = labels[i]
        if label == index: # Filter out other defects
            center_x = (box[0] + box[2]) / 2
            # center_y = (box[1] + box[3]) / 2
            width += box[2] - box[0]
            height += box[3] - box[1]
            num += 1
            
            boxes_info.append(center_x)
            boxes_index.append(i)
    
    pattern = {
        'x': boxes_info,
        'width': width / max(num, 1),
        'indices': boxes_index
    }
    results['pattern'] = pattern
    
    return results


class PatternRecorder(object):
    def __init__(self, params):
        self.updateParams(params)
        
    def updateParams(self, params):
        self.machine_perimeter = np.pi * params['machine_diameter']
        self.camera_field = params['camera_field']
        self.resolution_w = params['resolution_w']
        self.dist_to_pixel = params['resolution_w'] / params['camera_field'] # pix / cm
        self.params = params
        self.reset()
        
    def reset(self):
        self.is_record = False
        self.is_start = False
        self.start_intv_cache = 0
        self.blank_fields = self.params['blank_fields']
        
        self.num_tailors = 0
        self.res_queue = list()
        
        self.acc_time = 0
        self.def_intv = 0
        self.intv_queue = list()
        self.is_def_appear = False
        
    def recordStartTime(self, results):
        rev = results['rev']
        speed = rev * self.machine_perimeter / 60.0 # cm / s
        field_time = self.camera_field / speed # Time to run through a camera field
        blank_time = self.blank_fields * field_time
        
        if len(results['pattern']['x']) == 0 and not self.is_start:
            if self.start_intv_cache >= blank_time:
                self.start_intv_cache += results['intv']
                self.acc_time += self.start_intv_cache / 2
                self.is_start = True
                
            if self.start_intv_cache > 0: 
                self.start_intv_cache += results['intv']
            else:
                self.start_intv_cache += results['intv']/20
        else:
            self.start_intv_cache = 0
            
    def recordTailor(self, results):
        self.acc_time += results['intv']
        self.intv_queue.append(results['intv'])
        
        if len(results['pattern']['x']) > 0:
            if self.is_def_appear:
                self.def_intv += results['intv']
                
            results['def_intv'] = self.def_intv
            self.res_queue.append(results)
            self.is_def_appear = True
            self.def_intv = 0
        else:
            self.parseResQueue()
            if self.is_def_appear:
                self.def_intv += results['intv']
        
        self.checkRecordStatus(results)
        
    def parseResQueue(self):
        if not len(self.res_queue): return 
        
        overlap = 0
        pre_results = self.res_queue[0]
        total = len(pre_results['pattern']['x'])
        
        for i in range(1, len(self.res_queue), 1):
            results = self.res_queue[i]
            overlap += self.getResOverlaps(pre_results, results)
            total += len(results['pattern']['x'])
            pre_results = self.res_queue[i]
            
        self.num_tailors = total - overlap
        self.res_queue.clear()
        
    def getResOverlaps(self, pre_results, results):
        rev = results['rev']
        pattern_width = pre_results['pattern']['width']
        speed = rev * self.machine_perimeter / 60.0 # cm / s
        pix_offset = (speed * results['def_intv']) * self.dist_to_pixel
        
        pix_pos = list()
        pattern_width = 0
        for x in pre_results['pattern']['x']:
            pix_pos.append(x - pix_offset)
            pattern_width += pre_results['pattern']['width']
        pattern_width /= max(1, len(pre_results['pattern']['x']))
            
        overlap = 0
        pre_pos, cur_pos = np.meshgrid(pix_pos, results['pattern']['x'])
        dist_matrix = abs(pre_pos - cur_pos)
        
        for i in range(dist_matrix.shape[0]):
            dist_slice = dist_matrix[i,:]
            if len(dist_slice[dist_slice < pattern_width*1.0]) >= 1:
                overlap += 1
        
        return overlap
        
    def checkRecordStatus(self, results):
        rev = results['rev']
        intv = sum(self.intv_queue) / len(self.intv_queue)
        cir_intv = 60 / rev
        
        if abs(self.acc_time - cir_intv) < 1.5*intv:
            self.is_record = True
        
    def __call__(self, results):
        results = preprocessResults(results) 
        
        if not self.is_start:
            self.recordStartTime(results)
        elif not self.is_record:
            self.recordTailor(results)
        else:
            #results['pattern']['start_time'] = self.pattern_start_time
            results['pattern']['num_tailors'] = self.num_tailors
        
        return results
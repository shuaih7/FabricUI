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


class PatternFilter(object):
    def __init__(self, params):
        self.updateParams(params)
        
    def updateParams(self, params):
        self.machine_perimeter = np.pi * params['machine_diameter']
        self.camera_field = params['camera_field']
        self.resolution_w = params['resolution_w']
        self.dist_to_pixel = params['resolution_w'] / params['camera_field'] # pix / cm
        self.blank_fields = params['blank_fields']
        self.params = params
        self.reset()
        
    def reset(self):
        self.def_intv = 0
        self.avg_intv = 0
        self.num_tailors = 0
        self.cur_num_tailors = 0
        self.res_queue = list()
        self.is_record = False
        self.is_def_appear = False
        self.resetStartTimer()
        
    def resetStartTimer(self):
        self.is_start = False
        self.acc_time = 0
        self.start_intv_cache = 0
        
    def recordStartTime(self, results):
        rev = results['rev']
        speed = rev * self.machine_perimeter / 60.0 # cm / s
        field_time = self.camera_field / speed # Time to run through a camera field
        blank_time = self.blank_fields * field_time
        
        if len(results['pattern']['x']) == 0:
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
        self.updateAvgIntv(results['intv'])
        
        if len(results['pattern']['x']) > 0:
            if self.is_def_appear:
                self.def_intv += results['intv']
            
            results['def_intv'] = self.def_intv
            self.res_queue.append(results)
            self.is_def_appear = True
            self.def_intv = 0
        else:
            if self.is_def_appear: 
                self.def_intv += results['intv']
                if not self.mightHaveTailor() and len(self.res_queue) > 0: 
                    self.parseResQueue() # Update the current number of tailors
                    
                    if not self.is_record: self.num_tailors = self.cur_num_tailors
                    self.res_queue.clear()
        
        self.checkResults(results)
        
    def mightHaveTailor(self):
        if not len(self.res_queue): return
        
        last_results = self.res_queue[-1]
        center = max(last_results['pattern']['x']) # Left right turn consider
        speed = last_results['rev'] * self.machine_perimeter / 60.0 # cm / s
        cur_pos = center - speed * self.def_intv * self.dist_to_pixel # Left right turn consider
        
        if cur_pos >= 0: return True
        else: return False
        
    def parseResQueue(self):
        overlap = 0
        pre_results = self.res_queue[0]
        total = len(pre_results['pattern']['x'])
        
        for i in range(1, len(self.res_queue), 1):
            results = self.res_queue[i]
            overlap += self.getResOverlaps(pre_results, results)
            total += len(results['pattern']['x'])
            pre_results = self.res_queue[i]
            
        self.cur_num_tailors += total - overlap 
        # self.cur_num_tailors = max(self.cur_num_tailors, total - overlap)
        
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
        
    def checkResults(self, results):
        if not self.isFullCycle(results): return
        if not self.is_record: self.is_record = True
        
        pattern = {
            'num_tailors': self.num_tailors,
            'det_tailors': self.cur_num_tailors
        }
        if self.num_tailors < self.cur_num_tailors:
            pattern['defect_info'] = "检测到长疵缺陷！"
            
        results['pattern'] = pattern
        self.cur_num_tailors = 0
        self.resetStartTimer()
        
    def updateAvgIntv(self, intv):
        if self.avg_intv == 0: 
            self.avg_intv = intv
        else:
            self.avg_intv = 0.1 * self.avg_intv + 0.9 * intv
        
    def isFullCycle(self, results):
        rev = results['rev']
        cir_intv = 60 / rev
        
        if abs(self.acc_time - cir_intv) < 1.5*self.avg_intv:
            return True
        else:
            return False
        
    def __call__(self, results):
        results = preprocessResults(results) 
        
        if not self.is_start: 
            self.recordStartTime(results)
        else: 
            self.recordTailor(results)
        
        return results
#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 03.09.2021
Updated on 03.09.2021

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
    width, height, num = 0, 0, 0
    for box, label in zip(boxes, labels):
        if label == index: # Filter out other defects
            center_x = (box[0] + box[2]) / 2
            # center_y = (box[1] + box[3]) / 2
            width += box[2] - box[0]
            height += box[3] - box[1]
            num += 1
            boxes_info.append(center_x)
    
    results['pattern_x'] = boxes_info
    results['pattern_width'] = width / max(num, 1)
    results['pattern_height'] = height / max(num, 1)
    
    return results


class PatternRecorder(object):
    def __init__(self, params):
        self.updateParams(params)
        
    def updateParams(self, params):
        self.time_queue_length = max(3, params['blank_frames'])
        self.machine_perimeter = np.pi * params['machine_diameter']
        self.resolution_w = params['resolution_w']
        self.dist_to_pixel = params['resolution_w'] / params['camera_field'] # pix / cm
        self.params = params
        self.reset()
        
    def reset(self):
        self.is_record = False
        self.start_time = None
        
        self.num_tailors = 0
        self.tailor_groups = 0
        self.tailor_dists = list()
        self.time_queue = list()
        self.res_queue = list()
        
    def recordStartTime(self, results):
        if len(results['pattern_x']) == 0:
            self.time_queue.append(time.time())
            
            if len(self.time_queue) == self.time_queue_length:
                self.start_time = self.time_queue[self.time_queue_length//2]
        else:
            self.time_queue.clear()
            
    def recordTailor(self, results):
        if len(results['pattern_x'] > 0):
            self.res_queue.append(results)
        else:
            self.parseResQueue()
            self.res_queue = list()
            
        self.checkCompleteStatus(results)
        
    def parseResQueue(self):
        overlap = 0
        pre_results = self.res_queue[0]
        total = len(pre_results['pattern_x'])
        
        for i in range(1, len(self.res_queue), 1):
            results = self.res_queue[i]
            overlap += self.getOverlapResults(pre_results, results)
            total += len(results['pattern_x'])
            pre_results = self.res_queue[i]
            
        self.num_tailors = total - overlap
        self.tailor_groups += 1
        
    def getOverlapResults(self, pre_results, results):
        rev = results['rev']
        intv = results['intv']
        pattern_width = pre_results['pattern_width']
        speed = rev * self.machine_perimeter / 60.0 # cm / s
        pix_offset = (speed * intv) * self.dist_to_pixel
        
        pix_pos = list()
        for i, x in pre_results['pattern_x']:
            pix_pos.append(x - pix_offset)
            
        overlap = 0
        pre_pos, cur_pos = np.meshgrid(pix_pos, results['pattern_x'])
        dist_matrix = abs(pre_pos - cur_pos)
        
        for i in range(dist_matrix.shape[0]):
            dist_slice = dist_matrix[i,:]
            if len(dist_slice[dist_slice < pattern_height*1.0]) >= 1:
                overlap += 1
        
        return overlap
        
    def checkCompleteStatus(self, results):
        rev = results['rev']
        intv = results['intv']
        
        cir_intv = 60 / rev
        cur_intv = time.time() - self.start_time
        if abs(cir_time - self.start_time) < 1.5*intv:
            self.is_record = True
        
    def __call__(self, results):
        if self.is_record:
            return results
        elif not self.start_time:
            self.recordStartTime(preprocessResults(results))
        else:
            self.recordTailor(preprocessResults(results))
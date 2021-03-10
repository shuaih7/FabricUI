#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 03.02.2021
Updated on 03.10.2021

Author: haoshuai@handaotech.com
'''

import os
import sys
import cv2
import time
import copy
import numpy as np
from .pattern_recorder import PatternRecorder


class PatternFilter(object):
    def __init__(self, params):
        self.recorder = PatternRecorder(params)
        self.updateParams(params)
        
    def updateParams(self, params):
        self.recorder.updateParams(params)
        self.machine_perimeter = np.pi * params['machine_diameter']
        self.resolution_w = params['resolution_w']
        self.camera_field = params['camera_field']
        self.dist_to_pixel = params['resolution_w'] / params['camera_field'] # pix / cm
        self.params = params
        self.reset()
        
    def reset(self):
        self.pattern_start_time = None
        self.pattern_time_queue = list()
        self.res_queue = list()
        self.num_tailors = 0
        self.is_register = False
        self.recorder.reset()
        
    def register(self, results):
        if self.is_register: return
        self.pattern_start_time = results['pattern']['pattern_start_time']
        self.num_tailors = results['pattern']['num_tailors']
        
        rev = results['rev']
        speed = rev * self.machine_perimeter / 60.0 # cm / s
        self.field_time = self.camera_field / speed # Time to run through a camera field
        self.cir_intv = 60 / rev
        self.is_register = True
        
    def isFullCircle(self):
        if abs(time.time() - self.cir_intv) < 1.2*self.field_time:
            return True
        else:
            return False
            
    def arangeResults(self, results):
        #indices = results['pattern']['indices']
        #for index in indices:
        #    results['labels'][index] += 2
        results.pop('pattern')
        
        return results
        
    def isTailorDefects(self):
        if not len(self.res_queue): return False
        
        overlap = 0
        pre_results = self.res_queue[0]
        pre_time = self.pattern_time_queue[0]
        total = len(pre_results['pattern']['x'])
        
        for i in range(1, len(self.res_queue), 1):
            results = self.res_queue[i]
            cur_time = self.pattern_time_queue[i]
            overlap += self.recorder.getResOverlaps(pre_results, results, pre_time, cur_time)
            total += len(results['pattern']['x'])
            pre_results = self.res_queue[i]
            
            if total - overlap > self.num_tailors:
                return True
                
        return False
        
    def updateStartTime(self):
        if self.pattern_start_time is None or len(self.pattern_time_queue)==0: 
            return 
            
        self.pattern_start_time = sum(self.pattern_time_queue) / len(self.pattern_time_queue)
        self.pattern_time_queue.clear()
        
    def filterResults(self, results):
        pattern = results['pattern']
        is_circle = self.isFullCircle()
        
        if len(pattern['x']) > 0:
            if is_circle:
                self.res_queue.append(results)
                self.pattern_time_queue.append(time.time())
            else:
                results['is_defect'] = True
        else:
            if self.isTailorDefects():
                results['is_defect'] = True
            self.res_queue.clear()
            self.updateStartTime()
        
        results = self.arangeResults(results)
        
        return results
        
    def __call__(self, results):
        results = self.recorder(results)
        if 'num_tailors' not in results['pattern']:
            return results
        elif not self.is_register:
            self.register(results)
            return results
            
        results = self.filterResults(results)
        
        return results
        
            
    
#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 03.09.2021
Updated on 03.18.2021

Author: haoshuai@handaotech.com
'''


import os
import numpy as np
from .pattern_utils import preprocessResults


class PatternFilter(object):
    """ Pattern postprocess class to filter out the tailors in the detection results.
    This class is the full version filter, which could count the number of long defects 
    in the first cycle, select the defect cluster with most defects and count the numebr 
    as the number of tailors, then compare the tailor amount with the amount of long defects 
    in the following cycles. Defect information will be added in the detection results 
    if the number of long defects larger than the tailor amount.
    
    Attributes:
        params: Configuration matrix
        
    Raises:
    
    """
    def __init__(self, params):
        self.updateParams(params)
        
    def updateParams(self, params):
        self.machine_perimeter = np.pi * params['machine_diameter']  # Perimeter of the weaving machine
        self.camera_field = params['camera_field']  # Camera visual field in cm
        self.resolution_w = params['resolution_w']  # Horizontal camera resolution
        self.dist_to_pixel = params['resolution_w'] / params['camera_field'] # pix / cm
        self.blank_fields = params['blank_fields']  # Blank fields for the filter to start a new cycle
        self.params = params
        self.reset()
        
    def reset(self):
        self.avg_intv = 0          # Exponentially averaged time interval between two consecutive frames
        self.avg_width = 0         # Exponentially averaged defect width
        self.num_tailors = 0       # Number of tailors (long defects) of the first cycle
        self.cur_num_tailors = 0   # Number of tailors (long defects) of the current cycle
        self.res_queue = list()    # Result queue containing the results with defects within one cycle
        self.is_record = False     # Status for whether the number of tailors is recorded
        self.resetStartTimer()
        
    def resetStartTimer(self):
        self.is_start = False      # Status for whether a new cycle is started
        self.acc_time = 0          # Accumulated time from the start time
        self.start_intv_cache = 0  # Cached time interval for the blank frames
        self.def_intv = 0          # Time interval from the latest frame with defect
        self.is_def_appear = False # Status for whether the defect has appeared in one cycle
        
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
            
        if self.is_record: self.cur_num_tailors += total - overlap 
        else: self.cur_num_tailors = max(self.cur_num_tailors, total - overlap)
        
    def getResOverlaps(self, pre_results, results):
        rev = results['rev']
        pre_widths = pre_results['pattern']['width']
        cur_widths = results['pattern']['width']
        speed = rev * self.machine_perimeter / 60.0 # cm / s
        pix_offset = (speed * results['def_intv']) * self.dist_to_pixel
        
        pix_pos = list()
        for x in pre_results['pattern']['x']:
            pix_pos.append(x - pix_offset)
        pattern_width = (sum(pre_widths) + sum(cur_widths)) / (len(pre_widths) + len(cur_widths))
            
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
        
        pattern = results['pattern']
        pattern['num_tailors'] = self.num_tailors
        pattern['det_tailors'] = self.cur_num_tailors

        if self.num_tailors < self.cur_num_tailors and self.is_record:
            pattern['is_defect'] = True
        elif not self.is_record: 
            self.is_record = True
        
        self.cur_num_tailors = 0
        self.resetStartTimer()
        
    def updateAvgIntv(self, intv):
        if self.avg_intv == 0: 
            self.avg_intv = intv
        else:
            self.avg_intv = 0.9 * self.avg_intv + 0.1 * intv
            
    def updateAvgWidth(self, width):
        if self.avg_width == 0: 
            self.avg_width = width
        else:
            self.avg_width = 0.9 * self.avg_width + 0.1 * width
        
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
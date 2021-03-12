#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 03.02.2021
Updated on 03.12.2021

Author: haoshuai@handaotech.com
'''

import os


def preprocessResults(results, index=0):
    boxes = results['boxes']
    labels = results['labels']
    
    width = list()
    boxes_info = list()
    boxes_index = list()
    
    for i, box in enumerate(boxes):
        label = labels[i]
        if label == index: # Filter out other defects
            boxes_info.append((box[0] + box[2]) / 2)
            boxes_index.append(i)
            width.append(box[2] - box[0])
            
    pattern = {
        'x': boxes_info,
        'width': width,
        'indices': boxes_index
    }
    results['pattern'] = pattern
    
    return results
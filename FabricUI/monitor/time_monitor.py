#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 03.03.2020
Updated on 03.08.2021

Author: haoshuai@handaotech.com
'''


import os
import time


class TimerNotInitError(Exception):
    def __init__(self):
        super().__init__(self) 
        self.errorinfo = 'The timer has not been initialized.'
    def __str__(self):
        return self.errorinfo


class TimeMonitor(object):
    """ Monitor for the running time 
    
    Attributes:
        num: Length for the time queue for the average calculation
        delimiter: The last key in the printing group
        
    Raises:
        TimerNotInitError: Start time not initialized
    
    """
    def __init__(self, num=1, delimiter=''):
        self.setNum(num)
        self.setDelimiter(delimiter)
        self.time_dict = {}
        
    def setNum(self, num):
        num = int(max(1, num))
        self.num = num
        
    def setDelimiter(self, delimiter):
        self.delimiter = delimiter
        
    def init(self):
        self.start = time.time()
        
    def append(self, key):
        t = time.time()
        start = self.start
        
        if key in self.time_dict:
            self.time_dict[key].append(max(0, t-start))
            if len(self.time_dict[key]) == self.num:
                ta = self.calculate(self.time_dict[key])
                self.printTime(key, ta)
                self.clearKey(key)
        else:
            self.time_dict[key] = [max(0, t-start)]
            
        self.start = t
            
    def calculate(self, time_queue):
        return sum(time_queue)/len(time_queue)
        
    def printTime(self, key, t):
        print("The averaged time for", key, "is", t, "second(s).")
        if key == self.delimiter: print('\n')
        
    def clearKey(self, key):
        self.time_dict[key] = list()
        
    def clearAll(self):
        self.time_dict = {}
        del self.start
       
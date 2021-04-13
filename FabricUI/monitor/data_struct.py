#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 03.08.2021
Updated on 03.08.2021

Author: haoshuai@handaotech.com
'''

import os


class MonitorQueue(list):
    def __init__(self, max_length=1):
        super(MonitorQueue, self).__init__()
        self.max_length = max(1, int(max_length))
        self.is_full = False
        
    def setLength(self, max_length):
        max_length = max(1, int(max_length))
        self.max_length = max_length
        
        if len(self) > max_length: 
            self.is_full = True
            for i in range(len(self)-max_length): 
                super(MonitorQueue, self).pop(-1)
        
    def append(self, val):
        super(MonitorQueue, self).append(val)
        if len(self) > self.max_length: 
            super(MonitorQueue, self).pop(0)
            self.is_full = True
        elif len(self) == self.max_length: 
            self.is_full = True
            
    def getVal(self):
        return self.getAverage()
    
    def getDiff(self):
        return self.getAbstractDiff()
        
    def getAverage(self):
        return sum(self)/len(self)
        
    def getAbstractDiff(self):
        return max(self) - min(self)
        
    def getMax(self):
        return max(self)
        
    def getMin(self):
        return min(self)
        
    
if __name__ == "__main__":
    q = MonitorQueue(5)
    for i in range(5):
        q.append(i)
        
    print(q.getAverage())
    print(q.getDiff())
        
        




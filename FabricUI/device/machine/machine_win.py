#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 03.19.2021
Updated on 03.19.2021

Author: haoshuai@handaotech.com
'''


class Machine(object):
    def __init__(self, params):
        self.updateParams(params)
        
    def updateParams(self, params):
        self.params = params
        
    def start(self) -> bool:
        return True
        
    def stop(self) -> bool:
        return True
#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 03.02.2021
Updated on 03.19.2021

Author: haoshuai@handaotech.com
'''

import os
import RPi.GPIO as GPIO


class Machine(object):
    def __init__(self, params):
        self.updateParams(params)
        
    def updateParams(self, params):
        self.input_pin = params['input_pin']
        # set default value
        self.prev_value = None
        # set to BCM mode
        GPIO.setmode(GPIO.BCM)
        # set the pin as input
        GPIO.setup(self.input_pin, GPIO.OUT)
        
        self.params = params
        
    def start(self) -> bool:
        try:
            GPIO.output(self.input_pin, GPIO.LOW)
            return True
        except Exception as expt:
            return False
        
    def stop(self) -> bool:
        try:
            GPIO.output(self.input_pin, GPIO.HIGH)
            return True
        except Exception as expt:
            return False


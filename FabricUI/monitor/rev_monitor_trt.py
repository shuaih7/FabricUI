#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.20.2020
Updated on 03.08.2021

Author: haoshuai@handaotech.com
'''


import os
import time

import RPi.GPIO as GPIO
from PyQt5.QtCore import QThread, pyqtSignal

from .data_struct import MonitorQueue


class RevMonitor(QThread):
    """Get the signal from the proximity detector and send to the HMI class

    Attributes:
        params:
    
    """
    revSignal = pyqtSignal(float)

    def __init__(self, params, parent=None):
        super(RevMonitor, self).__init__(parent)
        self.updateParams(params)
    
    def updateParams(self, params):
        self.params = params
        
        self.input_pin = params["input_pin"]
        # set default value
        self.prev_value = None
        # set to BCM mode
        GPIO.setmode(GPIO.BCM)
        # set the pin as input
        GPIO.setup(self.input_pin, GPIO.IN)
        
        # Initialize the revolution-steady monitor parameters
        self.is_steady = False
        self.steady_turns = params["steady_turns"]
        self.rev_offset = params["rev_offset"]
        self.rev_queue = MonitorQueue(self.steady_turns)
    
    def updateRevStatus(self, rev):
        self.rev_queue.append(rev)
        
        if not self.rev_queue.is_full:
            self.is_steady = False
        elif self.rev_queue.getDiff() < self.rev_offset:
            self.is_steady = True
        else:
            self.is_steady = False
        
    def run(self):
        try:
            start = time.time()
            # set start time to measure second used per round
            while True:
                value = GPIO.input(self.input_pin)
                
                if value != self.prev_value:
                    # GPIO is HIGH when no signal coming in
                    if value == GPIO.HIGH:
                        value_str = 'HIGH'
                    # GPIO changed to LOW when signal coming in
                    else:
                        value_str = 'LOW'
                        # calculate second used per round
                        spr = time.time() - start
                        # calculate RPM
                        rev = 60.0 / spr
                        # send out the revolution value
                        self.updateRevStatus(rev)
                        self.revSignal.emit(round(rev, 3))
                        # reset start time for next round
                        start = time.time()
                    self.prev_value = value
                    
        except Exception as expt:
            print(expt)
        finally:
            GPIO.cleanup()
#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.20.2020
Updated on 12.30.2020

Author: haoshuai@handaotech.com
'''


import os
import time

import RPi.GPIO as GPIO
from PyQt5.QtCore import QThread, pyqtSignal


class RevMonitor(QThread):
    """Get the signal from the proximity detector and send to the HMI class

    Attributes:
        params:
    
    """
    revSignal = pyqtSignal(float)

    def __init__(self, params, parent=None):
        super(RevMonitor, self).__init__(parent)
        self.params = params
        
        self.input_pin = params["input_pin"]
        # set default value
        self.prev_value = None
        # set to BCM mode
        GPIO.setmode(GPIO.BCM)
        # set the pin as input
        GPIO.setup(self.input_pin, GPIO.IN)

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
                        rpm = 60.0 / spr
                        # send out the revolution value
                        self.revSignal.emit(round(rpm, 3))
                        # reset start time for next round
                        start = time.time()
                    self.prev_value = value
                    
        except Exception as expt:
            print(expt)
        finally:
            GPIO.cleanup()
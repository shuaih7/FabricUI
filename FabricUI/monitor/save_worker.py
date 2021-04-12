#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 04.12.2020
Updated on 04.13.2021

Author: haoshuai@handaotech.com
'''


import os
import cv2
import time
import json
import asyncio
import numpy as np
from datetime import datetime

from PyQt5.QtCore import QThread, pyqtSignal
from threading import Thread


class SaveWorker(QThread):

    def __init__(self, params, parent=None):
        super(SaveWorker, self).__init__(parent)
        self.updateParams(params)
        
    def updateParams(self, params):
        self.save_dir = params['save_dir']
        self.save_prob = params['save_prob']
        self.save_cycles = params['save_cycles']
        
        self.async_saved = 0
        self.frames_to_save = 0
        self.frames_saving = 0
        self.prefix_dir = ''
        self.is_start = False
        self.params = params
          
    async def saveFunc(self, image, results):
        fname = datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')[:-3]
        prefix = os.path.join(self.prefix_dir, fname)
        
        cv2.imwrite(prefix + '.png', image)
        with open(prefix + '.json', "w", encoding="utf-8") as f:
            res_obj = json.dumps(results, indent=4)
            f.write(res_obj)
            f.close()
        self.async_saved += 1
        
    def __call__(self, image, results):
        if not self.is_start and self.checkMutex():
            if np.random.uniform(0, 1) > self.save_prob: return
            self.initSaveStatus(results)
            self.save(image, results)
        elif self.is_start and self.frames_saving < self.frames_to_save:
            self.save(image, results)
        else:
            self.is_start = False
        
    def save(self, image, results):
        self.frames_saving += 1
        asyncio.run_coroutine_threadsafe(self.saveFunc(image, results), self.loop)
        
    def checkMutex(self):
        if self.async_saved == self.frames_to_save:
            return True
        else:
            return False
        
    def initSaveStatus(self, results):
        rev = results['rev']
        intv = results['intv']
        self.async_saved = 0
        self.frames_saving = 0
        self.frames_to_save = int((60/rev)/intv * self.save_cycles) + 1
        self.is_start = True
        
        parent_dir = os.path.join(self.save_dir, datetime.now().strftime('%Y-%m-%d'))
        if not os.path.exists(parent_dir):
            try: os.mkdir(parent_dir)
            except Exception as expt: print(expt)
        
        self.prefix_dir = os.path.join(parent_dir, datetime.now().strftime('%H-%M-%S-%f')[:-3])
        if not os.path.exists(self.prefix_dir):
            try: os.mkdir(self.prefix_dir)
            except Exception as expt: print(expt)

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
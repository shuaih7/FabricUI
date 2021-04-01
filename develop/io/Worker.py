#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 04.01.2020
Updated on 04.01.2021

Author: haoshuai@handaotech.com
'''


import os
import cv2
import time
import asyncio

from PyQt5.QtCore import QThread, pyqtSignal
from threading import Thread


class SaveWorker(QThread):

    def __init__(self, parent=None):
        super(SaveWorker, self).__init__(parent)
        self.image_list = list()
        
    def append(self, image):
        self.image_list.append(image)
        
    async def saveFunc(self, image):
        print('saveing...')
        cv2.imwrite('./image.png', image)
        print('Finished...')
        
    def save(self, image):
        asyncio.run_coroutine_threadsafe(self.saveFunc(image), self.loop)

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
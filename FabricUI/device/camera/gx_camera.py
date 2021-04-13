#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 02.04.2021
Updated on 02.05.2021

Author: haoshaui@handaotech.com
        hanjie@handaotech.com
'''

import os
import sys
import cv2

camera_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(camera_path)

import gxipy as gx
from .camera import *


def acq_color(device):
    img = None

    # send software trigger command
    device.TriggerSoftware.send_command()

    # get raw image
    raw_image = device.data_stream[0].get_image()
    if raw_image is None: return img

    # get RGB image from raw image
    rgb_image = raw_image.convert("RGB")
    if rgb_image is None: return img

    # create numpy array with data from raw image
    numpy_image = rgb_image.get_numpy_array()
    if numpy_image is None: return img

    return numpy_image


def acq_mono(device):
    device.TriggerSoftware.send_command()

    # get raw image
    raw_image = device.data_stream[0].get_image()
    if raw_image is None: return None

    # create numpy array with data from raw image
    numpy_image = raw_image.get_numpy_array()
    if numpy_image is None: return None

    return numpy_image


class GXCamera(Camera):
    def __init__(self, params):
        """ API connecting the Daheng Mercury industrial camera
        
        Attributes:
            params: Camera configuration parameters
        
        Raises:
            CameraNotFound: Could not find the specified camera
        
        """
        super(GXCamera, self).__init__(params=params)
        
        self.cam = None
        self.device_manager = gx.DeviceManager()
        
        self.search()
        self.connect()
        
    def search(self):
        dev_num, dev_info_list = self.device_manager.update_device_list()
        if dev_num is 0:
            raise CameraNotFoundError("未搜索到可连接的相机。")
        
    def connect(self):
        # Connect the first device
        self.cam = self.device_manager.open_device_by_index(1)
        self.cam.TriggerMode.set(gx.GxSwitchEntry.ON)
        self.cam.TriggerSource.set(gx.GxTriggerSourceEntry.SOFTWARE)

        # Start data acquisition
        self.cam.stream_on()
        self.initSettings()
        
    def reconnect(self):
        del self.cam
        self.search()
        self.connect()
        
    def getImage(self):
        if self.cam.PixelColorFilter.is_implemented() is True:
            img = acq_color(self.cam)
        else:
            img = acq_mono(self.cam)

        return img
        
    def updateParams(self, params):
        self.params = params
        self.initSettings()

    def initSettings(self):
        self.set_expo(self.params["exposure_time"])
        self.set_gain(self.params["gain"])
        self.set_binning(self.params["binning"])

    def set_expo(self, exposure_time=300):
        self.cam.ExposureTime.set(exposure_time)

    def set_gain(self, gain=25):
        self.cam.Gain.set(gain)

    def set_binning(self, inning=4):
        try:  # Because some DH cameras do not support "binning"
            self.cam.BinningHorizontal.set(binning)
            self.cam.BinningVertical.set(binning)
        except Exception as expt:
            print(expt)

    def __del__(self):
        try:
            self.cam.stream_off()
            self.cam.close_device()
            del self.cam
        except:
            return
            
            
if __name__ == "__main__":
    params = {
        "exposure_time": 1000,
        "gain": 24,
        "binning": 4
    }
    reader = GXCamera(params)
    while True:
        img = reader.getImage()
        if img is None: continue
        img = cv2.resize(img, (720,540), cv2.INTER_LINEAR)
        cv2.imshow("gx image", img)
        key = cv2.waitKey(10)
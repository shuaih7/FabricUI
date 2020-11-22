#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.20.2020
Updated on 11.20.2020

Author: haoshaui@handaotech.com
'''

import gxipy as gx
import os, json, time, cv2
import datetime
from PIL import Image


def getCamera(config_matrix, logger):
    cam_config = config_matrix["Camera"]
    
    # Fetch the config parameters
    SN = camera_config['DeviceSerialNumber']
    ExposureTime = camera_config['ExposureTime']
    Gain = camera_config['Gain']
    Binning = camera_config['Binning']
    
    # create a device manager
    device_manager = gx.DeviceManager()
    dev_num, dev_info_list = device_manager.update_device_list()
    if dev_num == 0:
        #logger.warning("Camera not found, please check the camera connection.")
        return
        
    # open the first device
    cam = device_manager.open_device_by_sn(SN)

    # set exposure & gain
    cam.ExposureTime.set(ExposureTime)
    cam.Gain.set(Gain)
    cam.BinningHorizontal.set(Binning)
    cam.BinningVertical.set(Binning)

    # set trigger mode and trigger source
    # cam.TriggerMode.set(gx.GxSwitchEntry.OFF)
    cam.TriggerMode.set(gx.GxSwitchEntry.ON)
    cam.TriggerSource.set(gx.GxTriggerSourceEntry.SOFTWARE)

    # start data acquisition
    cam.stream_on()
    #logger.info("Camera initialized successfully.")
    
    return cam
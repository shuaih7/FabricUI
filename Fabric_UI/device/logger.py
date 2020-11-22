#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.20.2020
Updated on 11.20.2020

Author: haoshaui@handaotech.com
'''

import os, logging

def getLogger(log_path, log_name="log"):
    """
    Initialize the logger 
    :return:
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    #sh = logging.StreamHandler()
    fh = logging.FileHandler(log_name, encoding='utf-8', mode='a')
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    fh.setFormatter(formatter)
    #sh.setFormatter(formatter)
    #logger.addHandler(sh)
    logger.addHandler(fh)
    return logger
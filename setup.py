#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 03.19.2021
Updated on 03.19.2021

Author: haoshuai@handaotech.com
'''


import os
import platform
from setuptools import setup, find_packages

system = platform.system()

if system == "Windows":
    model_dir = "model/win/*"
elif system == "Linux":
    model_dir = "model/trt/*"

with open("README.md") as f:
    readme = f.read()
    
with open("LICENSE") as f:
    license = f.read()
    
with open("FabricUI/_version.py") as f:
    exec(f.read())

with open("requirements.txt") as f:
    requirements = f.read().split("\n")
    
    
setup(
    name="FabricUI",
    version=__version__,
    description="UI design using PyQt5 for fabric defect detection",
    long_description=readme,
    author="Shuai",
    author_email="haoshuai@handaotech.com",
    url="https://github.com/shuaih7/FabricUI",
    license=license,
    classifiers=["Programming Language :: Python :: 3.6.6", 
                 "Programming Language :: Python :: Implementation :: CPython",],
    packages=find_packages(exclude=("docs")),
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=requirements,
    package_data={"FabricUI": ["icon/*", model_dir, "config.json", "HMI.ui", "widget/ConfigWidget.ui"]},
    entry_points={
        "console_scripts": ["FabricUI=FabricUI.main:main"],
    },
    extras_require={
        "cpu": [
            "paddlepaddle>=1.8.4",
        ],
        "gpu": [
            "paddlepaddle-gpu>=1.8.4",
        ]
    },
    test_suits="nose.collector",
    tests_require=["nose"],
)
# -*- coding: utf-8 -*-

# Header ...

import os
from setuptools import setup, find_packages


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
    author_email="shuaih7@gmail.com",
    url="https://github.com/shuaih7/FabricUI",
    license=license,
    classifiers=["Programming Language :: Python :: 3.6.6", 
                 "Programming Language :: Python :: Implementation :: CPython",],
    packages=find_packages(exclude=("docs")),
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=requirements,
    extras_require={
        
    },
    test_suits="nose.collector",
    tests_require=["nose"],
)
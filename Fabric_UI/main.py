#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.19.2020
Updated on 11.19.2020

Author: haoshaui@handaotech.com
'''

import sys
from PyQt5.QtWidgets import QApplication
app = QApplication(sys.argv)
try: from .HMI import MainWindow
except Exception as expt: from HMI import MainWindow


def main():
    Window = MainWindow()
    Window.showMaximized()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
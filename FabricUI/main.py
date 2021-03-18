#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.19.2020
Updated on 03.19.2020

Author: haoshuai@handaotech.com
'''

import sys
from PyQt5.QtWidgets import QApplication
app = QApplication(sys.argv)

from HMI import MainWindow


def main():
    Window = MainWindow()
    Window.showMaximized()
    Window.live()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

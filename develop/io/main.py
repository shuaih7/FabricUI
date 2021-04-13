#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 03.31.2020
Updated on 03.31.2020

Author: haoshuai@handaotech.com
'''

import sys
from PyQt5.QtWidgets import QApplication
app = QApplication(sys.argv)

from Widget import Widget


def main():
    Window = Widget()
    Window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

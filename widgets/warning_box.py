# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 10:38:17 2021

@author: ogurreck
"""
from PyQt5 import QtWidgets

class WarningBox(QtWidgets.QMessageBox):
    def __init__(self, title, msg, info=None, details=None):
        super().__init__()
        self.setIcon(self.Warning)
        self.setWindowTitle(title)
        self.setText(msg)
        if info:
            self.setInformativeText(info)
        if details:
            self.setDetailedText(details)
        self.setStandardButtons(self.Ok)
        self.__exec__()

    def __exec__(self):
        self.exec_()
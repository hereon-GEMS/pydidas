# -*- coding: utf-8 -*-
"""
Created on Thu Mar 25 11:40:35 2021

@author: ogurreck
"""
from PyQt5 import QtCore, QtWidgets
from functools import partial

from plugin_workflow_gui.config.qt_presets import STYLES

class _Metadata(QtCore.QObject):
    checked_state = QtCore.pyqtSignal(bool, bool, bool)

    def __init__(self):
        super().__init__()
        self.checked = [False, False, False]

    def update_checks(self, i):
        self.checked[i] = not self.checked[i]
        self.checked_state.emit(*self.checked)

class _MetadataFactory:
    def __init__(self):
        self._instance = None

    def __call__(self):
        if not self._instance:
            self._instance = _Metadata()
        return self._instance

Metadata = _MetadataFactory()

class ConfirmationBar(QtWidgets.QFrame):

    def __init__(self, parent=None, qt_main=None, master=None):
        super().__init__(parent)
        self.parent = parent
        self.qt_main = qt_main
        self.master = master

        self.setFixedHeight(70)

        self.label = QtWidgets.QLabel('Confirm\nConfiguration: ', self)
        self.label.setStyleSheet(STYLES['subtitle'])
        self.check_experiment = QtWidgets.QCheckBox('Experiment description', self)
        self.check_scan = QtWidgets.QCheckBox('Scan description', self)
        self.check_workflow = QtWidgets.QCheckBox('Workflow configuration', self)


        _layout = QtWidgets.QHBoxLayout(self)
        _layout.addWidget(self.label, 0, QtCore.Qt.AlignLeft)
        _layout1 = QtWidgets.QVBoxLayout(self)
        _layout1.setContentsMargins(20, 0, 0, 0)
        _layout1.addWidget(self.check_experiment)
        _layout1.addWidget(self.check_scan)
        _layout1.addWidget(self.check_workflow)
        _layout.addLayout(_layout1)
        _layout.setAlignment(QtCore.Qt.AlignLeft)
        _layout.setContentsMargins(5, 2, 0, 0)
        self.setLayout(_layout)

        self.check_experiment.clicked.connect(partial(Metadata().update_checks, 0))
        self.check_scan.clicked.connect(partial(Metadata().update_checks, 1))
        self.check_workflow.clicked.connect(partial(Metadata().update_checks, 2))

        Metadata().checked_state.connect(self.set_buttons)

    def update_references(self, parent=None, qt_main=None, master=None):
        if parent:
            self.setParent(parent)
        self.qt_main = qt_main if qt_main else self.qt_main
        self.master = master if master else self.master

    @QtCore.pyqtSlot(bool, bool, bool)
    def set_buttons(self, state0, state1, state2):
        self.check_experiment.setChecked(state0)
        self.check_scan.setChecked(state1)
        self.check_workflow.setChecked(state2)

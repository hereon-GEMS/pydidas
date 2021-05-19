# MIT License
#
# Copyright (c) 2021 Malte Storm, Helmholtz-Zentrum Hereon.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Module with the WorkflowEditFrame which is used to create the workflow
tree."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['PyfaiCalibFrame']

import os
from PyQt5 import QtWidgets, QtGui, QtCore

import functools

import pyFAI
from pyFAI.gui.model import MarkerModel
from pyFAI.gui.utils import projecturl
from pyFAI.gui.CalibrationWindow import MenuItem
from pyFAI.gui.CalibrationContext import CalibrationContext
from pyFAI.app.calib2 import parse_options, setup_model

from plugin_workflow_gui.gui.toplevel_frame import ToplevelFrame
from plugin_workflow_gui.core import GlobalSettings
GLOBAL_SETTINGS = GlobalSettings()



settings = QtCore.QSettings(QtCore.QSettings.IniFormat,
                            QtCore.QSettings.UserScope,
                            "pyfai",
                            "pyfai-calib2",
                            None)
CalibrationContext._releaseSingleton()
# try:
context = CalibrationContext(settings)
# except:
#     context = CalibrationContext.instance()
context.restoreSettings()
options = parse_options()
setup_model(context.getCalibrationModel(), options)

# register_param

def pyfaiCalibIcon():
    return QtGui.QIcon('\\'.join([os.path.dirname(pyFAI.__file__),
                                  'resources', 'gui', 'images', 'icon.png']))

def pyfaiRingIcon():
    return QtGui.QIcon('\\'.join([os.path.dirname(pyFAI.__file__),
                                  'resources', 'gui', 'icons',
                                  'task-identify-rings.svg']))



class PyfaiCalibFrame(ToplevelFrame):
    def __init__(self, **kwargs):
        mainWindow = kwargs.get('mainWindow', None)
        parent = kwargs.get('parent', None)
        super().__init__(parent, initLayout=False)
        if mainWindow:
            context.setParent(mainWindow)
        else:
            context.setParent(self)


        self._list = QtWidgets.QListWidget(self)
        self._list.setSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                 QtWidgets.QSizePolicy.Expanding)
        self._list.setFixedWidth(150)
        self._help = QtWidgets.QPushButton(self)
        self._help.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                 QtWidgets.QSizePolicy.Fixed)
        self._stack = QtWidgets.QStackedWidget(self)
        self._stack.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                 QtWidgets.QSizePolicy.Expanding)


        _layout = QtWidgets.QGridLayout()
        _layout.addWidget(self._list, 0, 0, 1, 1)
        _layout.addWidget(self._help, 1, 0, 1, 1)
        _layout.addWidget(self._stack, 0, 1, 2, 1)

        self.setLayout(_layout)

        self.__context = context
        model = context.getCalibrationModel()

        self.__menu_connections ={}
        self.__tasks = self.createTasks()
        for task in self.__tasks:
            task.nextTaskRequested.connect(self.nextTask)
            item = MenuItem(self._list)
            item.setText(task.windowTitle())
            item.setIcon(task.windowIcon())
            self._stack.addWidget(task)
            self.__menu_connections[item.text()] = task
            task.warningUpdated.connect(functools.partial(self.__updateTaskState, task, item))
        # self.

        if len(self.__tasks) > 0:
            self._list.setCurrentRow(0)
            # Hide the nextStep button of the last task
            task.setNextStepVisible(False)

        self.setModel(model)
        self._list.currentRowChanged.connect(self._stack.setCurrentIndex)

        url = projecturl.get_documentation_url("")
        if url.startswith("http"):
            self._help.setText("Online help...")
        self._helpText = self._help.text()
        self._help.clicked.connect(self.__displayHelp)

    def __displayHelp(self):
        subpath = "usage/cookbook/calib-gui/index.html"
        url = projecturl.get_documentation_url(subpath)
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))

    def __updateTaskState(self, task, item):
        warnings = task.nextStepWarning()
        item.setWarnings(warnings)

    def update_stack(self, text):
        w = self.__menu_connections[text]
        self._stack.setCurrentWidget(w)


    def closeEvent(self, event):
        poniFile = self.model().experimentSettingsModel().poniFile()
        event.accept()

        for task in self.__tasks:
            task.aboutToClose()
        self.__context.saveWindowLocationSettings("main-window", self)

    def createTasks(self):
        from pyFAI.gui.tasks.ExperimentTask import ExperimentTask
        from pyFAI.gui.tasks.MaskTask import MaskTask
        from pyFAI.gui.tasks.PeakPickingTask import PeakPickingTask
        from pyFAI.gui.tasks.GeometryTask import GeometryTask
        from pyFAI.gui.tasks.IntegrationTask import IntegrationTask

        tasks = [
            ExperimentTask(),
            MaskTask(),
            PeakPickingTask(),
            GeometryTask(),
            IntegrationTask()
        ]
        return tasks

    def model(self):
        return self.__model

    def setModel(self, model):
        self.__model = model
        if len(self.__model.markerModel()) == 0:
            origin = MarkerModel.PixelMarker("Origin", 0, 0)
            self.__model.markerModel().add(origin)
        for task in self.__tasks:
            task.setModel(self.__model)

    def nextTask(self):
        index = self._list.currentRow() + 1
        if index < self._list.count():
            self._list.setCurrentRow(index)




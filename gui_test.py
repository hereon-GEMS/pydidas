"""
Created on Thu Mar 11 10:24:52 2021

@author: ogurreck
"""

import sys
import os
import re
import time

from functools import partial

#from qtpy import QtWidgets, QtGui, QtCore
from PyQt5 import QtWidgets, QtGui, QtCore, Qt

import qtawesome as qta

import pydidas
WORKFLOW_EDIT_MANAGER = pydidas.gui.WorkflowEditTreeManager()
PLUGIN_COLLECTION = pydidas.GetPluginCollection()
STYLES = pydidas.config.STYLES
PALETTES = pydidas.config.PALETTES
STANDARD_FONT_SIZE = pydidas.config.STANDARD_FONT_SIZE

from pydidas.gui import (DataBrowsingFrame,  WorkflowEditFrame, BaseFrame,
    ExperimentSettingsFrame, ScanSettingsFrame, ProcessingSinglePluginFrame,
    ProcessingFullWorkflowFrame, CompositeCreatorFrame)
from pydidas.widgets.param_config import ParameterConfigMixIn

class HomeFrame(BaseFrame):
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        name = kwargs.get('Name', None)
        super().__init__(parent=parent, name=name)
        self.create_label('Welcome to pyDIDAS', fontsize=14, bold=True, fixedWidth=400)
        self.create_label('the python Diffraction Data Analysis Suite.\n', fontsize=13,
                         bold=True, fixedWidth=400)
        self.create_label('\nQuickstart:', fontsize=12, bold=True, fixedWidth=400)
        self.create_label('\nMenu toolbar: ', fontsize=11, underline=True, bold=True, fixedWidth=400)
        self.create_label('Use the menu toolbar on the left to switch between'
                         ' different Frames. Some menu toolbars will open an '
                         'additional submenu on the left.', fixedWidth=600)


class ProcessingSetupFrame(BaseFrame):
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        name = kwargs.get('Name', None)
        super().__init__(parent, name)


class ToolsFrame(BaseFrame):
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        name = kwargs.get('Name', None)
        super().__init__(parent, name)


class ProcessingFrame(BaseFrame):
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        name = kwargs.get('Name', None)
        super().__init__(parent, name)

class ResultVisualizationFrame(BaseFrame, ParameterConfigMixIn):
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        name = kwargs.get('Name', None)
        super().__init__(parent, name)
        self.create_label('Result visualization', fontsize=14,
                              gridPos=(0, 0, 1, 5))


if __name__ == '__main__':
    from pydidas.gui.main_window import MainWindow

    app = QtWidgets.QApplication(sys.argv)
    #app.setStyle('Fusion')

    # needs to be initialized after the app has been created.
    # sys.excepthook = pydidas.widgets.excepthook
    CENTRAL_WIDGET_STACK = pydidas.widgets.CentralWidgetStack()

    _font = app.font()
    _font.setPointSize(STANDARD_FONT_SIZE)
    app.setFont(_font)
    gui = MainWindow()

    from pydidas.gui.pyfai_calib_frame import PyfaiCalibFrame, pyfaiCalibIcon
    gui.register_frame('Home', 'Home', qta.icon('mdi.home'), HomeFrame)
    gui.register_frame('Data browsing', 'Data browsing', qta.icon('mdi.image-search-outline'), DataBrowsingFrame)
    gui.register_frame('Tools', 'Tools', qta.icon('mdi.tools'), ToolsFrame)
    gui.register_frame('pyFAI calibration', 'Tools/pyFAI calibration', pyfaiCalibIcon(), PyfaiCalibFrame)
    gui.register_frame('Composite image creator', 'Tools/Composite image creator', qta.icon('mdi.view-comfy'), CompositeCreatorFrame)
    gui.register_frame('Processing setup', 'Processing setup', qta.icon('mdi.cogs'), ProcessingSetupFrame)
    gui.register_frame('Processing', 'Processing', qta.icon('mdi.sync'), ProcessingFrame)
    gui.register_frame('Result visualization', 'Result visualization', qta.icon('mdi.monitor-eye'), ResultVisualizationFrame)
    gui.register_frame('Run single plugins', 'Processing/Run single plugins', qta.icon('mdi.debug-step-over'), ProcessingSinglePluginFrame)
    gui.register_frame('Run full processing', 'Processing/Run full procesing', qta.icon('mdi.play-circle-outline'), ProcessingFullWorkflowFrame)
    gui.register_frame('Experimental settings', 'Processing setup/Experimental settings', qta.icon('mdi.card-bulleted-settings-outline'), ExperimentSettingsFrame)
    gui.register_frame('Scan settings', 'Processing setup/Scan settings', qta.icon('ei.move'), ScanSettingsFrame)
    gui.register_frame('Workflow editing', 'Processing setup/Workflow editing', qta.icon('mdi.clipboard-flow-outline'), WorkflowEditFrame)
    # gui.register_frame('Help', 'Tools/help', qta.icon('mdi.home'), QtWidgets.QFrame())
    gui.create_toolbars()

    gui.show()
    sys.exit(app.exec_())

    app.deleteLater()

# -*- coding: utf-8 -*-
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
import numpy as np

import pydidas as pwg

WORKFLOW_EDIT_MANAGER = pwg.gui.WorkflowEditTreeManager()
PLUGIN_COLLECTION = pwg.PluginCollection()
STYLES = pwg.config.STYLES
PALETTES = pwg.config.PALETTES
STANDARD_FONT_SIZE = pwg.config.STANDARD_FONT_SIZE

from pydidas.gui import DataBrowsingFrame,  WorkflowEditFrame, ToplevelFrame, ExperimentSettingsFrame, ScanSettingsFrame


class HomeFrame(ToplevelFrame):
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        name = kwargs.get('Name', None)
        super().__init__(parent=parent, name=name)
        self.add_textbox('Welcome to pyDIDAS', 14, bold=True)
        self.add_textbox('the python Diffraction Data Analysis Suite.\n', 13,
                         bold=True)
        self.add_textbox('\nQuickstart:', 12, bold=True)
        self.add_textbox('\nMenu toolbar: ', 11, underline=True, bold=True)
        self.add_textbox('Use the menu toolbar on the left to switch between'
                         ' different Frames. Some menu toolbars will open an '
                         'additional submenu on the left.')


class ProcessingSetupFrame(ToplevelFrame):
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        name = kwargs.get('Name', None)
        super().__init__(parent, name)


class ToolsFrame(ToplevelFrame):
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        name = kwargs.get('Name', None)
        super().__init__(parent, name)


class ProcessingFrame(ToplevelFrame):
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        name = kwargs.get('Name', None)
        super().__init__(parent, name)

class ResultVisualizationFrame(ToplevelFrame):
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        name = kwargs.get('Name', None)
        super().__init__(parent, name)


if __name__ == '__main__':
    from pydidas.gui.main_window import MainWindow

    app = QtWidgets.QApplication(sys.argv)
    #app.setStyle('Fusion')

    # needs to be initialized after the app has been created.
    sys.excepthook = pwg.widgets.excepthook
    CENTRAL_WIDGET_STACK = pwg.widgets.CentralWidgetStack()



    _font = app.font()
    _font.setPointSize(STANDARD_FONT_SIZE)
    app.setFont(_font)
    gui = MainWindow()

    from pydidas.gui.pyfai_calib_frame import PyfaiCalibFrame, pyfaiCalibIcon
    gui.register_frame('Home', 'Home', qta.icon('mdi.home'), HomeFrame)
    gui.register_frame('Data browsing', 'Data browsing', qta.icon('mdi.image-search-outline'), DataBrowsingFrame)
    gui.register_frame('Tools', 'Tools', qta.icon('mdi.tools'), ToolsFrame)
    gui.register_frame('pyFAI calibration', 'Tools/pyFAI calibration', pyfaiCalibIcon(), PyfaiCalibFrame)
    gui.register_frame('Processing setup', 'Processing setup', qta.icon('mdi.cogs'), ProcessingSetupFrame)
    gui.register_frame('Processing', 'Processing', qta.icon('mdi.sync'), ProcessingFrame)
    gui.register_frame('Result visualization', 'Result visualization', qta.icon('mdi.monitor-eye'), ResultVisualizationFrame)
    gui.register_frame('Home 2', 'Processing/Home', qta.icon('mdi.home'), HomeFrame)
    gui.register_frame('Help', 'Processing/Home2', qta.icon('mdi.home'), HomeFrame)
    gui.register_frame('Help', 'Tools/help/Help/help', qta.icon('mdi.home'), HomeFrame)
    gui.register_frame('Experimental settings', 'Processing setup/Experimental settings', qta.icon('mdi.card-bulleted-settings-outline'), ExperimentSettingsFrame)
    gui.register_frame('Scan settings', 'Processing setup/Scan settings', qta.icon('ei.move'), ScanSettingsFrame)
    gui.register_frame('Workflow editing', 'Processing setup/Workflow editing', qta.icon('mdi.clipboard-flow-outline'), WorkflowEditFrame)
    gui.register_frame('Help', 'Tools/help/Help 2', qta.icon('mdi.home'), HomeFrame)
    # gui.register_frame('Help', 'Tools/help', qta.icon('mdi.home'), QtWidgets.QFrame())
    gui.create_toolbars()


    # WORKFLOW_EDIT_MANAGER.add_plugin_node('HDF loader', 'Test title 0')
    # WORKFLOW_EDIT_MANAGER.add_plugin_node('HDF loader', 'Test title 1')
    # WORKFLOW_EDIT_MANAGER.add_plugin_node('HDF loader', 'Test title 2')
    # WORKFLOW_EDIT_MANAGER.add_plugin_node('HDF loader', 'Test title 3')
    # WORKFLOW_EDIT_MANAGER.set_active_node(2)
    # WORKFLOW_EDIT_MANAGER.add_plugin_node('HDF loader', 'Test title 4')
    # WORKFLOW_EDIT_MANAGER.add_plugin_node('HDF loader', 'Test title 5')
    # WORKFLOW_EDIT_MANAGER.set_active_node(2)
    # WORKFLOW_EDIT_MANAGER.add_plugin_node('HDF loader', 'Test title 6')
    # WORKFLOW_EDIT_MANAGER.add_plugin_node('HDF loader', 'Test title 7')
    # WORKFLOW_EDIT_MANAGER.set_active_node(6)
    # WORKFLOW_EDIT_MANAGER.add_plugin_node('HDF loader', 'Test title 8')

    gui.show()
    sys.exit(app.exec_())

    app.deleteLater()
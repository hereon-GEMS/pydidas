"""
Created on Thu Mar 11 10:24:52 2021

@author: ogurreck
"""

import sys
from PyQt5 import QtWidgets, QtCore, QtGui

import qtawesome as qta
import numpy as np

import pydidas
WORKFLOW_EDIT_MANAGER = pydidas.gui.WorkflowTreeEditManager()
PLUGIN_COLLECTION = pydidas.plugins.PluginCollection()
STANDARD_FONT_SIZE = pydidas.constants.STANDARD_FONT_SIZE

from pydidas.gui import (
    DataBrowsingFrame,  WorkflowEditFrame,
    ExperimentSettingsFrame, ScanSettingsFrame, ProcessingSinglePluginFrame,
    ExecuteWorkflowFrame, CompositeCreatorFrame)
from pydidas.widgets.parameter_config import ParameterWidgetsMixIn
from pydidas.widgets import BaseFrame

from pydidas.core import ExperimentalSettings, ScanSettings
from pydidas.workflow_tree import WorkflowResults, WorkflowTree

EXP = ExperimentalSettings()
SCAN = ScanSettings()
RESULTS = WorkflowResults()
TREE = WorkflowTree()

SCAN.import_from_file('H:/myPython/pydidas/tests_of_workflow/__scan_settings.yaml')
EXP.import_from_file('H:/myPython/pydidas/tests_of_workflow/__calib.poni')
TREE.import_from_file('H:/myPython/pydidas/tests_of_workflow/__workflow_new.yaml')


import pickle
from pydidas.core import Dataset
RESULTS.__dict__ = pickle.load(open('d:/tmp/saved_results/results.pickle', 'rb'))
for _i in [1, 2]:
    _data = Dataset(np.load(f'd:/tmp/saved_results/node_{_i:02d}.npy'))
    _meta = pickle.load(open(f'd:/tmp/saved_results/node_{_i:02d}.pickle', 'rb'))
    _data.axis_labels = _meta['axis_labels']
    _data.axis_units = _meta['axis_units']
    _data.axis_ranges = _meta['axis_ranges']
    RESULTS._WorkflowResults__composites[_i] = _data



class HomeFrame(BaseFrame):
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent)
        self.create_label('label_welcome', 'Welcome to pyDIDAS', fontsize=14, bold=True, fixedWidth=400)
        self.create_label('label_full_name', '- the python Diffraction Data Analysis Suite.\n', fontsize=13,
                         bold=True, fixedWidth=400)
        self.create_label('label_quickstart', '\nQuickstart:', fontsize=12, bold=True, fixedWidth=400)
        self.create_label('label_toolbar', '\nMenu toolbar: ', fontsize=11, underline=True, bold=True, fixedWidth=400)
        self.create_label('label_toolbar_use', 'Use the menu toolbar on the left to switch between'
                         ' different Frames. Some menu toolbars will open an '
                         'additional submenu on the left.', fixedWidth=600)


class ProcessingSetupFrame(BaseFrame):
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent)


class ToolsFrame(BaseFrame):
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent)


class ProcessingFrame(BaseFrame):
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent)
        self.create_label('title', 'Processing', fontsize=14,
                          gridPos=(0, 0, 1, 5))


class ResultVisualizationFrame(BaseFrame, ParameterWidgetsMixIn):
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent)
        self.create_label('title', 'Result visualization', fontsize=14,
                          gridPos=(0, 0, 1, 5))


def run_gui(app):
    from pydidas.gui.main_window import MainWindow
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
    # gui.register_frame('Processing', 'Processing', qta.icon('mdi.sync'), ProcessingFrame)
    # gui.register_frame('Result visualization', 'Result visualization', qta.icon('mdi.monitor-eye'), ResultVisualizationFrame)
    # gui.register_frame('Run single plugins', 'Processing/Run single plugins', qta.icon('mdi.debug-step-over'), ProcessingSinglePluginFrame)
    gui.register_frame('Run full processing', 'Run full procesing', qta.icon('mdi.sync'), ExecuteWorkflowFrame)
    gui.register_frame('Experimental settings', 'Processing setup/Experimental settings', qta.icon('mdi.card-bulleted-settings-outline'), ExperimentSettingsFrame)
    gui.register_frame('Scan settings', 'Processing setup/Scan settings', qta.icon('ei.move'), ScanSettingsFrame)
    gui.register_frame('Workflow editing', 'Processing setup/Workflow editing', qta.icon('mdi.clipboard-flow-outline'), WorkflowEditFrame)
    gui.create_toolbars()

    gui.show()
    sys.exit(app.exec_())
    for widget in CENTRAL_WIDGET_STACK.widgets:
        widget.deleteLater()
    CENTRAL_WIDGET_STACK.deleteLater()
    gui.deleteLater()


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    run_gui(app)
    app.deleteLater()

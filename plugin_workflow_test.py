# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 10:24:52 2021

@author: ogurreck
"""

import sys
#from qtpy import QtWidgets, QtGui, QtCore
from PyQt5 import QtWidgets, QtGui, QtCore, Qt

import plugin_workflow_gui as pwg

WORKFLOW_EDIT_MANAGER = pwg.gui.WorkflowEditTreeManager()
PLUGIN_COLLECTION = pwg.PluginCollection()
STYLES = pwg.config.STYLES
PALETTES = pwg.config.PALETTES

from plugin_workflow_gui.widgets import WorkflowTreeCanvas, PluginCollectionPresenter, ScrollArea
from plugin_workflow_gui.widgets.plugin_config import PluginParamConfig
from plugin_workflow_gui.config import STANDARD_FONT_SIZE
#WorkflowTree = pwg.WorkflowTree()







class WorkflowEditTab(QtWidgets.QWidget):
    def __init__(self, parent=None, params=None):
        super().__init__(parent)
        self.parent = parent
        self.workflow_canvas = WorkflowTreeCanvas(self)
        self.plugin_edit_canvas = PluginParamConfig(self)
        self.w_plugin_collection = PluginCollectionPresenter(self)
        self.workflow_area = ScrollArea(
            self, self.workflow_canvas,
            params['workflow_edit_canvas_x'],
            params['workflow_edit_canvas_y']
        )
        self.plugin_edit_area = ScrollArea(self, self.plugin_edit_canvas, 400, None)
        self.plugin_edit_area.setMinimumHeight(500)

        self.w_plugin_collection.selection_confirmed.connect(self.workflow_add_plugin)

        _layout0 = QtWidgets.QHBoxLayout()
        _layout0.setContentsMargins(5, 5, 5, 5)

        _layout1 = QtWidgets.QVBoxLayout()
        _layout1.setContentsMargins(0, 0, 0, 0)
        _layout1.addWidget(self.workflow_area)
        _layout1.addWidget(self.w_plugin_collection)

        _layout0.addLayout(_layout1)
        _layout0.addWidget(self.plugin_edit_area)

        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setContentsMargins(0, 0, 0, 0)
        _layout.addLayout(_layout0)
        _layout.addWidget(pwg.widgets.ConfirmationBar())
        self.setLayout(_layout)
        WORKFLOW_EDIT_MANAGER.plugin_to_edit.connect(self.configure_plugin)

    def workflow_add_plugin(self, name):
        WORKFLOW_EDIT_MANAGER.add_plugin_node(name)

    @QtCore.pyqtSlot(int)
    def configure_plugin(self, node_id):
        # print(f'configure plugin {node_id}')
        self.plugin_edit_canvas.configure_plugin(node_id)


class ExperimentEditTab(QtWidgets.QWidget):
    def __init__(self, parent=None, qt_main=None, master=None):
        super().__init__(parent)
        self.parent = parent
        self.qt_main = qt_main
        self._layout = QtWidgets.QVBoxLayout()
        _label = QtWidgets.QLabel('Test 123')
        self._layout.addWidget(_label)
        self._layout.addWidget(pwg.widgets.ConfirmationBar())
        self.setLayout(self._layout)


class MainTabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)



class LayoutTest(QtWidgets.QMainWindow):
    name_selected_signal = QtCore.pyqtSlot(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.process = None
        self.setGeometry(20, 40, 1400, 1000)
        self.params = {'workflow_edit_canvas_x': 1000,
                       'workflow_edit_canvas_y': 600}
        self.status = self.statusBar()



        self.main_frame = QtWidgets.QTabWidget()
        self.setCentralWidget(self.main_frame)
        self.status.showMessage('Test status')

        self.experiment_edit_tab = ExperimentEditTab(self.main_frame)
        self.workflow_edit_tab = WorkflowEditTab(self.main_frame, self.params)
        self.main_frame.addTab(self.experiment_edit_tab, 'Experiment editor')
        self.main_frame.addTab(self.workflow_edit_tab, 'Workflow editor')
        WORKFLOW_EDIT_MANAGER.update_qt_items(
            self.workflow_edit_tab.workflow_canvas, self
        )

        WORKFLOW_EDIT_MANAGER.add_plugin_node('HDF loader', 'Test title 0')
        WORKFLOW_EDIT_MANAGER.add_plugin_node('HDF loader', 'Test title 1')
        WORKFLOW_EDIT_MANAGER.add_plugin_node('HDF loader', 'Test title 2')
        WORKFLOW_EDIT_MANAGER.add_plugin_node('HDF loader', 'Test title 3')
        WORKFLOW_EDIT_MANAGER.set_active_node(2)
        WORKFLOW_EDIT_MANAGER.add_plugin_node('HDF loader', 'Test title 4')
        WORKFLOW_EDIT_MANAGER.add_plugin_node('HDF loader', 'Test title 5')
        WORKFLOW_EDIT_MANAGER.set_active_node(2)
        WORKFLOW_EDIT_MANAGER.add_plugin_node('HDF loader', 'Test title 6')
        WORKFLOW_EDIT_MANAGER.add_plugin_node('HDF loader', 'Test title 7')
        WORKFLOW_EDIT_MANAGER.set_active_node(6)
        WORKFLOW_EDIT_MANAGER.add_plugin_node('HDF loader', 'Test title 8')

        self.setWindowTitle('Plugin edit test')
        self._createMenu()

    def action_new(self):
        print('new')

    def action_open(self):
        print('open')

    def _createMenu(self):
        self._menu = self.menuBar()

        newAction = QtWidgets.QAction(QtGui.QIcon('new.png'), '&New', self)
        newAction.setShortcut('Ctrl+N')
        newAction.setStatusTip('New document')
        newAction.triggered.connect(self.action_new)

        # Create new action
        openAction = QtWidgets.QAction(QtGui.QIcon('open.png'), '&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open document')
        openAction.triggered.connect(self.action_open)

        # Create exit action
        exitAction = QtWidgets.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.closeEvent)

        fileMenu = QtWidgets.QMenu('&File')
        fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)

        self._menu.addMenu(fileMenu)
        self._menu.addMenu("&Edit")
        self._menu.addMenu("&Help")


# class MasterApplication:
#     def __init__(self):
#         self.

if __name__ == '__main__':
    sys.excepthook = pwg.widgets.excepthook
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    _font = app.font()
    _font.setPointSize(STANDARD_FONT_SIZE)
    app.setFont(_font)
# new_font.setPointSize( int ** ); //your option
# new_font.setWeight( int ** ); //your option
# app.setFont( new_font );
    # app.setFont(QtGui.Font('{font-size: 11px;}'))
    gui = LayoutTest()
    gui.show()
    sys.exit(app.exec_())

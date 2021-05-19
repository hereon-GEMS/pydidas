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

import plugin_workflow_gui as pwg

WORKFLOW_EDIT_MANAGER = pwg.gui.WorkflowEditTreeManager()
PLUGIN_COLLECTION = pwg.PluginCollection()
STYLES = pwg.config.STYLES
PALETTES = pwg.config.PALETTES

from plugin_workflow_gui.gui import DataBrowsingFrame,  WorkflowEditFrame, ToplevelFrame, ExperimentSettingsFrame, ScanSettingsFrame
from plugin_workflow_gui.config import STANDARD_FONT_SIZE
from plugin_workflow_gui._exceptions import FrameConfigError



class HomeFrame(ToplevelFrame):
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        name = kwargs.get('Name', None)
        super().__init__(parent=parent, name=name)
        self.add_label('Welcome to pyDIDAS', 14, bold=True)
        self.add_label('the python Diffraction Data Analysis Suite.\n', 13,
                       bold=True)
        self.add_label('\nQuickstart:', 12, bold=True)
        self.add_label('\nMenu toolbar: ', 11, underline=True, bold=True)
        self.add_label('Use the menu toolbar on the left to switch between'
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


class _InfoWidget(QtWidgets.QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setMinimumHeight(50)
        self.resize(500, 50)

    def sizeHint(self):
        return QtCore.QSize(500, 50)

class _InfoWidgetFactory:
    def __init__(self):
        self._instance = None

    def __call__(self):
        if not self._instance:
            self._instance = _InfoWidget()
        return self._instance

InfoWidget = _InfoWidgetFactory()

class LayoutTest(QtWidgets.QMainWindow):
    def __init__(self, parent=None, geometry=None):
        from plugin_workflow_gui.gui.pyfai_calib_frame import pyfaiRingIcon
        super().__init__(parent)

        self.process = None
        if geometry and len(geometry) == 4:
            self.setGeometry(*geometry)
        else:
            self.setGeometry(40, 60, 1400, 1000)
        self.status = self.statusBar()

        self.frame_menuentries = []
        self.frame_meta = {}

        self.setCentralWidget(CENTRAL_WIDGET_STACK)
        self.status.showMessage('Test status')

        self.setWindowTitle('pyDIDAS layout prototype')
        self.setWindowIcon(pyfaiRingIcon())
        self.__createMenu()
        self.__create_info_box()
        self.setFocus(QtCore.Qt.OtherFocusReason)

    @staticmethod
    def __find_toolbar_bases(items):
        _menu = []
        for _item in items:
            _itembase = os.path.dirname(_item)
            if _itembase not in _menu:
                _menu.append(_itembase)
            _item = _itembase
        _menu.sort()
        return _menu

    @staticmethod
    def __find_all_own_bases(item):
        _r = []
        while len(item) > 0:
            _base = os.path.dirname(item)
            _r.append(_base)
            item = _base
        return _r[::-1]



    @staticmethod
    def __format_str_for_toolbar(input_str):
        _r = []
        _s = ''
        for s in [s for s in re.split(' |\n', input_str) if len(s) > 0]:
            if len(_s) + len(s) <= 11:
                _s = _s + f' {s}' if len(_s) > 0 else s
            else:
                _r.append(f'{_s}\n')
                _s = s
        # append last line
        if _s not in _r:
            _r.append(_s)
        return ''.join(_r).strip()



    def __create_info_box(self):
        _dock_widget = QtWidgets.QDockWidget('Logging & information')
        _dock_widget.setWidget(InfoWidget())
        _dock_widget.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFloatable)
        _dock_widget.setBaseSize(500, 50)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, _dock_widget)

    def create_toolbars(self):
        self._toolbars = {}
        for tb in self.__find_toolbar_bases(self.frame_menuentries):
            tb_title = tb if tb else 'Main toolbar'
            self._toolbars[tb] = QtWidgets.QToolBar(tb_title, self)
            self._toolbars[tb].setStyleSheet("QToolBar{spacing:20px;}")
            self._toolbars[tb].setIconSize(QtCore.QSize(40, 40))
            self._toolbars[tb].setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
            self._toolbars[tb].setFixedWidth(85)
            self._toolbars[tb].setMovable(False)
            self._toolbars[tb].toggleViewAction().setEnabled(False)

        for item in self.frame_menuentries:
            _icon = self.frame_meta[item]['icon']
            _name = self.frame_meta[item]['name']
            _action = QtWidgets.QAction(_icon, _name, self)
            _action.setStatusTip(_name)
            _action.triggered.connect(partial(self.select_item, item))
            itembase = os.path.dirname(item)
            self._toolbars[itembase].addAction(_action)

        for tb in self._toolbars:
            if tb == '':
                self.addToolBar(QtCore.Qt.LeftToolBarArea, self._toolbars[tb])
            else:
                self.addToolBarBreak(QtCore.Qt.LeftToolBarArea)
                self.addToolBar(QtCore.Qt.LeftToolBarArea, self._toolbars[tb])
                self._toolbars[tb].setVisible(False)
        self.select_item(self.frame_menuentries[0])
        CENTRAL_WIDGET_STACK.setCurrentIndex(0)

        # _toolbar = QtWidgets.QToolBar('Top toolbar')
        # _toolbar.setStyleSheet("QToolBar{spacing:20px;}")
        # _toolbar.setIconSize(QtCore.QSize(40, 40))
        # _toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        # _toolbar.setFixedHeight(30)
        # _toolbar.setMovable(False)
        # self.addToolBar(QtCore.Qt.TopToolBarArea, _toolbar)
        # self.top_toolbar_label = QtWidgets.QLabel(_toolbar)
        # self.top_toolbar_label

    @staticmethod
    def __get_active_toolbars(name):
        _r = [name]
        while len(name):
            name = os.path.dirname(name)
            _r.append(name)
        return _r[::-1]

    def register_frame(self, name, menu_name, menuicon, frame):
        if menu_name in self.frame_menuentries:
            raise FrameConfigError(f'The selected menu entry "{menu_name}"'
                                   ' already exists.')
        _frame = frame(mainWindow=self)
        _frame.name = menu_name
        _frame.setParent(self)
        _frame.status_msg.connect(self.update_status)
        if CENTRAL_WIDGET_STACK.is_registed(_frame):
            CENTRAL_WIDGET_STACK.change_reference_name(menu_name, _frame)
        else:
            CENTRAL_WIDGET_STACK.register_widget(menu_name, _frame)
        self.frame_menuentries.append(menu_name)
        _meta = dict(name=self.__format_str_for_toolbar(name),
                     icon=menuicon,
                     index=_frame.frame_index,
                     menus=self.__get_active_toolbars(menu_name))
        self.frame_meta[menu_name] = _meta

    def select_item(self, name):
        self.setUpdatesEnabled(False)
        CENTRAL_WIDGET_STACK.setUpdatesEnabled(False)
        _no_show_toolbars = (set(self._toolbars)
                             - set(self.frame_meta[name]['menus']))
        _show_toolbars = [_tb for _tb in self._toolbars
                          if _tb in self.frame_meta[name]['menus']]
        for _tb in _no_show_toolbars:
            self._toolbars[_tb].setVisible(False)
        for _tb in _show_toolbars:
            self._toolbars[_tb].setVisible(True)

        w = CENTRAL_WIDGET_STACK.get_widget_by_name(name)
        if w.layout() and w.layout().count() > 0:
            CENTRAL_WIDGET_STACK.setCurrentIndex(self.frame_meta[name]['index'])
        self.setUpdatesEnabled(True)
        CENTRAL_WIDGET_STACK.setUpdatesEnabled(True)

    def action_new(self):
        print('new')

    def action_open(self):
        print('open')

    @QtCore.pyqtSlot(str)
    def update_status(self, text):
        self.status.showMessage(text)

    def __createMenu(self):
        self._menu = self.menuBar()

        newAction = QtWidgets.QAction(QtGui.QIcon('new.png'),
                                      '&New processing workflow', self)
        # newAction.setShortcut('Ctrl+N')
        newAction.setStatusTip('Create a new processing workflow and discard'
                               ' the current workflow.')
        newAction.triggered.connect(self.action_new)

        openExp = QtWidgets.QAction(QtGui.QIcon('open.png'),
                                       'Open &experimental configuration', self)
        openExp.setShortcut('Ctrl+O')
        openExp.setStatusTip('Discard the current experimental configuration'
                             ' and open a configuration from file.')
        openExp.triggered.connect(self.action_open)

        openScan = QtWidgets.QAction(QtGui.QIcon('open.png'),
                                       'Open &scan configuration', self)
        openScan.setShortcut('Ctrl+O')
        openScan.setStatusTip('Discard the current scan settings'
                             ' and open a scan configuration from file.')
        openScan.triggered.connect(self.action_open)

        openTree = QtWidgets.QAction(QtGui.QIcon('open.png'),
                                       'Open &workflow tree', self)
        openTree.setShortcut('Ctrl+O')
        openTree.setStatusTip('Discard the current workflow tree'
                             ' and open a workflow tree from file..')
        openTree.triggered.connect(self.action_open)


        # Create exit action
        exitAction = QtWidgets.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        fileMenu = self._menu.addMenu('&File')
        fileMenu.addAction(newAction)
        openMenu = fileMenu.addMenu('&Open')
        openMenu.addAction(openExp)
        openMenu.addAction(openScan)
        openMenu.addAction(openTree)
        fileMenu.addAction(exitAction)

        self._menu.addMenu(fileMenu)
        self._menu.addMenu("&Edit")
        self._menu.addMenu("&Help")




if __name__ == '__main__':
    sys.excepthook = pwg.widgets.excepthook
    app = QtWidgets.QApplication(sys.argv)
    #app.setStyle('Fusion')

    # needs to be initialized after the app has been created.
    CENTRAL_WIDGET_STACK = pwg.widgets.CENTRAL_WIDGET_STACK()



    _font = app.font()
    _font.setPointSize(STANDARD_FONT_SIZE)
    app.setFont(_font)
    gui = LayoutTest()

    from plugin_workflow_gui.gui.pyfai_calib_frame import PyfaiCalibFrame, pyfaiCalibIcon
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
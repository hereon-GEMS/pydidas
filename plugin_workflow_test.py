# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 10:24:52 2021

@author: ogurreck
"""

import sys
import os
import re

from functools import partial

#from qtpy import QtWidgets, QtGui, QtCore
from PyQt5 import QtWidgets, QtGui, QtCore, Qt

import qtawesome as qta

import plugin_workflow_gui as pwg

WORKFLOW_EDIT_MANAGER = pwg.gui.WorkflowEditTreeManager()
PLUGIN_COLLECTION = pwg.PluginCollection()
STYLES = pwg.config.STYLES
PALETTES = pwg.config.PALETTES

from plugin_workflow_gui.widgets import WorkflowTreeCanvas, PluginCollectionPresenter, ScrollArea
from plugin_workflow_gui.widgets.plugin_config import PluginParamConfig
from plugin_workflow_gui.config import STANDARD_FONT_SIZE
import plugin_workflow_gui.config.gui_constants as gui_const
#WorkflowTree = pwg.WorkflowTree()


class FrameConfigError(Exception):
    ...




class WorkflowEditFrame(QtWidgets.QFrame):
    def __init__(self, parent=None, params=None):
        super().__init__(parent)
        self.parent = parent
        self.workflow_canvas = WorkflowTreeCanvas(self)
        self.plugin_edit_canvas = PluginParamConfig(self)
        self.w_plugin_collection = PluginCollectionPresenter(self)
        params = params if params else {}
        self.params = {}
        self.params['workflow_edit_canvas_x'] = params.get('workflow_edit_canvas_x', gui_const.WORKFLOW_EDIT_CANVAS_X)
        self.params['workflow_edit_canvas_y'] = params.get('workflow_edit_canvas_y', gui_const.WORKFLOW_EDIT_CANVAS_Y)
        self.workflow_area = ScrollArea(
            self, widget=self.workflow_canvas, minHeight=500)
        #     self.params['workflow_edit_canvas_x'],
        #     self.params['workflow_edit_canvas_y']
        # )
        self.plugin_edit_area = ScrollArea(self, widget=self.plugin_edit_canvas, fixedWidth=400, minHeight=500)
        #self.plugin_edit_area.setMinimumHeight(500)
        self.plugin_edit_area.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

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
        # _layout.addWidget(pwg.widgets.ConfirmationBar())
        self.setLayout(_layout)
        WORKFLOW_EDIT_MANAGER.update_qt_items(qt_canvas=self.workflow_canvas)
        WORKFLOW_EDIT_MANAGER.plugin_to_edit.connect(self.configure_plugin)

    def workflow_add_plugin(self, name):
        WORKFLOW_EDIT_MANAGER.add_plugin_node(name)

    @QtCore.pyqtSlot(int)
    def configure_plugin(self, node_id):
        self.plugin_edit_canvas.configure_plugin(node_id)





class _ToplevelFrame(QtWidgets.QFrame):
    def __init__(self, parent=None, name=None):
        super().__init__(parent)
        self.font = QtWidgets.QApplication.font()
        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.initialized = False
        self.name = name if name else ''
        # self.empty_frame
        if name:
            CENTRAL_WIDGET_PROXY.register_widget(self.name, self)
        if self.parent():
            self._initialize()
            self.initialized = True

    def set_parent(self, parent):
        self.setParent(parent)
        if self.parent() and not self.initialized:
            self._initialize()
            self.initialized = True

    def _initialize(self):
        ...

    def set_name(self, name):
        self.name = name
        if not CENTRAL_WIDGET_PROXY.is_registered(self.name, self):
            CENTRAL_WIDGET_PROXY.register_widget(name, self)
        else:
            CENTRAL_WIDGET_PROXY.change_reference_name(name, self)

    def _initialize(self):
        self.initialized = True

    def add_label(self, text, fontsize=STANDARD_FONT_SIZE, underline=False,
                  bold=False):
        _l = QtWidgets.QLabel(text)
        self.font.setPointSize(fontsize)
        self.font.setBold(bold)
        self.font.setUnderline(underline)
        _l.setFont(self.font)
        _l.setFixedWidth(400)
        _l.setWordWrap(True)
        self._layout.addWidget(_l)


class HomeFrame(_ToplevelFrame):
    def __init__(self, parent=None, name=None):
        super().__init__(parent, name)
        self.add_label('Welcome to pySALADD', 14, bold=True)
        self.add_label('\nQuickstart:', 12, bold=True)
        self.add_label('\nMenu: ', 11, underline=True, bold=True)
        self.add_label('Use the menu toolbar on the left to switch between'
                       ' different views. Some menu toolbars will open a'
                       'further submenu on the left.\nAll functions can'
                       ' also be accessed through the regular menu on top.')



class ProcessingSetupFrame(_ToplevelFrame):
    def __init__(self, parent=None, name=None):
        super().__init__(parent, name)

class DataBrowsingFrame(_ToplevelFrame):
    def __init__(self, parent=None, name=None):
        super().__init__(parent, name)


class ToolsFrame(_ToplevelFrame):
    def __init__(self, parent=None, name=None):
        super().__init__(parent, name)

class ProcessingFrame(_ToplevelFrame):
    def __init__(self, parent=None, name=None):
        super().__init__(parent, name)

class ResultVisualizationFrame(_ToplevelFrame):
    def __init__(self, parent=None, name=None):
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

class LayoutTest2(QtWidgets.QMainWindow):
    name_selected_signal = QtCore.pyqtSlot(str)

    def __init__(self, parent=None, geometry=None):
        super().__init__(parent)

        self.process = None
        if geometry and len(geometry) == 4:
            self.setGeometry(*geometry)
        else:
            self.setGeometry(40, 60, 1400, 1000)
        self.status = self.statusBar()

        self.frame_menuentries = []
        self.frame_meta = {}

        # self.params = {'active_frame': 'Home'}
        # self.main_frames = {'Home': HomeFrame(),
        #                     'Data browsing': DataBrowsingFrame(),
        #                     'Tools': ToolsFrame(),
        #                     'Processing setup': ProcessingSetupFrame(),
        #                     'Processing': ProcessingFrame(),
        #                     'Result visualization': ResultVisualizationFrame()}
        self.setCentralWidget(CENTRAL_WIDGET_PROXY)
        self.status.showMessage('Test status')
        #self.__create_main_toolbar()

        # for key in self.main_frames:
        #     self.main_frames[key].toggle(False)
        #     self.main_frames[key].set_parent(self)
        # self.experiment_edit_tab = ExperimentEditTab(self.main_frame)
        # self.workflow_edit_tab = WorkflowEditTab(self.main_frame, self.params)
        # self.main_frame.addTab(self.experiment_edit_tab, 'Experiment editor')
        # self.main_frame.addTab(self.workflow_edit_tab, 'Workflow editor')

        # WORKFLOW_EDIT_MANAGER.update_qt_items(
        #     self.workflow_edit_tab.workflow_canvas, self
        # )
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

        self.setWindowTitle('Plugin edit test')
        self.__createMenu()
        self.__create_info_box()


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
        CENTRAL_WIDGET_PROXY.setCurrentIndex(0)

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
        frame.name = menu_name
        frame.setParent(self)
        if CENTRAL_WIDGET_PROXY.is_registed(frame):
            CENTRAL_WIDGET_PROXY.change_reference_name(menu_name, frame)
        else:
            CENTRAL_WIDGET_PROXY.register_widget(menu_name, frame)
        self.frame_menuentries.append(menu_name)
        _meta = dict(name=self.__format_str_for_toolbar(name),
                     icon=menuicon,
                     index=frame.frame_index,
                     menus=self.__get_active_toolbars(menu_name))
        self.frame_meta[menu_name] = _meta


    def select_item(self, name):
        for _tb in self._toolbars:
            self._toolbars[_tb].setVisible(_tb in self.frame_meta[name]['menus'])


        w = CENTRAL_WIDGET_PROXY.get_widget_by_name(name)
        if w.layout() and w.layout().count() > 0:
            CENTRAL_WIDGET_PROXY.setCurrentIndex(self.frame_meta[name]['index'])


    def action_new(self):
        print('new')

    def action_open(self):
        print('open')

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
    CENTRAL_WIDGET_PROXY = pwg.widgets.CENTRAL_WIDGET_PROXY()


    _font = app.font()
    _font.setPointSize(STANDARD_FONT_SIZE)
    app.setFont(_font)
    gui = LayoutTest2()

    gui.register_frame('Home', 'Home', qta.icon('mdi.home'), HomeFrame())
    gui.register_frame('Data browsing', 'Data browsing', qta.icon('mdi.image-search-outline'), DataBrowsingFrame())
    gui.register_frame('Tools', 'Tools', qta.icon('mdi.tools'), ToolsFrame())
    gui.register_frame('Processing setup', 'Processing setup', qta.icon('mdi.cogs'), ProcessingSetupFrame())
    gui.register_frame('Processing', 'Processing', qta.icon('mdi.sync'), ProcessingFrame())
    gui.register_frame('Result visualization', 'Result visualization', qta.icon('mdi.monitor-eye'), ResultVisualizationFrame())
    gui.register_frame('Home 2', 'Processing/Home', qta.icon('mdi.home'), HomeFrame())
    gui.register_frame('Help', 'Processing/Home2', qta.icon('mdi.home'), HomeFrame())
    gui.register_frame('Help', 'Tools/help/Help', qta.icon('mdi.home'), HomeFrame())
    gui.register_frame('Workflow editing', 'Processing setup/Workflow editing', qta.icon('mdi.clipboard-flow-outline'), WorkflowEditFrame())
    gui.register_frame('Help', 'Tools/help/Help 2', qta.icon('mdi.home'), HomeFrame())
    gui.register_frame('Help', 'Tools/help', qta.icon('mdi.home'), QtWidgets.QFrame())
    gui.create_toolbars()

    gui.show()
    sys.exit(app.exec_())

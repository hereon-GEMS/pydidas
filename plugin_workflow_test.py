# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 10:24:52 2021

@author: ogurreck
"""

import sys
import os
import re
#from qtpy import QtWidgets, QtGui, QtCore
from PyQt5 import QtWidgets, QtGui, QtCore, Qt
from functools import partial

import plugin_workflow_gui as pwg

WORKFLOW_EDIT_MANAGER = pwg.gui.WorkflowEditTreeManager()
PLUGIN_COLLECTION = pwg.PluginCollection()
STYLES = pwg.config.STYLES
PALETTES = pwg.config.PALETTES

from plugin_workflow_gui.widgets import WorkflowTreeCanvas, PluginCollectionPresenter, ScrollArea
from plugin_workflow_gui.widgets.plugin_config import PluginParamConfig
from plugin_workflow_gui.config import STANDARD_FONT_SIZE
#WorkflowTree = pwg.WorkflowTree()

import qtawesome as qta

class FrameConfigError(Exception):
    ...




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




class MainTabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

class _ToplevelFrame(QtWidgets.QFrame):
    def __init__(self, parent=None, name=None):
        super().__init__(parent)
        self.parent = parent
        self.menu_bar = None
        self.active = False
        self.initialized = False
        self._actions = []
        self.name = name if name else ''
        if name:
            CENTRAL_WIDGET_PROXY.register_widget(self.name, self)
        if self.parent:
            self._initialize()

    def set_parent(self, parent):
        self.parent = parent
        if self.parent and not self.initialized:
            self._initialize()

    def set_name(self, name):
        self.name = name
        if not CENTRAL_WIDGET_PROXY.is_registered(self.name, self):
            CENTRAL_WIDGET_PROXY.register_widget(name, self)
        else:
            CENTRAL_WIDGET_PROXY.change_reference_name(name, self)


    def _initialize(self):
        self.menu_bar = QtWidgets.QToolBar(self)

        for icon, name in self._actions:
            _action = QtWidgets.QAction(icon, name.replace(' ', '\n'), self)
            _action.setStatusTip(name)
            _action.triggered.connect(partial(self.select_item, name))
            self.menu_bar.addAction(_action)

        self.menu_bar.setStyleSheet("QToolBar{spacing:20px;}");
        self.menu_bar.setIconSize(QtCore.QSize(40, 40))
        self.menu_bar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.menu_bar.setFixedWidth(80)
        self.menu_bar.setMovable(False)
        self.menu_bar.toggleViewAction().setChecked(False)
        self.menu_bar.toggleViewAction().trigger()
        self.initialized = True

    def toggle(self, value=None):
        if value is not None:
            self.active = value
        else:
            self.active = not self.active
        if self.menu_bar:
            self.menu_bar.toggleViewAction().trigger()

    def select_item(self, name):
        raise NotImplementedError

class HomeFrame(_ToplevelFrame):
    def __init__(self, parent=None, name=None):
        super().__init__(parent, name)
        self._initialize()

    def _initialize(self):
        self.initialized = True
        self.font = QtWidgets.QApplication.font()
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        self.add_label('Welcome to pySALADD', 14, bold=True)
        self.add_label('\nQuickstart:', 12, bold=True)
        self.add_label('\nMenu: ', 11, underline=True, bold=True)
        self.add_label('Use the menu toolbar on the left to switch between'
                       ' different views. Some menu toolbars will open a'
                       'further submenu on the left.\nAll functions can'
                       'also be accessed through the regular menu on top.')

    def add_label(self, text, fontsize=STANDARD_FONT_SIZE, underline=False,
                  bold=False):
        _l = QtWidgets.QLabel(text)
        self.font.setPointSize(fontsize)
        self.font.setBold(bold)
        self.font.setUnderline(underline)
        _l.setFont(self.font)
        _l.setFixedWidth(400)
        _l.setWordWrap(True)
        self.layout.addWidget(_l)


class ProcessingSetupFrame(_ToplevelFrame):
    def __init__(self, parent=None, name=None):
        super().__init__(parent, name)
        self._actions = [[qta.icon('mdi.flask', color='blue'), 'Experiment'],
                         [qta.icon('mdi.axis-arrow'), 'Scan'],
                         [qta.icon('mdi.clipboard-flow-outline'), 'Workflow']
                         ]

    def select_item(self, name):
        print(name)

class DataBrowsingFrame(_ToplevelFrame):
    def __init__(self, parent=None, name=None):
        super().__init__(parent, name)

    def select_item(self, name):
        print(name)

class ToolsFrame(_ToplevelFrame):
    def __init__(self, parent=None, name=None):
        super().__init__(parent, name)
        self._actions = [[qta.icon('mdi.flask', color='blue'), 'Experiment'],
                         [qta.icon('mdi.axis-arrow'), 'Scan'],
                         [qta.icon('mdi.clipboard-flow-outline'), 'Workflow']
                         ]

    def select_item(self, name):
        print(name)

class ProcessingFrame(_ToplevelFrame):
    def __init__(self, parent=None, name=None):
        super().__init__(parent, name)
        self._actions = [[qta.icon('mdi.flask', color='blue'), 'Experiment'],
                         [qta.icon('mdi.axis-arrow'), 'Scan'],
                         [qta.icon('mdi.clipboard-flow-outline'), 'Workflow']
                         ]

    def select_item(self, name):
        print(name)

class ResultVisualizationFrame(_ToplevelFrame):
    def __init__(self, parent=None, name=None):
        super().__init__(parent, name)
        self._actions = [[qta.icon('mdi.flask', color='blue'), 'Experiment'],
                         [qta.icon('mdi.axis-arrow'), 'Scan'],
                         [qta.icon('mdi.clipboard-flow-outline'), 'Workflow']
                         ]

    def select_item(self, name):
        print(name)



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

    def __init__(self, parent=None):
        super().__init__(parent)

        self.process = None
        self.setGeometry(20, 40, 1400, 1000)
        self.params = {'workflow_edit_canvas_x': 1000,
                       'workflow_edit_canvas_y': 600}
        self.status = self.statusBar()
        self._refs = {}

        self.frame_menuentries = []
        self.frame_names= {}
        self.frame_refs= {}
        self.frame_icons = {}

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

    def __update_toolbar(self):

        menu = ['Home', 'Tools', 'Proc setup', 'Proc setup/Workflow', 'Proc setup/Exp', 'Proc setup/Scan', 'Proc setup/Exp/Generic']
        menuitems = [item.split('/') for item in menu]

        # _menu = QtWidgets.QToolBar(self)
        # _action = None

        # _groups = [[[qta.icon('mdi.home'), 'Home']],
        #            [[qta.icon('mdi.image-search-outline'), 'Data browsing']],
        #            [[qta.icon('mdi.tools'), 'Tools']],
        #            [[qta.icon('mdi.cogs'), 'Processing setup'],
        #             [qta.icon('fa5s.sync'), 'Processing'],
        #             [qta.icon('mdi.monitor-eye'), 'Result visualization']]
        #            ]

        # for i, group in enumerate(_groups):
        #     _newgroup = True
        #     for icon, name in group:
        #         _action = QtWidgets.QAction(icon, name.replace(' ', '\n'), self)
        #         _action.setStatusTip(name)
        #         _action.triggered.connect(partial(self.select_item, name))
        #         _menu.addAction(_action)
        #         if _newgroup and i > 0:
        #             _menu.insertSeparator(_action)
        #         _newgroup = False

        # _menu.setStyleSheet("QToolBar{spacing:20px;}");
        # _menu.setIconSize(QtCore.QSize(40, 40))
        # _menu.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        # _menu.setFixedWidth(80)
        # _menu.setMovable(False)
        # self._refs['main_toolbar'] = _menu
        # self.addToolBar(QtCore.Qt.LeftToolBarArea, _menu)

        # for icon, name in self._actions:
        #     _action = QtWidgets.QAction(icon, name.replace(' ', '\n'), self)
        #     _action.setStatusTip(name)
        #     _action.triggered.connect(partial(self.select_item, name))
        #     self.menu_bar.addAction(_action)

        # self.menu_bar.setStyleSheet("QToolBar{spacing:20px;}");
        # self.menu_bar.setIconSize(QtCore.QSize(40, 40))
        # self.menu_bar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        # self.menu_bar.setFixedWidth(80)
        # self.menu_bar.setMovable(False)
        # self.menu_bar.toggleViewAction().setChecked(False)
        # self.menu_bar.toggleViewAction().trigger()
        # self.initialized = True


    def __find_toolbar_bases(self):
        _menu = []
        for item in self.frame_menuentries:
            itembase = os.path.dirname(item)
            if itembase not in _menu:
                _menu.append(itembase)
        return _menu

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
        for tb in self.__find_toolbar_bases():
            self._toolbars[tb] = QtWidgets.QToolBar(self)
            self._toolbars[tb].setStyleSheet("QToolBar{spacing:20px;}");
            self._toolbars[tb].setIconSize(QtCore.QSize(40, 40))
            self._toolbars[tb].setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
            self._toolbars[tb].setFixedWidth(80)
            self._toolbars[tb].setMovable(False)
            self._toolbars[tb].toggleViewAction().setChecked(False)
            self._toolbars[tb].toggleViewAction().trigger()

        for item in self.frame_menuentries:
            _icon = self.frame_icons[item]
            _name = self.frame_names[item]
            _action = QtWidgets.QAction(_icon, _name, self)
            _action.setStatusTip(_name)
            _action.triggered.connect(partial(self.select_item, item))
            itembase = os.path.dirname(item)
            self._toolbars[itembase].addAction(_action)

        for tb in self._toolbars:
            if tb == '':
                self._toolbars[tb].toggleViewAction().setChecked(True)
                self.addToolBar(QtCore.Qt.LeftToolBarArea, self._toolbars[tb])
            else:
                self.addToolBarBreak(QtCore.Qt.LeftToolBarArea)
                self.addToolBar(QtCore.Qt.LeftToolBarArea, self._toolbars[tb])
                self._toolbars[tb].toggleViewAction().trigger()
        self.select_item(self.frame_menuentries[0])
        CENTRAL_WIDGET_PROXY.setCurrentIndex(0)




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
        self.frame_names[menu_name] = self.__format_str_for_toolbar(name)
        self.frame_icons[menu_name] = menuicon
        self.frame_refs[menu_name] = frame.frame_index


    def select_item(self, name):
        print(name)
        CENTRAL_WIDGET_PROXY.setCurrentIndex(self.frame_refs[name])
        print(CENTRAL_WIDGET_PROXY.currentWidget())

        # if name != self.params['active_frame']:
        #     current_frame = self.main_frames[self.params['active_frame']]
        #     print(name, current_frame, current_frame.menu_bar)
        #     if current_frame.menu_bar:
        #         self.removeToolBar(current_frame.menu_bar)
        # CENTRAL_WIDGET_PROXY.activate_widget_by_name(name)
        # for key in self.main_frames:
        #     item = self.main_frames[key]
        #     if item.name == name:

        #         item.toggle(True)
        #         self.addToolBarBreak(QtCore.Qt.LeftToolBarArea)
        #         self.addToolBar(QtCore.Qt.LeftToolBarArea, item.menu_bar)
        #     else:
        #         item.toggle(False)
        # self.params['active_frame'] = name



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
    print(CENTRAL_WIDGET_PROXY.get_all_widget_names())
    gui.register_frame('Data browsing', 'Data browsing', qta.icon('mdi.image-search-outline'), DataBrowsingFrame())
    gui.register_frame('Tools', 'Tools', qta.icon('mdi.tools'), ToolsFrame())
    gui.register_frame('Processing setup', 'Processing setup', qta.icon('mdi.cogs'), ProcessingSetupFrame())
    gui.register_frame('Processing', 'Processing', qta.icon('mdi.sync'), ProcessingFrame())
    gui.register_frame('Result visualization', 'Result visualization', qta.icon('mdi.monitor-eye'), ResultVisualizationFrame())
    gui.register_frame('Home 2', 'Processing/Home', qta.icon('mdi.home'), HomeFrame())
    gui.register_frame('Help', 'Processing/Home2', qta.icon('mdi.home'), HomeFrame())
    gui.register_frame('Help', 'Tools/Help', qta.icon('mdi.home'), HomeFrame())
    gui.register_frame('Help', 'Tools/Help 2', qta.icon('mdi.home'), HomeFrame())
    gui.create_toolbars()

    gui.show()
    sys.exit(app.exec_())

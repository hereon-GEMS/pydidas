# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Module with the WorkflowPluginWidget which is used to create the workflow
tree."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['MainWindow']

import os
import re
from functools import partial

import qtawesome as qta
from PyQt5 import QtWidgets, QtGui, QtCore

from pydidas.widgets import CentralWidgetStack, GetInfoWidget
from pydidas.core import get_generic_parameter
from pydidas._exceptions import FrameConfigError
from pydidas.gui.global_configuration_frame import GlobalConfigurationFrame
from pydidas.config import QSETTINGS_GLOBAL_KEYS
from pydidas.workflow_tree import WorkflowTree

TREE = WorkflowTree()
TREE.clear()


class MainWindow(QtWidgets.QMainWindow):
    """
    Inherits from :py:class:`PyQt5.QtWidgets.QMainWindow`.

    The MainWindow is used to organize frames and for managing the menu
    and global application parameters.
    """
    def __init__(self, parent=None, geometry=None):
        from pydidas.gui.pyfai_calib_frame import pyfaiRingIcon
        super().__init__(parent)

        self.process = None
        if geometry and len(geometry) == 4:
            self.setGeometry(*geometry)
        else:
            self.setGeometry(40, 60, 1400, 1000)
        self.status = self.statusBar()

        self.frame_menuentries = []
        self.frame_meta = {}
        self.windows = {}

        self.setCentralWidget(CentralWidgetStack())
        self.status.showMessage('Test status')

        self.setWindowTitle('pydidas GUI (alpha)')
        self.setWindowIcon(pyfaiRingIcon())
        self.__createMenu()
        self.__create_info_box()
        self.setFocus(QtCore.Qt.OtherFocusReason)

        app = QtWidgets.QApplication.instance()
        app.setOrganizationName("Hereon")
        app.setOrganizationDomain("Hereon/WPI")
        app.setApplicationName("pydidas")
        self.__create_qsettings_if_required()
        self.__add_documentation_window()

    def __add_global_config_window(self):
        """
        Add the required widgets and signals for the global configuration.
        """
        from ..widgets.windows import GlobalConfigWindow
        self.register_frame('Global configuration', 'Global configuration',
                            qta.icon('mdi.application-cog'),
                            GlobalConfigurationFrame)

        _w = CentralWidgetStack().get_widget_by_name('Global configuration')
        self.windows['global_config'] = GlobalConfigWindow(self)
        _w2 = self.windows['global_config'].centralWidget()
        _w.value_changed_signal.connect(_w2.external_update)
        _w2.value_changed_signal.connect(_w.external_update)

    def __add_documentation_window(self):
        from ..widgets.windows import GlobalDocumentationWindow
        self.windows['documentation'] = GlobalDocumentationWindow(self)

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

    def __create_qsettings_if_required(self):
        settings = QtCore.QSettings()
        for key in QSETTINGS_GLOBAL_KEYS:
            _val = settings.value(f'global/{key}')
            if _val is None:
                _param = get_generic_parameter(key)
                settings.setValue(f'global/{key}', _param.default)

    def __create_info_box(self):
        self.__info_widget = GetInfoWidget()
        _dock_widget = QtWidgets.QDockWidget('Logging && information')
        _dock_widget.setWidget(self.__info_widget)
        _dock_widget.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFloatable)
        _dock_widget.setBaseSize(500, 50)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, _dock_widget)

    def create_toolbars(self):
        self.__add_global_config_window()
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
        self.centralWidget().setCurrentIndex(0)

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
        if self.centralWidget().is_registered(_frame):
            self.centralWidget().change_reference_name(menu_name, _frame)
        else:
            self.centralWidget().register_widget(menu_name, _frame)
        self.frame_menuentries.append(menu_name)
        _meta = dict(name=self.__format_str_for_toolbar(name),
                     icon=menuicon,
                     index=_frame.frame_index,
                     menus=self.__get_active_toolbars(menu_name))
        self.frame_meta[menu_name] = _meta

    def select_item(self, name):
        self.setUpdatesEnabled(False)
        self.centralWidget().setUpdatesEnabled(False)
        _no_show_toolbars = (set(self._toolbars)
                             - set(self.frame_meta[name]['menus']))
        _show_toolbars = [_tb for _tb in self._toolbars
                          if _tb in self.frame_meta[name]['menus']]
        for _tb in _no_show_toolbars:
            self._toolbars[_tb].setVisible(False)
        for _tb in _show_toolbars:
            self._toolbars[_tb].setVisible(True)

        w = self.centralWidget().get_widget_by_name(name)
        if w.layout() and w.layout().count() > 0:
            self.centralWidget().setCurrentIndex(self.frame_meta[name]['index'])
        self.setUpdatesEnabled(True)
        self.centralWidget().setUpdatesEnabled(True)

    def action_new(self):
        print('new')

    def action_open(self):
        print('open')

    def show_window(self, name):
        """
        Show a separate window.

        Parameters
        ----------
        name : str
            The name key of the window to be shown.
        """
        self.windows[name].show()

    def __action_open_doc_in_browser(self):
        """
        Open the link to the documentation in the system web browser.
        """
        from ..widgets.windows import get_doc_qurl
        QtGui.QDesktopServices.openUrl(get_doc_qurl())

    def closeEvent(self, event):
        for window in self.windows:
            self.windows[window].close()
        event.accept()

    @QtCore.pyqtSlot(str)
    def update_status(self, text):
        self.status.showMessage(text)
        self.__info_widget.add_status(text)

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

        extrasMenu = self._menu.addMenu('&Extras')
        settingsAction = QtWidgets.QAction('&Settings', self)
        settingsAction.triggered.connect(partial(self.show_window,
                                                 'global_config'))
        extrasMenu.addAction(settingsAction)

        helpMenu = self._menu.addMenu('&Help')
        documentation_action = QtWidgets.QAction('Open documentation in '
                                                'window', self)
        documentation_action.triggered.connect(partial(self.show_window,
                                                      'documentation'))
        doc_in_browser_action = QtWidgets.QAction('Open documentation in '
                                                  'web browser', self)
        doc_in_browser_action.triggered.connect(
            self.__action_open_doc_in_browser)
        helpMenu.addAction(documentation_action)
        helpMenu.addAction(doc_in_browser_action)


        self._menu.addMenu(fileMenu)
        self._menu.addMenu(extrasMenu)
        self._menu.addMenu(helpMenu)

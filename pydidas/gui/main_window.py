# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the MainWindow class which is a subclassed QMainWindow which has
been modified for pydidas's requirements and which manages the option and
selection bars.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['MainWindow']

import os
import sys
from pathlib import Path
from functools import partial

from qtpy import QtWidgets, QtGui, QtCore

from ..core import FrameConfigError
from ..core.utils import format_input_to_multiline_str, get_doc_home_qurl
from ..core.constants import STANDARD_FONT_SIZE
from ..widgets import (CentralWidgetStack, InfoWidget, excepthook,
                       get_pyqt_icon_from_str_reference)
from .global_configuration_frame import GlobalConfigurationFrame
from .windows import GlobalDocumentationWindow, GlobalConfigWindow
from .utils import QTooltipEventFilter


def _configure_qtapp_namespace():
    """
    Set the QApplication organization and application names.
    """
    app = QtWidgets.QApplication.instance()
    app.setOrganizationName("Hereon")
    app.setOrganizationDomain("Hereon/WPI")
    app.setApplicationName("pydidas")


def _get_pydidas_icon():
    """
    Get the pydidas icon.

    Returns
    -------
    _icon : QtGui.QIcon
        The instantiated pydidas icon.
    """
    _path = __file__
    for _ in range(2):
        _path = os.path.dirname(_path)
    _logopath = os.path.join(_path, 'pydidas_logo.svg')
    _icon= QtGui.QIcon(_logopath)
    return _icon


def _find_toolbar_bases(items):
    """
    Find the bases of all toolbar items which are not included in the items
    itself.

    Base levels in items are separated by forward slashes.

    Parameters
    ----------
    items : Union[list, tuple]
        An iterable of string items.

    Example
    -------
    >>> items = ['a', 'a/b', 'a/c', 'b', 'd/e']
    >>> _find_toolbar_bases(items)
    ['', 'a', 'd']

    The '' entry is the root for all top-level items. Even though 'a' is an
    item itself, it is also a parent for 'a/b' and 'a/c' and it is therefore
    also included in the list, similar to 'd'.

    Returns
    -------
    itembases : list
        A list with string entries of all the items' parents.
    """
    _itembases = []
    for _item in items:
        _parent = os.path.dirname(_item)
        if _parent not in _itembases:
            _itembases.append(_parent)
        _item = _parent
    _itembases.sort()
    return _itembases


def _update_qtapp_font_size():
    """
    Update the standard fonz size in the QApplication with the font size
    defined in pydidas.
    """
    _app = QtWidgets.QApplication.instance()
    _font = _app.font()
    _font.setPointSize(STANDARD_FONT_SIZE)
    _app.setFont(_font)


def _apply_tooltop_event_filter():
    """
    Apply the pydidas.core.utils.QTooltipEventFilter to the QApplication
    to force the desired handling of tooltip.
    """
    _app = QtWidgets.QApplication.instance()
    _app.installEventFilter(QTooltipEventFilter(_app))


class MainWindow(QtWidgets.QMainWindow):
    """
    Inherits from :py:class:`qtpy.QtWidgets.QMainWindow`.

    The MainWindow is used to organize frames and for managing the menu
    and global application parameters.

    Parameters
    ----------
    parent : QtWidgets.QWidget, optional
        The widget's parent. The default is None.
    geometry : Union[tuple, list, None], optional
        The geometry as a 4-tuple or list. The entries are the top left
        corner coordinates (x0, y0) and width and height. If None, the
        default values will be used. The default is None.
    """

    def __init__(self, parent=None, geometry=None):
        super().__init__(parent)
        _configure_qtapp_namespace()
        _update_qtapp_font_size()
        _apply_tooltop_event_filter()
        sys.excepthook = excepthook

        self._frame_menuentries = []
        self._frame_meta = {}
        self._child_windows = {}
        self._actions = {}
        self._toolbars = {}
        self._toolbar_actions = {}
        self._toolbars_created = False

        self.__setup_mainwindow_widget(geometry)

        self.__create_menu()
        self.__create_logging_info_box()
        self.__add_documentation_window()

    def __setup_mainwindow_widget(self, geometry):
        """
        Setup the user interface.

        Parameters
        ----------
        geometry : Union[tuple, list, None], optional
            The geometry as a 4-tuple or list. The entries are the top left
            corner coordinates (x0, y0) and width and height. If None, the
            default values will be used. The default is None.
        """
        if isinstance(geometry, (tuple, list)) and len(geometry) == 4:
            self.setGeometry(*geometry)
        else:
            self.setGeometry(40, 60, 1400, 1000)
        self.setCentralWidget(CentralWidgetStack())
        self.statusBar().showMessage('pydidas started')
        self.setWindowTitle('pydidas GUI (alpha)')
        self.setWindowIcon(_get_pydidas_icon())
        self.setFocus(QtCore.Qt.OtherFocusReason)

    def __create_menu(self):
        """
        Create the application's main menu.
        """
        self.__create_menu_actions()
        self.__connect_menu_actions()
        self.__add_actions_to_menu()

    def __create_menu_actions(self):
        """
        Create all required actions for the menu entries and store them in the
        internal _actions dictionary.
        """
        # new_workflow_action = QtWidgets.QAction(
        #     QtGui.QIcon('new.png'), '&New processing workflow', self)
        # new_workflow_action.setStatusTip(
        #     'Create a new processing workflow and discard the current '
        #     'workflow.')
        # # new_workflow_action.setShortcut('Ctrl+N')
        # self._actions['new_workflow'] = new_workflow_action

        # load_exp_setup_action = QtWidgets.QAction(
        #     QtGui.QIcon('open.png'), 'Load &experimental configuration', self)
        # load_exp_setup_action.setStatusTip(
        #     'Discard the current experimental setup and open a configuration '
        #     'from file.')
        # self._actions['load_exp_setup'] = load_exp_setup_action

        # load_scan_setup_action = QtWidgets.QAction(
        #     QtGui.QIcon('open.png'), 'Load &scan configuration', self)
        # load_scan_setup_action.setStatusTip(
        #     'Discard the current scan setup and open a scan configuration '
        #     'from file.')
        # self._actions['load_scan_setup'] = load_scan_setup_action

        # load_workflow_tree_action = QtWidgets.QAction(
        #     QtGui.QIcon('open.png'), 'Load &workflow tree', self)
        # load_workflow_tree_action.setStatusTip(
        #     'Discard the current workflow tree and open a workflow tree '
        #     'from file.')
        # self._actions['load_workflow_tree'] = load_workflow_tree_action

        exit_action = QtWidgets.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        self._actions['exit'] = exit_action

        self._actions['open_settings'] = QtWidgets.QAction('&Settings', self)

        self._actions['open_documentation_window'] = QtWidgets.QAction(
            'Open documentation in separate window', self)

        self._actions['open_documentation_browser'] = QtWidgets.QAction(
            'Open documentation in default web browser', self)

    def __connect_menu_actions(self):
        """
        Connect all menu actions to their respective slots.
        """
        # self._actions['new_workflow'].triggered.connect(
        #     self._action_new_workflow)
        # self._actions['load_workflow_tree'].triggered.connect(
        #     self._action_load_workflow_tree)
        # self._actions['load_exp_setup'].triggered.connect(
        #     self._action_load_exp_setup)
        # self._actions['load_scan_setup'].triggered.connect(
        #     self._action_load_scan_setup)
        self._actions['exit'].triggered.connect(self.close)
        self._actions['open_settings'].triggered.connect(
            partial(self.show_window, 'global_config'))
        self._actions['open_documentation_window'].triggered.connect(
            partial(self.show_window, 'documentation'))
        self._actions['open_documentation_browser'].triggered.connect(
            self._action_open_doc_in_browser)

    def __add_actions_to_menu(self):
        """
        Add the defined actions to the menu bar.
        """
        _menu = self.menuBar()

        # _open_menu = QtWidgets.QMenu('&Open', self)
        # _open_menu.addAction(self._actions['load_exp_setup'])
        # _open_menu.addAction(self._actions['load_scan_setup'])
        # _open_menu.addAction(self._actions['load_workflow_tree'])

        _file_menu = _menu.addMenu('&File')
        # _file_menu.addAction(self._actions['new_workflow'])
        # _file_menu.addMenu(_open_menu)
        _file_menu.addAction(self._actions['exit'])
        _menu.addMenu(_file_menu)

        _extras_menu = _menu.addMenu('&Extras')
        _extras_menu.addAction(self._actions['open_settings'])
        _menu.addMenu(_extras_menu)

        _help_menu = _menu.addMenu('&Help')
        _help_menu.addAction(self._actions['open_documentation_window'])
        _help_menu.addAction(self._actions['open_documentation_browser'])
        _menu.addMenu(_help_menu)

    @QtCore.Slot()
    def _action_new_workflow(self):
        print('New workflow')

    @QtCore.Slot()
    def _action_load_workflow_tree(self):
        print('load workflow')

    @QtCore.Slot()
    def _action_load_exp_setup(self):
        print('load exp setup')

    @QtCore.Slot()
    def _action_load_scan_setup(self):
        print('load scan setup')

    @QtCore.Slot()
    def _action_open_doc_in_browser(self):
        """
        Open the link to the documentation in the system web browser.
        """
        QtGui.QDesktopServices.openUrl(get_doc_home_qurl())

    def __create_logging_info_box(self):
        """
        Create the InfoWidget for logging and status messages.
        """
        self.__info_widget = InfoWidget()
        _dock_widget = QtWidgets.QDockWidget('Logging && information')
        _dock_widget.setWidget(self.__info_widget)
        _dock_widget.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable
            | QtWidgets.QDockWidget.DockWidgetFloatable)
        _dock_widget.setBaseSize(500, 50)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, _dock_widget)

    def __add_documentation_window(self):
        """
        Add the floating documentation window to the main window.
        """
        self._child_windows['documentation'] = GlobalDocumentationWindow(self)

    def create_toolbars(self):
        """
        Create the toolbars to select between different widgets in the
        centralWidget.
        """
        self.__add_global_config_window()
        self._toolbars = {}
        for tb in _find_toolbar_bases(self._frame_menuentries):
            tb_title = tb if tb else 'Main toolbar'
            self._toolbars[tb] = QtWidgets.QToolBar(tb_title, self)
            self._toolbars[tb].setStyleSheet("QToolBar{spacing:20px;}")
            self._toolbars[tb].setIconSize(QtCore.QSize(40, 40))
            self._toolbars[tb].setToolButtonStyle(
                QtCore.Qt.ToolButtonTextUnderIcon)
            self._toolbars[tb].setFixedWidth(85)
            self._toolbars[tb].setMovable(False)
            self._toolbars[tb].toggleViewAction().setEnabled(False)

        for item in self._frame_menuentries:
            _icon = self._frame_meta[item]['icon']
            _label = self._frame_meta[item]['label']
            _action = QtWidgets.QAction(_icon, _label, self)
            _action.setCheckable(True)
            _action.triggered.connect(partial(self.select_item, item))
            self._toolbar_actions[item] = _action
            itembase = os.path.dirname(item)
            self._toolbars[itembase].addAction(_action)

        for _toolbar_name in self._toolbars:
            if _toolbar_name != '':
                self.addToolBarBreak(QtCore.Qt.LeftToolBarArea)
            self.addToolBar(QtCore.Qt.LeftToolBarArea,
                            self._toolbars[_toolbar_name])
            # only make the root toolbar visible to start with:
            self._toolbars[_toolbar_name].setVisible(_toolbar_name == '')
        self.select_item(self._frame_menuentries[0])
        self._toolbars_created = True

    def __add_global_config_window(self):
        """
        Add the required widgets and signals for the global configuration
        window and create it.
        """
        self.register_frame(GlobalConfigurationFrame, 'Global configuration',
                            'Global configuration', 'qta::mdi.application-cog')
        _w = CentralWidgetStack().get_widget_by_name('Global configuration')
        self._child_windows['global_config'] = GlobalConfigWindow(self)
        _w2 = self._child_windows['global_config'].centralWidget()
        _w.value_changed_signal.connect(_w2.external_update)
        _w2.value_changed_signal.connect(_w.external_update)

    def show(self):
        """
        Insert a create_toolbars method call into the show method if the
        toolbars have not been created at the time of the show call.
        """
        if not self._toolbars_created:
            self.create_toolbars()
        super().show()

    def register_frame(self, frame, title, menu_entry, menuicon=None):
        """
        Register a frame class with the MainWindow and add it to the
        CentralWidgetStack.

        This method takes a :py:class:`BaseFrame <pydidas.widgets.BaseFrame>`
        and creates an instance which is registeres with the
        CentralWidgetStack. It also stores the required metadata to create
        a actionbar link to open the frame.

        Parameters
        ----------
        frame : pydidas.widgets.BaseFrame
            The class of the Frame. This must be a subclass of BaseFrame.
        title : str
            The frame's title.
        menu_entry : str
            The path to the menu entry for the frame. Hierachical levels are
            separated by a '/' item.
        menuicon : Union[str, QtGui.QIcon, None], optional
            The menuicon. If None, this defaults to the menu icon specified
            in the frame's class. If a string is supplied, this is interpreted
            as a reference for a QIcon. For the refernce on string conversion,
            please check
            :py:func:`pydidas.widgets.get_pyqt_icon_from_str_reference`.

        Raises
        ------
        FrameConfigError
            If a similar menu entry has already been registered.
        """
        if menu_entry in self._frame_menuentries:
            raise FrameConfigError(f'The selected menu entry "{menu_entry}"'
                                   ' already exists.')
        _frame = frame()
        _frame.ref_name = menu_entry
        _frame.title = title
        if menuicon is not None:
            _frame.menuicon = menuicon
        _frame.status_msg.connect(self.update_status)
        if self.centralWidget().is_registered(_frame):
            self.centralWidget().change_reference_name(menu_entry, _frame)
        else:
            self.centralWidget().register_widget(menu_entry, _frame)
        self._store_frame_metadata(_frame, menuicon)

    def _store_frame_metadata(self, frame, menuicon):
        """
        Store the frame metadata in the internal dictionaries for reference.

        Parameters
        ----------
        frame : pydidas.widgets.BaseFrame
            The instantiated frame
        menuicon : Union[str, QtGui.QIcon]
            The menuicon, either as a QIcon or as a string reference for a
            menu icon.
        """
        _ref = frame.ref_name
        _new_menus = ([('' if _path == Path() else _path.as_posix())
                       for _path in reversed(Path(_ref).parents)] + [_ref])
        self._frame_menuentries.append(_ref)
        if isinstance(menuicon, str):
            menuicon = get_pyqt_icon_from_str_reference(menuicon)
        self._frame_meta[_ref] = dict(
            label=format_input_to_multiline_str(frame.title),
            icon=menuicon,
            index=frame.frame_index,
            menus=_new_menus)

    @QtCore.Slot(str)
    def select_item(self, label):
        """
        Select an item from the left toolbar and select the corresponding
        frame in the centralWidget.

        Parameters
        ----------
        label : str
            The label of the selected item.
        """
        self.setUpdatesEnabled(False)
        self.centralWidget().setUpdatesEnabled(False)
        for _name, _toolbar in self._toolbars.items():
            _toolbar.setVisible(_name in self._frame_meta[label]['menus'])
        _new_widget = self.centralWidget().get_widget_by_name(label)
        if _new_widget.show_frame:
            for _name, _action in self._toolbar_actions.items():
                _action.setChecked(_name in self._frame_meta[label]['menus']
                                   or _name == label)
            self.centralWidget().setCurrentIndex(
                self._frame_meta[label]['index'])
        else:
            self._toolbar_actions[label].setChecked(False)
        self.setUpdatesEnabled(True)
        self.centralWidget().setUpdatesEnabled(True)

    def closeEvent(self, event):
        """
        Handle the Qt closeEvent.

        This method adds calls to the child windows to close themselves.

        Parameters
        ----------
        event : QtCore.QEvent
            The closing event.
        """
        for window in self._child_windows:
            self._child_windows[window].deleteLater()
            self._child_windows[window].close()
        event.accept()

    @QtCore.Slot(str)
    def update_status(self, text):
        """
        Get a text message and show it in the global status widget.

        This slot can be used by any QObject to send an update which will be
        added to the global list of status messages.

        Parameters
        ----------
        text : str
            The status message.
        """
        self.statusBar().showMessage(text)
        if text[-1] != '\n':
            text += '\n'

        self.__info_widget.add_status(text)

    @QtCore.Slot(str)
    def show_window(self, name):
        """
        Show a separate window.

        Parameters
        ----------
        name : str
            The name key of the window to be shown.
        """
        self._child_windows[name].show()

    def deleteLater(self):
        """
        Add deleteLater entries for the associated windows.
        """
        for _window in self._child_windows:
            _window.deleteLater()
        self.centralWidget().deleteLater()
        super().deleteLater()

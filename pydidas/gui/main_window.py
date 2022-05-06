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
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["MainWindow"]

import os
from pathlib import Path
from functools import partial

from qtpy import QtWidgets, QtCore

from ..core import FrameConfigError
from ..core.utils import format_input_to_multiline_str
from ..widgets import CentralWidgetStack, InfoWidget, get_pyqt_icon_from_str_reference
from .global_configuration_frame import GlobalConfigurationFrame
from . import utils
from .main_menu import MainMenu


class MainWindow(MainMenu):
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

        self._frame_menuentries = []
        self._frame_meta = {}

        self._toolbars = {}
        self._toolbar_actions = {}
        self._toolbars_created = False
        self.__create_logging_info_box()

    def __create_logging_info_box(self):
        """
        Create the InfoWidget for logging and status messages.
        """
        self.__info_widget = InfoWidget()
        _dock_widget = QtWidgets.QDockWidget("Logging && information")
        _dock_widget.setWidget(self.__info_widget)
        _dock_widget.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable
            | QtWidgets.QDockWidget.DockWidgetFloatable
        )
        _dock_widget.setBaseSize(500, 50)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, _dock_widget)

    def create_toolbars(self):
        """
        Create the toolbars to select between different widgets in the
        centralWidget.
        """
        self.__add_global_config_frame()
        self._toolbars = {}
        for tb in utils.find_toolbar_bases(self._frame_menuentries):
            tb_title = tb if tb else "Main toolbar"
            self._toolbars[tb] = QtWidgets.QToolBar(tb_title, self)
            self._toolbars[tb].setStyleSheet("QToolBar{spacing:20px;}")
            self._toolbars[tb].setIconSize(QtCore.QSize(40, 40))
            self._toolbars[tb].setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
            self._toolbars[tb].setFixedWidth(85)
            self._toolbars[tb].setMovable(False)
            self._toolbars[tb].toggleViewAction().setEnabled(False)

        for item in self._frame_menuentries:
            _icon = self._frame_meta[item]["icon"]
            _label = self._frame_meta[item]["label"]
            _action = QtWidgets.QAction(_icon, _label, self)
            _action.setCheckable(True)
            _action.triggered.connect(partial(self.select_item, item))
            self._toolbar_actions[item] = _action
            itembase = os.path.dirname(item)
            self._toolbars[itembase].addAction(_action)

        for _toolbar_name in self._toolbars:
            if _toolbar_name != "":
                self.addToolBarBreak(QtCore.Qt.LeftToolBarArea)
            self.addToolBar(QtCore.Qt.LeftToolBarArea, self._toolbars[_toolbar_name])
            # only make the root toolbar visible to start with:
            self._toolbars[_toolbar_name].setVisible(_toolbar_name == "")
        self.select_item(self._frame_menuentries[0])
        self._toolbars_created = True

    def __add_global_config_frame(self):
        """
        Add the required widgets and signals for the global configuration
        window and create it.
        """
        self.register_frame(
            GlobalConfigurationFrame,
            "Global configuration",
            "Global configuration",
            "qta::mdi.application-cog",
        )
        _w = CentralWidgetStack().get_widget_by_name("Global configuration")
        _w2 = self._child_windows["global_config"].centralWidget()
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
            raise FrameConfigError(
                f'The selected menu entry "{menu_entry}"' " already exists."
            )
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
        _new_menus = [
            ("" if _path == Path() else _path.as_posix())
            for _path in reversed(Path(_ref).parents)
        ] + [_ref]
        self._frame_menuentries.append(_ref)
        if isinstance(menuicon, str):
            menuicon = get_pyqt_icon_from_str_reference(menuicon)
        self._frame_meta[_ref] = dict(
            label=format_input_to_multiline_str(frame.title),
            icon=menuicon,
            index=frame.frame_index,
            menus=_new_menus,
        )

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
            _toolbar.setVisible(_name in self._frame_meta[label]["menus"])
        _new_widget = self.centralWidget().get_widget_by_name(label)
        if _new_widget.show_frame:
            for _name, _action in self._toolbar_actions.items():
                _action.setChecked(
                    _name in self._frame_meta[label]["menus"] or _name == label
                )
            self.centralWidget().setCurrentIndex(self._frame_meta[label]["index"])
        else:
            self._toolbar_actions[label].setChecked(False)
        self.setUpdatesEnabled(True)
        self.centralWidget().setUpdatesEnabled(True)

    def restore_gui_state(self, filename=None):
        """
        Restore the window states from saved information.

        If the filename is not specified, the internally used file for storing
        the state will be opened.

        Parameters
        ----------
        filename : Union[None, str], optional
            The filename to be used to restore the state. Pydidas will use the
            internal default if the filename is None. The default is None.
        """
        super().restore_gui_state()
        _current_index = self.centralWidget().currentIndex()
        self.select_item(self._frame_menuentries[_current_index])

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
        if text[-1] != "\n":
            text += "\n"
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
        self.centralWidget().deleteLater()
        super().deleteLater()

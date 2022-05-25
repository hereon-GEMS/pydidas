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
from ..widgets import BaseFrame, InfoWidget, get_pyqt_icon_from_str_reference
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
        self._frames_to_add = []

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

    def show(self):
        """
        Insert a create_toolbars method call into the show method if the
        toolbars have not been created at the time of the show call.
        """
        self.create_frame_instances()
        if not self._toolbars_created:
            self.create_toolbars()
        self.connect_global_config_frame()
        QtWidgets.QMainWindow.show(self)
        self.centralWidget().currentChanged.emit(0)

    def create_frame_instances(self):
        """
        Create the instances for all registered frames.

        Raises
        ------
        FrameConfigError
            If a similar menu entry has already been registered.

        """
        while len(self._frames_to_add) > 0:
            _class, _title, _menu_entry, _icon = self._frames_to_add.pop(0)
            if _title is None:
                _title = _class.menu_title
            if _menu_entry is None:
                _menu_entry = _class.menu_entry
            if _icon is None:
                _icon = _class.menu_icon
            if _menu_entry in self._frame_menuentries:
                raise FrameConfigError(
                    f'The selected menu entry "{_menu_entry}"' " already exists."
                )
            _frame = _class(
                parent=self.centralWidget(),
                menu_entry=_menu_entry,
                title=_title,
                icon=_icon,
            )
            _frame.status_msg.connect(self.update_status)
            self.centralWidget().register_widget(_menu_entry, _frame)
            self._store_frame_metadata(_frame)

    def create_toolbars(self):
        """
        Create the toolbars to select between different widgets in the
        centralWidget.
        """
        self._toolbars = {}
        for tb in utils.find_toolbar_bases(self._frame_menuentries):
            tb_title = tb if tb else "Main toolbar"
            self._toolbars[tb] = QtWidgets.QToolBar(tb_title, self)
            self._toolbars[tb].setStyleSheet("QToolBar{spacing:20px;}")
            self._toolbars[tb].setIconSize(QtCore.QSize(40, 40))
            self._toolbars[tb].setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
            self._toolbars[tb].setFixedWidth(90)
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

    def connect_global_config_frame(self):
        """
        Add the required signals for the global configuration
        window and create it.
        """
        if "Global configuration" in self.centralWidget().widget_indices:
            _cfg_frame = self.centralWidget().get_widget_by_name("Global configuration")
            _cfg_frame.frame_activated(_cfg_frame.frame_index)
            _cfg_window = self._child_windows["global_config"]
            _cfg_frame.value_changed_signal.connect(_cfg_window.external_update)
            _cfg_window.value_changed_signal.connect(_cfg_frame.external_update)

    def register_frame(self, frame, title=None, menu_entry=None, icon=None):
        """
        Register a frame class with the MainWindow and add it to the
        CentralWidgetStack.

        This method takes a :py:class:`BaseFrame <pydidas.widgets.BaseFrame>`
        and creates an instance which is registeres with the
        CentralWidgetStack. It also stores the required metadata to create
        a actionbar link to open the frame.

        Parameters
        ----------
        frame : Union[pydidas.widgets.BaseFrame, str]
            The class of the Frame. This must be a subclass of BaseFrame.
            If a string is passed, an empty frame class with the metadata
            given by title, menu_entry and icon is created.
        title : Union[None, str], optional
            The frame's title. If None, the default title from the Frame class
            will be used. The default is None.
        menu_entry : Union[None, str], optional
            The path to the menu entry for the frame. Hierachical levels are
            separated by a '/' item. If None, the menu_entry from the Frame
            class will be used. The default is None.
        icon : Union[str, QtGui.QIcon, None], optional
            The menu icon. If None, this defaults to the menu icon specified
            in the frame's class. If a string is supplied, this is interpreted
            as a reference for a QIcon. For the refernce on string conversion,
            please check
            :py:func:`pydidas.widgets.get_pyqt_icon_from_str_reference`.
        """
        if isinstance(frame, str):
            frame = type(
                frame,
                (BaseFrame,),
                {
                    "menu_title": title,
                    "menu_entry": menu_entry,
                    "menu_icon": icon,
                    "show_frame": False,
                },
            )
        self._frames_to_add.append([frame, title, menu_entry, icon])

    def _store_frame_metadata(self, frame):
        """
        Store the frame metadata in the internal dictionaries for reference.

        Parameters
        ----------
        frame : pydidas.widgets.BaseFrame
            The instantiated frame
        """
        _ref = frame.ref_name
        _new_menus = [
            ("" if _path == Path() else _path.as_posix())
            for _path in reversed(Path(_ref).parents)
        ] + [_ref]
        self._frame_menuentries.append(_ref)
        _menu_icon = frame.icon
        if isinstance(_menu_icon, str):
            _menu_icon = get_pyqt_icon_from_str_reference(_menu_icon)
        self._frame_meta[_ref] = dict(
            label=format_input_to_multiline_str(frame.title),
            icon=_menu_icon,
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

    def deleteLater(self):
        """
        Add deleteLater entries for the associated windows.
        """
        self.centralWidget().deleteLater()
        super().deleteLater()

# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the MainWindow class which extends the MainMenu with a toolbar on the left
to select the different frames.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["MainWindow"]


import os
from functools import partial

from qtpy import QtCore, QtWidgets

from pydidas.core import PydidasGuiError, UserConfigError
from pydidas.gui import utils
from pydidas.gui.frames import (
    DefineDiffractionExpFrame,
    DefineScanFrame,
    WorkflowEditFrame,
)
from pydidas.gui.main_menu import MainMenu
from pydidas.resources import icons
from pydidas.widgets.framework import FontScalingToolbar


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
        MainMenu.__init__(self, parent, geometry)

        self._toolbar_metadata = {}
        self._frames_to_add = []

        self._toolbars = {}
        self._toolbar_actions = {}
        self.__configuration = {
            "toolbars_created": False,
            "toolbar_visibility": {"": True},
        }
        self.setWindowIcon(icons.pydidas_icon_with_bg())

    def show(self):
        """
        Insert a create_toolbar_menu method call into the show method if the
        toolbars have not been created at the time of the show call.
        """
        self.create_frame_instances()
        if not self.__configuration["toolbars_created"]:
            self.create_toolbar_menu()
        QtWidgets.QMainWindow.show(self)
        self.centralWidget().currentChanged.emit(0)

    def create_frame_instances(self):
        """
        Create the instances for all registered frames.

        Raises
        ------
        PydidasGuiError
            If a similar menu entry has already been registered.

        """
        while len(self._frames_to_add) > 0:
            _class = self._frames_to_add.pop(0)
            _frame = _class(parent=self.centralWidget())
            _frame.status_msg.connect(self.update_status)
            self.centralWidget().register_frame(_frame)

    def create_toolbar_menu(self):
        """
        Create the toolbar menu to select between different widgets in the
        centralWidget.
        """
        self._toolbar_metadata = self.centralWidget().frame_toolbar_metadata

        self._create_toolbar_menu_entries()
        self._create_toolbars()
        self._create_toolbar_actions()

        self._update_toolbar_visibility()
        self.select_item(self.centralWidget().currentWidget().menu_entry)
        self.__configuration["toolbars_created"] = True
        self.__connect_workflow_processing_signals()

    def _create_toolbar_menu_entries(self):
        """
        Create the required toolbar menu entries to populate the menu.
        """
        self.__configuration["menu_entries"] = []
        for _key in self.centralWidget().frame_toolbar_entries:
            _items = _key.split("/")
            for _entry in ["/".join(_items[: _i + 1]) for _i in range(len(_items))]:
                if _entry not in self.__configuration["menu_entries"]:
                    self.__configuration["menu_entries"].append(_entry)
                if _entry not in self._toolbar_metadata:
                    self._toolbar_metadata[_entry] = utils.create_generic_toolbar_entry(
                        _entry
                    )
                    self.__configuration["toolbar_visibility"][_entry] = False

    def _create_toolbars(self):
        """
        Create the toolbar widgets for the toolbar menu.
        """
        for _tb in utils.find_toolbar_bases(self.__configuration["menu_entries"]):
            tb_title = _tb if _tb else "Main toolbar"
            self._toolbars[_tb] = FontScalingToolbar(tb_title, self)
        for _toolbar_name, _toolbar in self._toolbars.items():
            if _toolbar_name != "":
                self.addToolBarBreak(QtCore.Qt.LeftToolBarArea)
            self.addToolBar(QtCore.Qt.LeftToolBarArea, _toolbar)

    def _create_toolbar_actions(self):
        """
        Create the toolbar actions to switch between frames.
        """
        for _entry in self.__configuration["menu_entries"]:
            _metadata = self._toolbar_metadata[_entry]
            _action = QtWidgets.QAction(_metadata["icon"], _metadata["label"], self)
            _action.setCheckable(True)
            _action.triggered.connect(partial(self.select_item, _entry))
            self._toolbar_actions[_entry] = _action
            _item_base = os.path.dirname(_entry)
            self._toolbars[_item_base].addAction(_action)

    def _update_toolbar_visibility(self):
        """
        Update the toolbar visibility based on the stored information.
        """
        for _name, _toolbar in self._toolbars.items():
            _visible = self.__configuration["toolbar_visibility"].get(_name, False)
            _toolbar.setVisible(_visible)
            if _name != "":
                self._auto_update_toolbar_entry(_name)

    def __connect_workflow_processing_signals(self):
        """
        Connect the signals from the WorkflowProcessing which block changes.
        """
        try:
            _proc_frame = self.centralWidget().get_widget_by_name(
                "Workflow processing/Run full workflow"
            )
        except KeyError:
            return
        for _key, _action in self._toolbar_actions.items():
            if _key in [
                WorkflowEditFrame.menu_entry,
                DefineScanFrame.menu_entry,
                DefineDiffractionExpFrame.menu_entry,
            ]:
                _proc_frame.sig_processing_running.connect(_action.setDisabled)

    def _auto_update_toolbar_entry(self, label):
        """
        Run an automatic update of the toolbar entry referenced by name.

        This method toggles the expand/hide of the toolbar entry.

        Parameters
        ----------
        label : str
            The toolbar entry reference label.
        """
        _action = self._toolbar_actions[label]
        _suffix = (
            "_visible"
            if self.__configuration["toolbar_visibility"][label]
            else "_invisible"
        )
        _text = self._toolbar_metadata[label][f"label{_suffix}"]
        _action.setText(_text)
        _icon = self._toolbar_metadata[label][f"icon{_suffix}"]
        _action.setIcon(_icon)

    def register_frame(self, frame):
        """
        Register a frame class with the MainWindow and add it to the
        PydidasFrameStack.

        This method takes a :py:class:`BaseFrame <pydidas.widgets.framework.BaseFrame>`
        and creates an instance which is registers with the
        PydidasFrameStack. It also stores the required metadata to create
        an actionbar link to open the frame.

        Parameters
        ----------
        frame : type[pydidas.widgets.framework.BaseFrame]
            The class of the Frame. This must be a subclass of BaseFrame.
            If a string is passed, an empty frame class with the metadata
            given by title, menu_entry and icon is created.
        """
        _stack = self.centralWidget()
        _entry_exists = frame.menu_entry in _stack.get_all_widget_names()
        _class_exists = frame in [_frame.__class__ for _frame in _stack.frames]
        if _entry_exists and _class_exists:
            return
        if _entry_exists or _class_exists:
            raise PydidasGuiError(
                f"Could not register frame '{frame.menu_title}' (class {frame}) "
                "because the menu entry and frame class do not match an already "
                "registered Frame."
            )
        self._frames_to_add.append(frame)

    @QtCore.Slot(str)
    def select_item(self, label):
        """
        Select an item from the left toolbar and select the corresponding
        frame in the centralWidget.

        For labels that have frames attached to them, this method will show the frame.
        For labels which are only entries in the menu tree, this method will show/hide
        the respective toolbar.

        Parameters
        ----------
        label : str
            The label of the selected item.
        """
        self.setUpdatesEnabled(False)
        if label in self.centralWidget().frame_indices:
            for _name, _action in self._toolbar_actions.items():
                _action.setChecked(_name == label)
            self.centralWidget().activate_widget_by_name(label)
        else:
            _toolbar = self._toolbars[label]
            _new_visibility = not _toolbar.isVisible()
            _toolbar.setVisible(_new_visibility)
            self._toolbar_actions[label].setChecked(False)
            self.__configuration["toolbar_visibility"][label] = _new_visibility
            self._auto_update_toolbar_entry(label)
        self.setUpdatesEnabled(True)

    def restore_gui_state(self, state="saved", filename=None):
        """
        Restore the window states from saved information.

        This method also updates the left toolbar entry according to the restored
        frame.

        Parameters
        ----------
        state: str, optional
            The state to be restored. Can be "saved" to restore the last saved state,
            "exit" to restore the state on exit or "manual" to manually give a filename.
        filename : Union[None, str], optional
            The filename to be used to restore the state. This kwarg will only be used
            if the state kwarg is set to "manual".
        """
        try:
            MainMenu.restore_gui_state(self, state, filename)
        except Exception as exc:
            raise UserConfigError(
                "Error during GUI state restoration.\n\n"
                + str(exc)
                + "\n\nSkipping restoration..."
            )
        self.select_item(self.centralWidget().currentWidget().menu_entry)

    def export_main_window_state(self):
        """
        Export the main window's state.

        Returns
        -------
        dict
            The state of the main window required to restore the look.
        """
        return MainMenu.export_main_window_state(self) | {
            "toolbar_visibility": self.__configuration["toolbar_visibility"],
        }

    def restore_main_window_state(self, state):
        """
        Restore the main window's state from saved information.

        Parameters
        ----------
        state : dict
            The stored state of the main window.
        """
        self.__configuration["toolbar_visibility"] = state["toolbar_visibility"]
        self._update_toolbar_visibility()
        MainMenu.restore_main_window_state(self, state)

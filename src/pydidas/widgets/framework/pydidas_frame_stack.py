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
Module with the PydidasFrameStack.

The PydidasFrameStack is a QStackedWidget and is used as the central widget
in the pydidas GUI. All frames can be accessed through the PydidasFrameStack
once they have been registered.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasFrameStack"]


from pathlib import Path
from typing import Any

from qtpy import QtCore, QtWidgets

from pydidas.core import SingletonObject, utils
from pydidas.widgets.dialogues import WarningBox
from pydidas.widgets.framework.base_frame import BaseFrame
from pydidas.widgets.utilities import get_pyqt_icon_from_str


class PydidasFrameStack(SingletonObject, QtWidgets.QStackedWidget):
    """
    A QStackedWidget with references to all the possible top-level widgets.

    Widgets are responsible for registering themselves with this class to
    allow a later reference. For the pydidas main application, the main
    window takes care of registration.

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget. The default is None.
    """

    sig_mouse_entered = QtCore.Signal()

    def initialize(self, *args: Any, **kwargs: Any) -> None:
        self._frame_indices = {}
        self._frame_names_from_index = {}
        self._frames = {}

    @property
    def frame_indices(self) -> dict[str, int]:
        """
        Get the frame indices.

        Returns
        -------
        dict
            A dictionary with the frame indices, where the keys are the
            frame menu items and the values are the indices in the QStackedWidget.
        """
        return self._frame_indices

    @property
    def current_frames(self) -> list[BaseFrame]:
        """
        Get all current frames

        This property returns the list of all registered frames in the
        PydidasFrameStack.

        Returns
        -------
        list
            The list of all registered frames.
        """
        return list(self._frames.values())

    @property
    def frame_names(self) -> list[str]:
        """
        Get the names of all registered frames.

        This property returns the list of all registered frame names in the
        PydidasFrameStack.

        Returns
        -------
        list
            The list of all registered frame names.
        """
        return list(self._frames)

    def register_frame(self, frame: BaseFrame):
        """
        Register a Frame with the stacked widget.

        This method will register a Frame and hold a reference to the frame index by
        the Frame's menu_entry.

        Parameters
        ----------
        frame : pydidas.widgets.framework.BaseFrame
            The BaseFrame to be registered.

        Raises
        ------
        TypeError
            If a widget is not of the type pydidas.widgets.framework.BaseFrame
        KeyError
            When a widget with the same name has already been registered
            to prevent duplicate entries in the index reference.
        """
        if not isinstance(frame, BaseFrame):
            raise TypeError("Can only register pydidas.widgets.BaseFrame objects.")
        if frame.menu_entry in self._frame_indices:
            raise KeyError(
                f"A widget with the menu entry '{frame.menu_entry}' has already "
                "been registered with the PydidasFrameStack. The new widget has not "
                "been registered."
            )
        index = QtWidgets.QStackedWidget.addWidget(self, frame)
        frame.frame_index = index
        self.currentChanged.connect(frame.frame_activated)
        self._frames[frame.menu_entry] = frame
        self._frame_indices[frame.menu_entry] = index
        self._frame_names_from_index[index] = frame.menu_entry

    def get_widget_by_name(self, ref_name: str) -> BaseFrame:
        """
        Get a widget from its reference name.

        This method will return the widget registered with the reference
        name, if it exists.

        Parameters
        ----------
        ref_name : str
            The reference name of the widget.

        Raises
        ------
        KeyError
            If no widget with the reference name has been registered.

        Returns
        -------
        widget : pydidas.widgets.framework.BaseFrame
            The widget referenced by the name.
        """
        if ref_name not in self._frame_indices:
            raise KeyError(f"No widget with the name `{ref_name}` has been registered.")
        return self.widget(self._frame_indices[ref_name])

    @property
    def frame_toolbar_entries(self) -> list[str]:
        """
        Get all menu entries based on the stored information in the Frames.

        Returns
        -------
        list
            The list of the menu entries for all registered Frames.
        """
        _entries = []
        for _frame in self._frames.values():
            _entries.append(_frame.menu_entry)
        return _entries

    @property
    def frame_toolbar_metadata(self) -> dict[str, Any]:
        """
        Get all the metadata to create the frame toolbar menu from the frames.

        Returns
        -------
        dict
            A dictionary with all the required information to create the toolbar menu.
        """
        _meta = {}
        for _frame in self._frames.values():
            if isinstance(_frame.menu_icon, str):
                _frame.menu_icon = get_pyqt_icon_from_str(_frame.menu_icon)

            _meta[_frame.menu_entry] = {
                "label": utils.format_input_to_multiline_str(
                    _frame.menu_title, max_line_length=12
                ),
                "icon": _frame.menu_icon,
                "index": _frame.frame_index,
                "menu_tree": [
                    ("" if _path == Path() else _path.as_posix())
                    for _path in reversed(Path(_frame.menu_entry).parents)
                ]
                + [_frame.menu_entry],
            }
        return _meta

    @property
    def active_widget_name(self) -> str:
        """
        Return the name of the active widget.

        Returns
        -------
        str
            The name of the active widget.
        """
        return self._frame_names_from_index[self.currentIndex()]

    def activate_widget_by_name(self, ref_name: str):
        """
        Set the widget referenced by name to the active widget.

        Parameters
        ----------
        ref_name : str
            The reference name of the widget.

        Raises
        ------
        KeyError
            If no widget with the name has been registered.
        """
        if ref_name not in self._frame_indices:
            raise KeyError(
                f"No widget with the name `{ref_name}` has been"
                " registered with the CENTRAL_WIDGET_STACK."
            )
        self.setCurrentIndex(self._frame_indices[ref_name])

    def remove_widget_by_name(self, ref_name: str):
        """
        Remove a widget by its reference name.

        This method finds the widget associated with the reference name and
        deletes it from the QStackedWidget.

        Note: This does not delete the widget itself, only the reference in
        the QStackedWidget.

        Parameters
        ----------
        ref_name : str
            The reference name of the widget

        Raises
        ------
        KeyError
            If the reference name has not been used for registering a widget.
        """
        if ref_name not in self._frame_indices:
            raise KeyError(
                f"No widget width the name `{ref_name}` has been registered."
            )
        _widget = self._frames[ref_name]
        self.removeWidget(_widget)

    def addWidget(self, widget: QtWidgets.QWidget | None = None, name: str = None):
        """
        Overload the QStackedWidget.addWidget method to deactivate it.

        Widgets should be added through the register_widget method, which
        also demands a reference name.

        Raises
        ------
        NotImplementedError
            Reference to the register_widget method is given.
        """
        raise NotImplementedError(
            'Please use the "register_widget(name, widget)" method.'
        )

    def removeWidget(self, frame: BaseFrame):
        """
        Remove a frame from the QStackdWidget.

        This overloaded method removes a frame widget from the QStackedWidget and
        also dereferences it from the metadata.

        Parameters
        ----------
        frame : BaseFrame
            The widget to be removed from the QStackedWidget.

        Raises
        ------
        KeyError
            If the widget is not registered.
        """
        if frame not in self._frames.values():
            raise KeyError(f"The widget `{frame}` is not registered.")
        frame.frame_index = None
        del self._frames[frame.menu_entry]
        del self._frame_indices[frame.menu_entry]
        self.currentChanged.disconnect(frame.frame_activated)
        super().removeWidget(frame)
        self._frame_names_from_index = {}
        for _index in range(self.count()):
            _frame = self.widget(_index)
            _frame.frame_index = _index
            self._frame_names_from_index[_index] = _frame.menu_entry
            self._frame_indices[_frame.menu_entry] = _index

    def reset(self):
        """
        Reset the PydidasFrameStack and delete all widgets from itself.
        """
        while len(self._frames) > 0:
            self.removeWidget(self.widget(0))

    def is_registered(self, widget: BaseFrame) -> bool:
        """
        Check if a widget is already registered.

        This method checks if a widget is already registered and returns
        the bool result.

        Parameters
        ----------
        widget : QWidget
            The widget which might already be registered.

        Returns
        -------
        bool
            This will be True if the widget has been registered, and False
            if not.
        """
        return widget in self._frames.values()

    def enterEvent(self, event: QtCore.QEvent):
        """
        Send a signal that the mouse entered the central widget.

        Parameters
        ----------
        event : QtCore.QEvent
            The calling event.
        """
        self.sig_mouse_entered.emit()

    def restore_frame_states(self, state: dict[str, dict]):
        """
        Restore the states of all frames from the stored state information.

        Parameters
        ----------
        state : dict[str, dict]
            A dictionary with the stored state information for all frames.
            The keys are labeled based on the menu entries and the values are
            dictionaries with the state information for each frame.
        """
        _unrestored_frames = self.frame_names
        _missing_frames = []
        for _frame_name, _state in state.items():
            if _frame_name not in _unrestored_frames:
                _missing_frames.append(_frame_name)
            self.get_widget_by_name(_frame_name).restore_state(_state)
            _unrestored_frames.remove(_frame_name)
        if _unrestored_frames:
            WarningBox(
                "Unrestored frames",
                (
                    "No stored state information was found for the following frames:\n"
                    + ", ".join(_unrestored_frames)
                ),
            )
        if _missing_frames:
            WarningBox(
                "Frames not included in current GUI",
                (
                    "The following frames had a stored state bute were not found in "
                    "the current GUI configuration:\n" + ", ".join(_missing_frames)
                ),
            )

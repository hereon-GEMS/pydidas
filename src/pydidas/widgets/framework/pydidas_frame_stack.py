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
from typing import List, Union

from qtpy import QtCore, QtWidgets

from pydidas.core import SingletonFactory, utils
from pydidas.widgets.framework.base_frame import BaseFrame
from pydidas.widgets.utilities import get_pyqt_icon_from_str


class _PydidasFrameStack(QtWidgets.QStackedWidget):
    """
    A QStackedWidget with references to all the possible top level widgets.

    Widgets are responsible for registering themselves with this class to
    allow a later reference. For the pydidas main application, the main
    window takes care of registration.

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget. The default is None.

    Attributes
    ----------
    widgets : list
        A list of all the registered widgets.
    frame_indices : dict
        A dictionary with (widget_name: index) entries to reference
        widgets with their names.
    """

    sig_mouse_entered = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.frame_indices = {}
        self.frames = []

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
            If a widget is not of type pydidas.widgets.framework.BaseFrame
        KeyError
            When a widget with the same name has already been registered
            to prevent duplicate entries in the index reference.
        """
        if not isinstance(frame, BaseFrame):
            raise TypeError("Can only register pydidas.widgets.BaseFrame objects.")
        if frame.menu_entry in self.frame_indices:
            raise KeyError(
                f"A widget with the menu entry '{frame.menu_entry}' has already "
                "been registered with the PydidasFrameStack. The new widget has not "
                "been registered."
            )
        index = QtWidgets.QStackedWidget.addWidget(self, frame)
        frame.frame_index = index
        self.currentChanged.connect(frame.frame_activated)
        self.frames.append(frame)
        self.frame_indices[frame.menu_entry] = index

    def get_name_from_index(self, index: int) -> str:
        """
        Get the widget reference name associated with the indexed widget.

        This method searches the dictionary of (name: index) entries and
        returns the name key for the index value.

        Parameters
        ----------
        index : int
            The widget index.

        Returns
        -------
        str
            The reference name.
        """
        key_list = list(self.frame_indices.keys())
        val_list = list(self.frame_indices.values())
        return key_list[val_list.index(index)]

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
        if ref_name not in self.frame_indices:
            raise KeyError(f"No widget with the name `{ref_name}` has been registered.")
        return self.widget(self.frame_indices[ref_name])

    @property
    def frame_toolbar_entries(self) -> List[str]:
        """
        Get all menu entries based on the stored information in the Frames.

        Returns
        -------
        list
            The list of the menu entries for all registered Frames.
        """
        _entries = []
        for _frame in self.frames:
            _entries.append(_frame.menu_entry)
        return _entries

    @property
    def frame_toolbar_metadata(self) -> dict:
        """
        Get all the metadata to create the frame toolbar menu from the frames.

        Returns
        -------
        dict
            A dictionary with all the required information to create the toolbar menu.
        """
        _meta = {}
        for _frame in self.frames:
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
        return self.get_name_from_index(self.currentIndex())

    def get_all_widget_names(self) -> List[str]:
        """
        Get the names of all registered widgets.

        Returns
        -------
        list
            The list of all names of registered widgets.
        """
        return [w.menu_entry for w in self.frames]

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
        if ref_name not in self.frame_indices:
            raise KeyError(
                f"No widget with the name `{ref_name}` has been"
                " registered with the CENTRAL_WIDGET_STACK."
            )
        index = self.frame_indices[ref_name]
        self.setCurrentIndex(index)

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
        if ref_name not in self.frame_indices:
            raise KeyError(
                f"No widget width the name `{ref_name}` has been registered."
            )
        _widget = self.frames[self.frame_indices[ref_name]]
        self.removeWidget(_widget)

    def addWidget(
        self, widget: Union[None, QtWidgets.QWidget] = None, name: str = None
    ):
        """
        Overload the QStackedWidget.addWidget method to deactivate it.

        Widgets should be added through the register_widget method which
        also demands a reference name.

        Raises
        ------
        NotImplementedError
            Reference to the register_widget method is given.
        """
        raise NotImplementedError(
            'Please use the "register_widget(name, widget)" method.'
        )

    def removeWidget(self, widget: BaseFrame):
        """
        Remove a widget from the QStackdWidget.

        This overloaded method removed a widget from the QStackedWidget and
        also de-references it from the metadata.

        Parameters
        ----------
        widget : BaseFrame
            The widget to be removed from the QStackedWidget.

        Raises
        ------
        KeyError
            If the widget is not registered.
        """
        if widget not in self.frames:
            raise KeyError(f"The widget `{widget}` is not registered.")
        widget.frame_index = None
        _index = self.frames.index(widget)
        _ref_name = self.get_name_from_index(_index)
        self.frames.remove(widget)
        self.currentChanged.disconnect(widget.frame_activated)
        for _key, _cur_index in self.frame_indices.items():
            if _cur_index > _index:
                self.frame_indices[_key] -= 1
                self.widget(_cur_index).frame_index -= 1
        del self.frame_indices[_ref_name]
        super().removeWidget(widget)

    def reset(self):
        """
        Reset the PydidasFrameStack and delete all widgets from itself.
        """
        while len(self.frames) > 0:
            self.removeWidget(self.frames[0])

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
            This will be True is the widget has been registered, and False
            if not.
        """
        return widget in self.frames

    def change_reference_name(self, new_name: str, widget: BaseFrame):
        """
        Change the reference name for a widget.

        This method changes the internal reference name for the widget and
        stored the supplied new_name.

        Parameters
        ----------
        new_name : str
            The new reference name.
        widget : BaseFrame
            The widget of which the reference name shall be changed.

        Raises
        ------
        KeyError
            If the widget is not registered at all.
        """
        if not self.is_registered(widget):
            raise KeyError(f"The widget `{widget}` is not registered.")
        index = self.frames.index(widget)
        name = self.get_name_from_index(index)
        if name != new_name:
            del self.frame_indices[name]
            self.frame_indices[new_name] = index
            self.widget(index).menu_entry = new_name

    def enterEvent(self, event):
        """
        Send a signal that the mouse entered the central widget.

        Parameters
        ----------
        event : QtCore.QEvent
            The calling event.
        """
        self.sig_mouse_entered.emit()


PydidasFrameStack = SingletonFactory(_PydidasFrameStack)

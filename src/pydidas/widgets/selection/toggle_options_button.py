# This file is part of pydidas
#
# Copyright 2024 - 2026, Helmholtz-Zentrum Hereon
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
# along with pydidas If not, see <http://www.gnu.org/licenses/>.

"""
Module with the ToggleOptionsButton which allows to show/hide a linked widget.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ToggleOptionsButton"]


from typing import Any

from qtpy import QtCore, QtGui, QtWidgets

from pydidas.core import UserConfigError
from pydidas.widgets.factory import PydidasPushButton
from pydidas.widgets.utilities import get_pyqt_icon_from_str


class ToggleOptionsButton(PydidasPushButton):
    """
    Widget to show or hide a linked widget.

    This button provides a convenient way to toggle the visibility of an
    optional advanced options widget. It manages the visibility state,
    updates its own text and icon to reflect the current state, and
    synchronizes the visibility of any linked widget.

    Parameters
    ----------
    linked_widget_visible : bool, optional
        Initial visibility state. Default is False.
    toggle_text_shown : str, optional
        Text shown when options are hidden. Default is "Show advanced options".
    toggle_text_hidden : str, optional
        Text shown when options are visible. Default is "Hide advanced options".
    linked_widget : QtWidgets.QWidget or None, optional
        Widget to control visibility. Default is None.
    """

    sig_visibility_changed = QtCore.Signal(bool)
    init_kwargs = PydidasPushButton.init_kwargs + [
        "linked_widget_visible",
        "linked_widget",
        "toggle_text_shown",
        "toggle_text_hidden",
    ]

    def __init__(self, *args: Any, **kwargs: Any):
        """
        Initialize the ToggleOptionsButton.

        Parameters
        ----------
        *args : Any
            Positional arguments passed to the parent PydidasPushButton class.
        **kwargs : Any
            Keyword arguments passed to the parent class and for configuring
            this button. Recognized keyword arguments include:

            linked_widget_visible : bool, optional
                The initial visibility state of the linked widget.
                Default is False.
            toggle_text_shown : str, optional
                The text to display on the button when showing options.
                Default is "Show advanced options".
            toggle_text_hidden : str, optional
                The text to display on the button when hiding options.
                Default is "Hide advanced options".
            linked_widget : QtWidgets.QWidget or None, optional
                The widget to link to this button for visibility control.
                Default is None.
        """
        PydidasPushButton.__init__(self, *args, **kwargs)
        self._linked_widget_visible = bool(kwargs.get("linked_widget_visible", False))
        self._toggle_text_for_state = {
            True: kwargs.get("toggle_text_shown", "Hide advanced options"),
            False: kwargs.get("toggle_text_hidden", "ShowN advanced options"),
        }
        self.linked_widget = kwargs.get("linked_widget", None)
        self.clicked.connect(self.toggle_state)

    @property
    def current_icon(self) -> QtGui.QIcon:
        """
        Get the currently correct icon.

        Returns
        -------
        QtGui.QIcon :
            The icon corresponding to the current status.
        """
        if self._linked_widget_visible:
            return get_pyqt_icon_from_str("qt-std::SP_TitleBarShadeButton")
        return get_pyqt_icon_from_str("qt-std::SP_TitleBarUnshadeButton")

    @property
    def linked_widget_visible(self) -> bool:
        """
        Get the advanced visibility status.

        Returns
        -------
        bool :
            The advanced visibility status.
        """
        return self._linked_widget_visible

    @linked_widget_visible.setter
    def linked_widget_visible(self, value: bool | int | float) -> None:
        """
        Set the advanced visibility status.

        Parameters
        ----------
        value : bool or int or float
            The new advanced visibility status.
        """
        if value not in [0, 1]:
            raise UserConfigError(
                "`ToggleOptionsButton.linked_widget_visible` must be called with "
                "a value of 0 or 1 (i.e. boolean)."
            )
        value = bool(value)
        _new_value = self._linked_widget_visible != value
        self._linked_widget_visible = value
        self.setIcon(self.current_icon)
        self.setText(self._toggle_text_for_state[value])
        if self._linked_widget:
            self._linked_widget.setVisible(value)
            if _new_value:
                self.sig_visibility_changed.emit(value)

    @QtCore.Slot()
    def toggle_state(self) -> None:
        """
        Toggle the advanced visibility state.

        This slot toggles the linked widget visibility status. When called,
        it inverts the current `linked_widget_visible` property, which in
        turn updates the button text, icon, and the visibility of any
        linked widget.
        """
        self.linked_widget_visible = not self.linked_widget_visible

    @property
    def linked_widget(self) -> QtWidgets.QWidget | None:
        """
        Get the linked widget.

        Returns
        -------
        QtWidgets.QWidget or None
            The linked widget, if applicable, or None.
        """
        return self._linked_widget

    @linked_widget.setter
    def linked_widget(self, widget: QtWidgets.QWidget | None):
        """
        Set the linked widget.

        Parameters
        ----------
        widget : QtWidgets.QWidget or None
            The widget to link.
        """
        if isinstance(widget, QtWidgets.QWidget) or widget is None:
            self._linked_widget = widget
            if isinstance(widget, QtWidgets.QWidget):
                self.linked_widget_visible = self._linked_widget_visible
                widget.setVisible(self.linked_widget_visible)
            return
        raise UserConfigError(
            "The `ToggleOptionsButton.linked_widget` must be a QWidget or None."
        )

    def set_linked_widget(self, widget: QtWidgets.QWidget | None) -> None:
        """
        Set the linked widget. This is an alias for the `linked_widget` property.

        Parameters
        ----------
        widget : QtWidgets.QWidget or None
            The widget to link.
        """
        self.linked_widget = widget

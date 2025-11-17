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
Module with the ParameterWidgetsMixIn class used to edit plugin
Parameters.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ParameterWidgetsMixIn"]


from typing import Any, Sequence

from qtpy import QtCore

from pydidas.core import Parameter, ParameterCollection, PydidasGuiError
from pydidas.widgets.parameter_config.base_param_io_widget import (
    BaseParamIoWidget,
)
from pydidas.widgets.parameter_config.parameter_widget import ParameterWidget
from pydidas.widgets.utilities import get_widget_layout_args


class ParameterWidgetsMixIn:
    """
    The ParameterWidgetsMixIn class includes methods which can be added to other
    classes to add functionality to create Parameter widgets and to have access to
    convenience functions for settings Parameter values.
    """

    def __init__(self):
        self.param_widgets: dict[str, BaseParamIoWidget] = {}
        self.param_composite_widgets: dict[str, ParameterWidget] = {}
        if not hasattr(self, "_widgets"):
            self._widgets = {}
        if not hasattr(self, "params"):
            self.params = ParameterCollection()

    def create_param_widget(self, param: Parameter | str, **kwargs: Any) -> None:
        """
        Add a name label and input widget for a specific parameter to the widget.

        Parameters
        ----------
        param : Parameter | str
            A Parameter class instance.
        **kwargs : Any
            Optional keyword arguments. Supported keys are:

            gridPos : tuple, optional
                The grid position in the layout. The default is (-1, 0, 1, 1)
            width_text : float, optional
                The relative width of the text field for the Parameter name.
                The default is defined in
                pydidas.core.constants.PARAM_WIDGET_TEXT_WIDTH.
            width_unit : float, optional
                The relative width of the text field for the Parameter unit.
                The default is defined in
                pydidas.core.constants.PARAM_WIDGET_UNIT_WIDTH.
            linebreak : bool, optional
                Keyword to toggle a line break between the text label and the
                input widget. The default is False.
            halign_io : QtCore.Qt.Alignment, optional
                The horizontal alignment for the input widget. The default is
                QtCore.Qt.AlignRight.
            halign_text : QtCore.Qt.Alignment, optional
                The horizontal alignment for the text (label) widget. The default
                is QtCore.Qt.AlignRight.
            parent_widget : Union[QWidget, str, None], optional
                The widget to which the label is added. If a string, this picks up the
                calling class's ._widgets dictionary and selects the string key's value.
                The default is self.
        """
        _parent = kwargs.get("parent_widget", self)
        if isinstance(_parent, str):
            _parent = self._widgets[_parent]
        if isinstance(param, str):
            param = self.params[param]
        _widget = ParameterWidget(param, **kwargs)
        self.param_composite_widgets[param.refkey] = _widget
        self.param_widgets[param.refkey] = _widget.io_widget

        if _parent.layout() is None:
            raise PydidasGuiError("No layout set.")
        _layout_args = get_widget_layout_args(_parent, **kwargs)
        _parent.layout().addWidget(_widget, *_layout_args)

    def set_param_value_and_widget(self, key: str, value: Any) -> None:
        """
        Update a parameter value both in the Parameter and the widget.

        This method will update the parameter referenced by <key> and
        update both the Parameter.value and the displayed widget
        entry.

        Parameters
        ----------
        key : str
            The reference key for the Parameter.
        value : Any
            The new parameter value. This must be of the same type as the
            Parameter datatype (or supported by a converter).

        Raises
        ------
        KeyError
            If no parameter or widget has been registered with this key.
        """
        if key not in self.params or key not in self.param_widgets:
            raise KeyError(
                f'No parameter with the key `{key}` and associated widget is "'
                f'"registered in this class.'
            )
        with QtCore.QSignalBlocker(self.param_widgets[key]):
            self.param_composite_widgets[key].param.value = value
            self.param_composite_widgets[key].set_value(value)

    def toggle_param_widget_visibility(self, key: str, visible: bool) -> None:
        """
        Toggle the visibility of widgets referenced with the key.

        This method allows showing/hiding the label and input widget for a
        parameter referenced with <key>.

        Parameters
        ----------
        key : str
            The reference key for the Parameter.
        visible : bool
            The boolean setting for the visibility.

        Raises
        ------
        KeyError
            If no widget has been registered with this key.
        """
        if key not in self.param_widgets:
            raise KeyError(f'No parameter with key "{key}" found.')
        self.param_composite_widgets[key].setVisible(visible)

    def update_param_widget_value(self, param_key: str, value: Any) -> None:
        """
        Update the value stored in a widget without changing the Parameter and
        without emitting signals.

        Parameters
        ----------
        param_key : str
            The Parameter reference key.
        value : Any
            The value. The type depends on the Parameter's value.
        """
        self.param_widgets[param_key].update_widget_value(value)

    def set_param_value_and_choices(
        self, param_key: str, value: Any, choices: None | Sequence[Any]
    ):
        """
        Update a Parameter's value and choices as well as the associated widget.

        Parameters
        ----------
        param_key : str
            The reference key for the Parameter.
        value : Any
            The new value for the Parameter.
        choices : None or Sequence[Any]
            The new list of choices for the Parameter. If None, the choices
            for the Parameter will be disabled.
        """
        super().set_param_value_and_choices(param_key, value, choices)
        self.param_composite_widgets[param_key].update_choices_from_param()

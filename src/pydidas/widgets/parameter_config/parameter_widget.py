# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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
Module with the ParameterWidget class which is a generic QWidget with a
GridLayout to add the label, I/O and unit widgets for a Parameter.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ParameterWidget"]


import html
from pathlib import Path
from typing import Any, Type

from qtpy import QtCore, QtWidgets

from pydidas.core import Hdf5key, Parameter, UserConfigError
from pydidas.core.constants import (
    ALIGN_CENTER_LEFT,
    PARAM_WIDGET_EDIT_WIDTH,
    PARAM_WIDGET_TEXT_WIDTH,
    PARAM_WIDGET_UNIT_WIDTH,
    POLICY_EXP_FIX,
)
from pydidas.core.utils import convert_special_chars_to_unicode
from pydidas.widgets.factory import EmptyWidget, PydidasLabel
from pydidas.widgets.parameter_config.base_param_io_widget import BaseParamIoWidget
from pydidas.widgets.parameter_config.param_io_widget_checkbox import (
    ParamIoWidgetCheckBox,
)
from pydidas.widgets.parameter_config.param_io_widget_combo_box import (
    ParamIoWidgetComboBox,
)
from pydidas.widgets.parameter_config.param_io_widget_file import ParamIoWidgetFile
from pydidas.widgets.parameter_config.param_io_widget_hdf5key import (
    ParamIoWidgetHdf5Key,
)
from pydidas.widgets.parameter_config.param_io_widget_lineedit import (
    ParamIoWidgetLineEdit,
)


AlignLeft = QtCore.Qt.AlignLeft
AlignVCenter = QtCore.Qt.AlignVCenter
_BOOL_CHOICES = [{True, False}, {True}, {False}]


class ParameterWidget(EmptyWidget):
    """
    A composite widget to display and modify a Parameter with name, value and unit.

    This widget is a wrapper and includes labels for name and unit and the
    respective Parameter edit widget which is selected based on the Parameter
    type and choices.

    This is the public widget should be added to the GUI to display and modify
    Parameters. It includes the following signals:

    sig_new_value : QtCore.Signal(str)
        Emitted when a new value is entered in the I/O widget. The new value is
         emitted as string representation.
    sig_value_changed : QtCore.Signal()
        Emitted when the value in the I/O widget has changed and been accepted.


    Parameters
    ----------
    param : pydidas.core.Parameter
        The associated Parameter.
    **kwargs : Any
        Additional keyword arguments. Supported keyword arguments are:

        width_text : float
            The relative width of the text field for the Parameter name.
            The default is defined in
            pydidas.core.constants.PARAM_WIDGET_TEXT_WIDTH.
        width_io : float
            The relative width of the input widget for the Parameter value.
            The default is defined in
            pydidas.core.constants.PARAM_WIDGET_EDIT_WIDTH.
        width_unit : float
            The relative width of the text field for the Parameter unit.
            The default is defined in
            pydidas.core.constants.PARAM_WIDGET_UNIT_WIDTH.
        linebreak : bool
            If True, the layout will include a linebreak between the name
            label and the I/O widget. The default is False.
    """

    sig_new_value = QtCore.Signal(str)
    sig_value_changed = QtCore.Signal()

    def __init__(
        self,
        param: Parameter,
        **kwargs: Any,
    ):
        EmptyWidget.__init__(self, **kwargs)
        self.setSizePolicy(*POLICY_EXP_FIX)
        self.layout().setSpacing(0)
        self.setToolTip(f"<qt>{html.escape(param.tooltip)}</qt>")

        self.param = param
        self._widgets: dict[str, QtWidgets.QWidget] = {}
        self.__store_config_from_kwargs(kwargs)

        self.__create_name_widget_if_required()
        self.__create_param_io_widget()
        self.__create_unit_widget_if_required()

        self._widgets["io"].sig_new_value.connect(self.set_param_value)
        self._widgets["io"].sig_new_value.connect(self.sig_new_value)
        self._widgets["io"].sig_value_changed.connect(self.sig_value_changed)

    @property
    def io_widget(self) -> BaseParamIoWidget:
        """
        Returns the I/O widget for the Parameter.

        Returns
        -------
        BaseParamIoWidget
            The I/O widget for the Parameter.
        """
        return self._widgets["io"]

    @property
    def _param_widget_class(self) -> Type[BaseParamIoWidget]:
        """Get the class of the Parameter I/O widget based on the Parameter."""
        if self.param.choices:
            if set(self.param.choices) in [{True, False}, {True}, {False}]:
                return ParamIoWidgetCheckBox
            return ParamIoWidgetComboBox
        if self.param.dtype == Path:
            return ParamIoWidgetFile
        if self.param.dtype == Hdf5key:
            return ParamIoWidgetHdf5Key
        return ParamIoWidgetLineEdit

    def __store_config_from_kwargs(self, kwargs: dict[str, Any]):
        """
        Set up the config from the kwargs formatting options.

        Parameters
        ----------
        kwargs : dict
            The calling kwargs.
        """
        _unit_preset = kwargs.get("width_unit", PARAM_WIDGET_UNIT_WIDTH)
        _text_preset = kwargs.get("width_text", PARAM_WIDGET_TEXT_WIDTH)
        _linebreak = kwargs.get("linebreak", False)

        _unit_width = _unit_preset if len(self.param.unit) > 0 else 0
        _io_width = kwargs.get("width_io", PARAM_WIDGET_EDIT_WIDTH)
        if _unit_width == 0:
            _io_width += _unit_preset
        self._config: dict[str, Any] = {
            "linebreak": _linebreak,
            "persistent_qsettings_ref": kwargs.get("persistent_qsettings_ref", None),
            "width_unit": _unit_width,
            "width_text": 1.0 if _linebreak else _text_preset,
            "width_io": kwargs.get(
                "width_io", (0.9 - _unit_width if _linebreak else _io_width)
            ),
            "layout_text": (0, 0, 1, 1 + 2 * _linebreak, ALIGN_CENTER_LEFT),
            "layout_io": (_linebreak, 1, 1, 2 - (_unit_width > 0), ALIGN_CENTER_LEFT),
            "layout_unit": (_linebreak, 2, 1, 1, ALIGN_CENTER_LEFT),
        }

    def __create_name_widget_if_required(self):
        """
        Create a widget with the Parameter's name if required.

        In the case of a
        """
        if self._param_widget_class == ParamIoWidgetCheckBox:
            return
        _display_txt = convert_special_chars_to_unicode(self.param.name) + ":"
        if self._font_metric_width_factor is None:
            _width_factor = None
        else:
            _width_factor = self._font_metric_width_factor * self._config["width_text"]
        self._widgets["label"] = PydidasLabel(
            _display_txt, margin=0, font_metric_width_factor=_width_factor
        )
        self.layout().addWidget(self._widgets["label"], *self._config["layout_text"])
        if not self._config["linebreak"]:
            self.layout().setColumnStretch(0, int(self._config["width_text"] * 100))

    def __create_param_io_widget(self):
        """
        Create an I/O widget for the Parameter based on its configuration and type.
        """
        kwargs = {
            "persistent_qsettings_ref": self._config["persistent_qsettings_ref"],
            "linebreak": self._config["linebreak"],
        }
        self._widgets["io"] = self._param_widget_class(self.param, **kwargs)
        if self._param_widget_class in (ParamIoWidgetFile, ParamIoWidgetHdf5Key):
            self._config["width_unit"] = 0
        try:
            self._widgets["io"].set_value(self.param.value)
        except UserConfigError:
            pass
        self.layout().addWidget(self._widgets["io"], *self._config["layout_io"])
        _width_col2 = int(100 * self._config["width_unit"])
        _width_col1 = int(100 * self._config["width_io"])
        _width_col0 = 100 - _width_col1 - _width_col2
        self.layout().setColumnStretch(1, _width_col1)
        if self._config["linebreak"]:
            self._widgets["io_spacer"] = EmptyWidget(sizePolicy=POLICY_EXP_FIX)
            self.layout().addWidget(self._widgets["io_spacer"], 1, 0, 1, 1)
            self.layout().setColumnStretch(0, _width_col0)
            self.layout().setColumnStretch(2, _width_col2)

    def __create_unit_widget_if_required(self):
        """
        Create a widget with the Parameter's unit text.
        """
        if self._config["width_unit"] == 0:
            return
        self._widgets["unit"] = PydidasLabel(
            convert_special_chars_to_unicode(self.param.unit),
            margin=3,
            font_metric_width_factor=(
                None
                if self._font_metric_width_factor is None
                else self._config["width_unit"] * self._font_metric_width_factor
            ),
        )
        self.layout().addWidget(self._widgets["unit"], *self._config["layout_unit"])
        self.layout().setColumnStretch(2, int(self._config["width_unit"] * 100))

    @QtCore.Slot(str)
    def set_param_value(self, value_str_repr: str):
        """
        Update the Parameter value with the entry from the widget.

        This method tries to update the Parameter value with the entry from
        the widget. If unsuccessful, an exception box will be opened and
        the widget input will be reset to the stored Parameter value.

        Parameters
        ----------
        value_str_repr : str
            The new value as string representation.
        """
        try:
            self.param.value = value_str_repr
        except (ValueError, UserConfigError):
            self._widgets["io"].set_value(self.param.value)
            raise

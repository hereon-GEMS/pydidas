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
from numbers import Real
from pathlib import Path
from typing import Any, Type

from qtpy import QtCore, QtWidgets

from pydidas.core import Hdf5key, Parameter, UserConfigError
from pydidas.core.constants import (
    ALIGN_CENTER_LEFT,
    FONT_METRIC_PARAM_EDIT_WIDTH,
    MINIMUN_WIDGET_DIMENSIONS,
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
        Additional keyword arguments. Note that many keywords supported by the
        generic mixin-class are ignored here because this is a composite widget.
        Note that the I/O has no width setting here because it is determined
        automatically based on the remaining space after allocating space for
        the name and unit fields.
        Supported keyword arguments are:

        width_text : float
            The relative width of the text field for the Parameter name.
            The default is defined in
            pydidas.core.constants.PARAM_WIDGET_TEXT_WIDTH.
        width_unit : float
            The relative width of the text field for the Parameter unit.
            The default is defined in
            pydidas.core.constants.PARAM_WIDGET_UNIT_WIDTH.
        linebreak : bool
            If True, the layout will include a linebreak between the name
            label and the I/O widget. The default is False.
        font_metric_width_factor : int | None
            The width of the widget in multiples of the font metric width. If None,
            the widget will use the default size policy. The default is
            pydidas.core.constants.FONT_METRIC_PARAM_EDIT_WIDTH.
    """

    sig_new_value = QtCore.Signal(str)
    sig_value_changed = QtCore.Signal()
    _MIN_VIS_UNIT_WIDTH = 5
    _MARGINS = 2
    _SPACING = 2

    def __init__(
        self,
        param: Parameter,
        **kwargs: Any,
    ):
        EmptyWidget.__init__(self, **kwargs)
        if not isinstance(self.font_metric_width_factor, Real):
            self.font_metric_width_factor = FONT_METRIC_PARAM_EDIT_WIDTH
        self.setSizePolicy(*POLICY_EXP_FIX)
        self.layout().setHorizontalSpacing(0)
        self.layout().setVerticalSpacing(self._SPACING)
        self.layout().setContentsMargins(0, self._MARGINS, 0, self._MARGINS)
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
        """Returns the I/O widget for the Parameter."""
        return self._widgets["io"]

    @property
    def display_value(self) -> str:
        """
        Get the current display value from the I/O widget.

        Returns
        -------
        str
            The current display value as string.
        """
        return self._widgets["io"].current_text

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
        _linebreak = int(kwargs.get("linebreak", False))
        _expected_width = self.font_metric_width_factor
        _unit_width = (
            0
            if (len(self.param.unit) == 0 or kwargs.get("width_unit", 1) == 0)
            else max(
                self._MIN_VIS_UNIT_WIDTH,
                self.fm_w * kwargs.get("width_unit", PARAM_WIDGET_UNIT_WIDTH),
            )
        )
        _text_width = self.fm_w * (
            max(_linebreak, kwargs.get("width_text", PARAM_WIDGET_TEXT_WIDTH))
        )
        # modify presets if checkbox is used to ignore linebreaks and text labels:
        if self._param_widget_class == ParamIoWidgetCheckBox:
            _linebreak = False
            _text_width = 0
        # modify presets to ignore unit for files or Hdf5keys:
        if self._param_widget_class in (ParamIoWidgetFile, ParamIoWidgetHdf5Key):
            _unit_width = 0
        # define I/O width based on available space:
        _io_width = (
            (self.fm_w * 0.9 - _unit_width)
            if _linebreak
            else self.font_metric_width_factor - _unit_width - _text_width
        )
        self._config: dict[str, Any] = {
            "linebreak": bool(_linebreak),
            "persistent_qsettings_ref": kwargs.get("persistent_qsettings_ref", None),
            "width_unit": _unit_width,
            "width_text": _text_width,
            "width_io": _io_width,
            "layout_text": (0, 0, 1, 1 + 2 * _linebreak, ALIGN_CENTER_LEFT),
            "layout_io": (_linebreak, 1, 1, 2 - (_unit_width > 0), ALIGN_CENTER_LEFT),
            "layout_unit": (_linebreak, 2, 1, 1, ALIGN_CENTER_LEFT),
        }

    def __create_name_widget_if_required(self):
        """
        Create a widget with the Parameter's name if required.
        """
        if self._param_widget_class == ParamIoWidgetCheckBox:
            return
        _display_txt = convert_special_chars_to_unicode(self.param.name) + ":"
        self._widgets["label"] = PydidasLabel(
            _display_txt,
            font_metric_height_factor=1,
            font_metric_width_factor=self._config["width_text"],
            margin=0,
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
            "font_metric_height_factor": 1,
            "font_metric_width_factor": self._config["width_io"],
        }
        self._widgets["io"] = self._param_widget_class(self.param, **kwargs)
        self._widgets["io"].set_value(self.param.value)
        self.layout().addWidget(self._widgets["io"], *self._config["layout_io"])
        if self._config["linebreak"]:
            self._widgets["io_spacer"] = EmptyWidget(
                size_hint_width=20,
                sizePolicy=POLICY_EXP_FIX,
                font_metric_width_factor=0.1 * self._font_metric_width_factor,
                minimum_width=0,
            )
            self.layout().addWidget(self._widgets["io_spacer"], 1, 0, 1, 1)

    def __create_unit_widget_if_required(self):
        """
        Create a widget with the Parameter's unit text.
        """
        if self._config["width_unit"] == 0:
            return
        self._widgets["unit"] = PydidasLabel(
            convert_special_chars_to_unicode(self.param.unit),
            font_metric_height_factor=1,
            font_metric_width_factor=self._config["width_unit"],
            margin=3,
            minimum_width=0,
        )
        self.layout().addWidget(self._widgets["unit"], *self._config["layout_unit"])
        self.layout().setColumnStretch(2, int(self._config["width_unit"] * 100))

    def sizeHint(self) -> QtCore.QSize:  # noqa C0103
        """
        Set a reasonable sizeHint based on the font metrics and configuration.

        Returns
        -------
        QtCore.QSize
            The widget sizeHint
        """
        if not hasattr(self, "_widgets"):
            return super().sizeHint()
        _width = int(self.fm_w * self._qtapp.font_char_width)
        _height = self._widgets["io"].height() + 2 * self._MARGINS
        if self._config.get("linebreak"):
            _height += self._widgets["label"].height() + self._SPACING
        return QtCore.QSize(_width, max(_height, MINIMUN_WIDGET_DIMENSIONS))

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

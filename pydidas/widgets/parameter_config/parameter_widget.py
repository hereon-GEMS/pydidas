# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ParameterWidget"]


import html
from pathlib import Path

from qtpy import QtCore, QtWidgets

from ...core import Hdf5key, UserConfigError
from ...core.constants import (
    ALIGN_TOP_LEFT,
    PARAM_INPUT_EDIT_WIDTH,
    PARAM_INPUT_TEXT_WIDTH,
    PARAM_INPUT_UNIT_WIDTH,
    PARAM_INPUT_WIDGET_HEIGHT,
    PARAM_INPUT_WIDGET_WIDTH,
)
from ...core.utils import apply_qt_properties, convert_special_chars_to_unicode
from ..factory import create_label
from .param_io_widget_combo_box import ParamIoWidgetComboBox
from .param_io_widget_file import ParamIoWidgetFile
from .param_io_widget_hdf5key import ParamIoWidgetHdf5Key
from .param_io_widget_lineedit import ParamIoWidgetLineEdit


class ParameterWidget(QtWidgets.QWidget):
    """
    A combined widget to display and modify a Parameter with name, value and unit.

    This widget is a wrapper and includes labels for name and unit and the
    respective Parameter edit widget which is selected based on the Parameter
    type and choices.

    This is the public widget should be added to the GUI to display and modify
    Parameters.

    Parameters
    ----------
    param : pydidas.core.Parameter
        The associated Parameter.
    parent : QtWidget, optional
        The parent widget. The default is None.
    **kwargs : dict
        Additional keyword arguments
    """

    io_edited = QtCore.Signal(str)

    def __init__(self, param, parent=None, **kwargs):
        QtWidgets.QWidget.__init__(self, parent)
        self.__set_size_from_kwargs(kwargs)
        self.__store_config_from_kwargs(kwargs)

        self.param = param
        self.setLayout(QtWidgets.QGridLayout())
        apply_qt_properties(
            self.layout(),
            contentsMargins=(0, 0, 0, 0),
            spacing=5,
            alignment=ALIGN_TOP_LEFT,
        )
        self.layout().setColumnStretch(1, 1)
        self.name_widget = self.__get_name_widget()
        if self.config["width_unit"] > 0:
            self.unit_widget = self.__get_unit_widget()
        self.io_widget = self.__get_param_io_widget(
            width=self.config["width_io"],
            persistent_qsettings_ref=kwargs.get("persistent_qsettings_ref", None),
        )
        _text_w_args, _input_w_args, _unit_w_args = self.__get_layout_args_for_widgets()
        self.layout().addWidget(self.name_widget, *_text_w_args)
        self.layout().addWidget(self.io_widget, *_input_w_args)
        if self.config["width_unit"] > 0:
            self.layout().addWidget(self.unit_widget, *_unit_w_args)

        self.io_widget.io_edited.connect(self.__emit_io_changed)
        self.io_widget.io_edited.connect(self.__set_param_value)
        apply_qt_properties(self, **kwargs)

    def __set_size_from_kwargs(self, kwargs):
        """
        Set the size of the widget based on the input keyword arguments.

        Parameters
        ----------
        kwargs : dict
            The keyword arguments.
        """
        _linebreak = kwargs.get("linebreak", False)
        _width = kwargs.get("width_total", PARAM_INPUT_WIDGET_WIDTH)
        _height = PARAM_INPUT_WIDGET_HEIGHT + _linebreak * (
            PARAM_INPUT_WIDGET_HEIGHT + 4
        )
        self.setFixedWidth(_width)
        self.setFixedHeight(_height)

    def __store_config_from_kwargs(self, kwargs):
        """
        Get the config from the kwargs formatting options.

        Parameters
        ----------
        parent : QtWidgets.QWidget
            The parent widget.
        **kwargs : dict
            All possible formatting options.

        Returns
        -------
        config : dict
            The full formatting options, updated with the default values.
        """
        _width = kwargs.get("width_total", PARAM_INPUT_WIDGET_WIDTH)
        _width_unit = kwargs.get("width_unit", PARAM_INPUT_UNIT_WIDTH)
        config = {
            "linebreak": kwargs.get("linebreak", False),
            "valign_io": kwargs.get("valign_io", QtCore.Qt.AlignVCenter),
            "valign_text": kwargs.get("valign_text", QtCore.Qt.AlignVCenter),
        }
        if config["linebreak"]:
            config["width_text"] = kwargs.get("width_text", _width - 10)
            config["width_io"] = kwargs.get("width_io", _width - _width_unit - 20)
            config["halign_text"] = kwargs.get("halign_text", QtCore.Qt.AlignLeft)
            config["halign_io"] = kwargs.get("halign_io", QtCore.Qt.AlignRight)
        else:
            config["width_text"] = kwargs.get("width_text", PARAM_INPUT_TEXT_WIDTH)
            config["width_io"] = kwargs.get("width_io", PARAM_INPUT_EDIT_WIDTH)
            config["halign_text"] = kwargs.get("halign_text", QtCore.Qt.AlignLeft)
            config["halign_io"] = kwargs.get("halign_io", QtCore.Qt.AlignRight)
        config["width_unit"] = _width_unit
        config["width_total"] = _width
        config["halign_unit"] = kwargs.get("halign_unit", QtCore.Qt.AlignLeft)
        config["valign_unit"] = kwargs.get("valign_unit", QtCore.Qt.AlignVCenter)
        self.config = config

    def __get_name_widget(self):
        """
        Get a widget with the Parameter's name.

        Parameters
        ----------
        config : dict
            The configuration dictionary.

        Returns
        -------
        QtWidgets.QLabel
            The label with the Parameter's name.
        """
        _text = convert_special_chars_to_unicode(self.param.name) + ":"
        return create_label(
            _text,
            fixedWidth=self.config["width_text"],
            fixedHeight=20,
            toolTip=f"<qt>{html.escape(self.param.tooltip)}</qt>",
            margin=0,
        )

    def __get_param_io_widget(self, **kwargs: dict) -> QtWidgets.QWidget:
        """
        Get the specific Parameter I/O widget for the Parameter configuration and type.

        Parameters
        ----------
        kwargs: dict
            Additional configuration dictionary.

        Returns
        -------
        QtWidgets.QWidget
            The parameter I/O widget.
        """
        if self.param.choices:
            _widget = ParamIoWidgetComboBox(self.param, **kwargs)
        else:
            if self.param.dtype == Path:
                _widget = ParamIoWidgetFile(self.param, **kwargs)
            elif self.param.dtype == Hdf5key:
                _widget = ParamIoWidgetHdf5Key(self.param, **kwargs)
            else:
                _widget = ParamIoWidgetLineEdit(self.param, **kwargs)
        try:
            _widget.set_value(self.param.value)
        except UserConfigError:
            pass
        return _widget

    def __get_unit_widget(self):
        """
        Get a widget with the Parameter's unit text.

        Parameters
        ----------
        config : dict
            The configuration dictionary.

        Returns
        -------
        QtWidgets.QLabel
            The label with the Parameter's unit text.
        """
        _text = convert_special_chars_to_unicode(self.param.unit)
        return create_label(
            _text,
            fixedWidth=self.config["width_unit"],
            fixedHeight=20,
            toolTip=f"<qt>{html.escape(self.param.tooltip)}</qt>",
            margin=0,
        )

    def __get_layout_args_for_widgets(self):
        """
        Get the layout insertion arguments based on config.

        Parameters
        ----------
        config : dict
            The dictionary with the layout formatting arguments.

        Returns
        -------
        txt_args : tuple
            The tuple with the layout formatting args for the name widget.
        io_args : tuple
            The tuple with the layout formatting args for the io widget.
        unit_args : tuple
            The tuple with the layout formatting args for the unit widget.
        """
        _iline = int(self.config["linebreak"])
        _iunit = int(self.config["width_unit"] > 0)
        _txtargs = (
            0,
            0,
            1,
            1 + 2 * _iline,
            self.config["valign_text"] | self.config["halign_text"],
        )
        _ioargs = (
            _iline,
            1,
            1,
            2 - _iunit,
            self.config["valign_io"] | self.config["halign_io"],
        )
        _unitargs = (
            _iline,
            2,
            1,
            1,
            self.config["valign_text"] | self.config["halign_text"],
        )
        return _txtargs, _ioargs, _unitargs

    @QtCore.Slot(str)
    def __emit_io_changed(self, value):
        """
        Forward the io_changed signal from the IO widget.

        Parameters
        ----------
        value : str
            The value emitted by the IO widget.
        """
        self.io_edited.emit(value)

    @QtCore.Slot()
    def __set_param_value(self):
        """
        Update the Parameter value with the entry from the widget.

        This method tries to update the Parameter value with the entry from
        the widget. If unsuccessful, an exception box will be opened and
        the widget input will be reset to the stored Parameter value.

        Parameters
        ----------
        param : Parameter
            A Parameter class instance from the plugin.
        widget : QWidget
            The input widget used for editing the parameter value.
        """
        try:
            self.param.value = self.io_widget.get_value()
        except ValueError:
            self.io_widget.set_value(self.param.value)
            raise

    def sizeHint(self):
        """
        Set the Qt sizeHint to be the widget's size.

        Returns
        -------
        QtCore.QSize
            The size of the widget.
        """
        return QtCore.QSize(self.width(), self.height())

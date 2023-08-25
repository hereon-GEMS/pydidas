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
from typing import Union

from qtpy import QtCore, QtWidgets

from ...core import Hdf5key, Parameter, UserConfigError
from ...core.constants import (
    PARAM_WIDGET_EDIT_WIDTH,
    PARAM_WIDGET_TEXT_WIDTH,
    PARAM_WIDGET_UNIT_WIDTH,
    POLICY_EXP_FIX,
)
from ...core.utils import apply_qt_properties, convert_special_chars_to_unicode
from ..factory import EmptyWidget, PydidasLabel, PydidasWidgetWithGridLayout
from .param_io_widget_combo_box import ParamIoWidgetComboBox
from .param_io_widget_file import ParamIoWidgetFile
from .param_io_widget_hdf5key import ParamIoWidgetHdf5Key
from .param_io_widget_lineedit import ParamIoWidgetLineEdit


class ParameterWidget(PydidasWidgetWithGridLayout):
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

    def __init__(
        self,
        param: Parameter,
        parent: Union[QtWidgets.QWidget, None] = None,
        **kwargs: dict,
    ):
        PydidasWidgetWithGridLayout.__init__(self, parent, **kwargs)
        self.setSizePolicy(*POLICY_EXP_FIX)
        self.layout().setHorizontalSpacing(0)
        self.setToolTip(f"<qt>{html.escape(param.tooltip)}</qt>")

        self.param = param
        self._widgets = {}
        self.__store_config_from_kwargs(kwargs)
        self.__store_layout_args_for_widgets()

        self.__create_name_widget()
        self.__create_param_io_widget()
        if self._config["width_unit"] > 0:
            self.__create_unit_widget()
        self.io_widget = self._widgets["io"]

        self._widgets["io"].io_edited.connect(self.__emit_io_changed)
        self._widgets["io"].io_edited.connect(self.__set_param_value)
        apply_qt_properties(self, **kwargs)

    def __store_config_from_kwargs(self, kwargs: dict):
        """
        Get the config from the kwargs formatting options.

        Parameters
        ----------
        kwargs : dict
            The calling kwargs.
        """
        _width_unit = kwargs.get("width_unit", PARAM_WIDGET_UNIT_WIDTH)
        config = {
            "linebreak": kwargs.get("linebreak", False),
            "persistent_qsettings_ref": kwargs.get("persistent_qsettings_ref", None),
        }
        if config["linebreak"]:
            config["width_text"] = 1.0
            config["width_io"] = kwargs.get("width_io", 0.8 - _width_unit)
        else:
            config["width_text"] = kwargs.get("width_text", PARAM_WIDGET_TEXT_WIDTH)
            config["width_io"] = kwargs.get("width_io", PARAM_WIDGET_EDIT_WIDTH)
        config["width_unit"] = _width_unit if len(self.param.unit) > 0 else 0
        config["align_text"] = QtCore.Qt.AlignVCenter | kwargs.get(
            "halign_text", QtCore.Qt.AlignLeft
        )
        config["align_io"] = QtCore.Qt.AlignVCenter | kwargs.get(
            "halign_io", QtCore.Qt.AlignLeft
        )
        config["align_unit"] = QtCore.Qt.AlignVCenter | kwargs.get(
            "halign_unit", QtCore.Qt.AlignLeft
        )
        self._config = config

    def __store_layout_args_for_widgets(self):
        """
        Store the layout insertion arguments based on the config.
        """
        _linebreak = int(self._config["linebreak"])
        _show_unit = int(self._config["width_unit"] > 0)
        self._config["layout_text"] = (
            0,
            0,
            1,
            1 + 2 * _linebreak,
            self._config["align_text"],
        )
        self._config["layout_io"] = (
            _linebreak,
            1,
            1,
            2 - _show_unit,
            self._config["align_io"],
        )
        self._config["layout_unit"] = (_linebreak, 2, 1, 1, self._config["align_text"])

    def __create_name_widget(self):
        """
        Create a widget with the Parameter's name.
        """
        _text = convert_special_chars_to_unicode(self.param.name) + ":"
        self._widgets["name_label"] = PydidasLabel(_text, margin=0)
        self._widgets["name_container"] = EmptyWidget(sizePolicy=POLICY_EXP_FIX)
        self.layout().addWidget(
            self._widgets["name_container"], *self._config["layout_text"]
        )
        self._widgets["name_container"].layout().addWidget(self._widgets["name_label"])
        if not self._config["linebreak"]:
            self.layout().setColumnStretch(0, int(self._config["width_text"] * 100))

    def __create_unit_widget(self):
        """
        Create a widget with the Parameter's unit text.
        """
        _text = convert_special_chars_to_unicode(self.param.unit)
        self._widgets["unit_label"] = PydidasLabel(_text, margin=3)
        self._widgets["unit_container"] = EmptyWidget(sizePolicy=POLICY_EXP_FIX)
        self.layout().addWidget(
            self._widgets["unit_container"], *self._config["layout_unit"]
        )
        self._widgets["unit_container"].layout().addWidget(self._widgets["unit_label"])
        self.layout().setColumnStretch(2, int(self._config["width_unit"] * 100))

    def __create_param_io_widget(self):
        """
        Create an I/O widget for the Parameter based on its configuration and type.
        """
        kwargs = {"persistent_qsettings_ref": self._config["persistent_qsettings_ref"]}
        if self.param.choices:
            _widget = ParamIoWidgetComboBox(self.param, **kwargs)
        else:
            if self.param.dtype == Path:
                _widget = ParamIoWidgetFile(self.param, **kwargs)
                self._config["width_unit"] = 0
            elif self.param.dtype == Hdf5key:
                _widget = ParamIoWidgetHdf5Key(self.param, **kwargs)
                self._config["width_unit"] = 0
            else:
                _widget = ParamIoWidgetLineEdit(self.param, **kwargs)
        try:
            _widget.set_value(self.param.value)
        except UserConfigError:
            pass
        self._widgets["io"] = _widget
        self._widgets["io"].setSizePolicy(*POLICY_EXP_FIX)
        self.layout().addWidget(self._widgets["io"], *self._config["layout_io"])
        if self._config["linebreak"]:
            self._widgets["io_spacer"] = EmptyWidget(sizePolicy=POLICY_EXP_FIX)
            self.layout().addWidget(self._widgets["io_spacer"], 1, 0, 1, 1)
            self.layout().setColumnStretch(0, 10)
            self.layout().setColumnStretch(
                1, int(100 * (1 - self._config["width_unit"]))
            )
        else:
            self.layout().setColumnStretch(
                1,
                int(
                    100 * (1 - self._config["width_unit"] - self._config["width_text"])
                ),
            )

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
            self.param.value = self._widgets["io"].get_value()
        except ValueError:
            self._widgets["io"].set_value(self.param.value)
            raise

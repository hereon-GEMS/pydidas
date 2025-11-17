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
Module with the ParamIoWidgetCheckBox class used to edit boolean Parameters.
There are no typechecks implemented in the widget and any input which is
accepted by the Parameter is valid.
"""

__author__ = ("Nonni Heere", "Malte Storm")
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ParamIoWidgetCheckBox"]


from typing import Any

from qtpy import QtCore

from pydidas.core import Parameter
from pydidas.core.utils import IS_QT6
from pydidas.widgets.factory import PydidasCheckBox
from pydidas.widgets.parameter_config.base_param_io_widget import (
    BaseParamIoWidgetMixIn,
)


class ParamIoWidgetCheckBox(BaseParamIoWidgetMixIn, PydidasCheckBox):
    """Widget for Parameters with True/False choices only."""

    @staticmethod
    def __convert_to_bool(value: int | str) -> bool:
        """
        Convert input to boolean.

        Parameters
        ----------
        value : int | str
            The input value to check.

        Returns
        -------
        bool
            The input value, with 0/1 converted to True or False
        """
        return value in ["1", 1, "True", "true"]

    def __init__(self, param: Parameter, **kwargs: Any):
        """
        Initialize the widget.

        Init method to set up the widget and set the links to the parameter
        and Qt parent widget.

        Parameters
        ----------
        param : Parameter
            A Parameter instance.
        **kwargs : Any
            Supported keyword arguments are all supported arguments of
             PydidasCheckBox.
        """
        PydidasCheckBox.__init__(self, **kwargs)
        BaseParamIoWidgetMixIn.__init__(self, param)
        self.setText(param.name)
        self.setEnabled(True in param.choices and False in param.choices)
        self.update_widget_value(param.value)
        if IS_QT6:
            self.checkStateChanged.connect(self.emit_signal)
        else:
            self.stateChanged.connect(self.emit_signal)

    @property
    def current_text(self) -> str:
        """
        Get the text of the checkbox.

        Returns
        -------
        str
            The text of the checkbox.
        """
        return "True" if self.isChecked() else "False"

    def update_widget_value(self, value: Any) -> None:
        """
        Update the widget value without emitting signals.

        Parameters
        ----------
        value : Any
            The new value to set in the widget.
        """
        with QtCore.QSignalBlocker(self):
            self.setChecked(self.__convert_to_bool(value))

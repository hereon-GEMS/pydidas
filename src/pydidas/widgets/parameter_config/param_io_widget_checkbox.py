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

__author__ = "Nonni Heere"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ParamIoWidgetCheckBox"]


from typing import Union

import qtpy as __qtpy

from pydidas.core import Parameter
from pydidas.widgets.factory import PydidasCheckBox
from pydidas.widgets.parameter_config.base_param_io_widget_mixin import (
    BaseParamIoWidgetMixIn,
)


IS_QT6 = __qtpy.QT_VERSION[0] == "6"


class ParamIoWidgetCheckBox(BaseParamIoWidgetMixIn, PydidasCheckBox):
    """Widgets for I/O during plugin parameter editing with boolean choices."""

    def __init__(self, param: Parameter, **kwargs: dict):
        """
        Initialize the widget.

        Init method to set up the widget and set the links to the parameter
        and Qt parent widget.

        Parameters
        ----------
        param : Parameter
            A Parameter instance.
        width : int, optional
            The width of the IOwidget.
        """
        PydidasCheckBox.__init__(self)
        BaseParamIoWidgetMixIn.__init__(self, param, **kwargs)
        param.value = self.__convert_bool(param.value)
        if IS_QT6:
            self.checkStateChanged.connect(self.emit_signal)
        else:
            self.stateChanged.connect(self.emit_signal)
        self.set_value(param.value)
        self.setText(param.name)
        self.setEnabled(set(param.choices) == {True, False})

    def __convert_bool(self, value: Union[int, str]) -> bool:
        """
        Convert boolean strings to bool.

        This conversion is necessary because boolean "0" and "1" cannot be
        interpreted as "True" and "False" straight away.

        Parameters
        ----------
        value : Union[int, str]
            The input value from the field. This could be any object.

        Returns
        -------
        bool
            The input value, with 0/1 converted to True or False
        """
        return True if value == "1" or value == 1 else False

    def emit_signal(self):
        """
        Emit a signal that the value has been edited.

        This method emits a signal that the combobox selection has been
        changed and the Parameter value needs to be updated.
        """
        _cur_value = self.isChecked()
        if _cur_value != self._old_value:
            self._old_value = _cur_value
            self.io_edited.emit("True" if _cur_value else "False")

    def get_value(self) -> object:
        """
        Get the current value from the combobox to update the Parameter value.

        Returns
        -------
        object
            Bool value of the checkbox.
        """
        return self.isChecked()

    def set_value(self, value: str):
        """
        Check or uncheck the checkbox.

        This method is used to set the checkbox value.


        Parameters
        ----------
        value : str
            The value to be set, "0" or "1".
        """
        value = self.__convert_bool(value)
        self._old_value = value
        self.setChecked(value)

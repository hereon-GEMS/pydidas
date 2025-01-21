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
Module with the ParamIoWidgetLineEdit class used to edit free-text Parameters.
There are no typechecks implemented in the widget and any input which is
accepted by the Parameter is valid.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ParamIoWidgetLineEdit"]


from numbers import Real

import numpy as np
from qtpy import QtCore

from pydidas.core import Parameter
from pydidas.core.constants import FLOAT_DISPLAY_ACCURACY, POLICY_EXP_FIX
from pydidas.widgets.factory import PydidasLineEdit
from pydidas.widgets.parameter_config.base_param_io_widget_mixin import (
    BaseParamIoWidgetMixIn,
)


class ParamIoWidgetLineEdit(BaseParamIoWidgetMixIn, PydidasLineEdit):
    """
    Widgets for I/O of Parameter editing without predefined choices.

    Parameters
    ----------
    param : Parameter
        A Parameter instance.
    **kwargs : dict
        Any additional kwargs.
    """

    io_edited = QtCore.Signal(str)

    def __init__(self, param: Parameter, **kwargs: dict):
        PydidasLineEdit.__init__(self, parent=kwargs.get("parent", None))
        BaseParamIoWidgetMixIn.__init__(self, param, **kwargs)
        self.set_validator(param)
        self.set_value(param.value)
        self.editingFinished.connect(self.emit_signal)
        self.setSizePolicy(*POLICY_EXP_FIX)

    def emit_signal(self):
        """
        Emit a signal that the value has been edited.

        This method emits a signal that the combobox selection has been
        changed and the Parameter value needs to be updated.
        """
        _cur_value = self.text()
        if _cur_value != self._old_value:
            self._old_value = _cur_value
            self.io_edited.emit(_cur_value)

    def get_value(self) -> object:
        """
        Get the current value from the combobox to update the Parameter value.

        Returns
        -------
        type
            The text converted to the required datatype (int, float, path)
            to update the Parameter value.
        """
        _text = self.text()
        _value = self.get_value_from_text(_text)
        if _text == "" and _value is None:
            self.setText("None")
        return _value

    def set_value(self, value: object):
        """
        Set the input field's value.

        This method changes the combobox selection to the specified value.
        Warning: This method will *not* update the connected parameter value.

        Parameters
        ----------
        value : object
            The new value to be displayed in the widget.
        """
        if self._ptype == Real and value is not None and np.isfinite(value):
            value = np.round(value, decimals=FLOAT_DISPLAY_ACCURACY)
        self._old_value = str(value)
        self.setText(f"{value}")

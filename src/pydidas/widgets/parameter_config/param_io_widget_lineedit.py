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


import numbers
from typing import Any

from qtpy import QtGui

from pydidas.core import Parameter
from pydidas.core.constants import (
    FLOAT_VALIDATOR,
    POLICY_EXP_FIX,
    QT_REG_EXP_FLOAT_VALIDATOR,
    QT_REG_EXP_INT_VALIDATOR,
)
from pydidas.widgets.factory import PydidasLineEdit
from pydidas.widgets.parameter_config.base_param_io_widget import (
    BaseParamIoWidgetMixIn,
)


class ParamIoWidgetLineEdit(BaseParamIoWidgetMixIn, PydidasLineEdit):
    """
    Widgets for I/O of Parameter editing without predefined choices.

    Parameters
    ----------
    param : Parameter
        A Parameter instance.
    **kwargs : Any
        Any additional kwargs. All kwargs are passed to the PydidasLineEdit
        constructor.
    """

    def __init__(self, param: Parameter, **kwargs: Any):
        PydidasLineEdit.__init__(self, **kwargs)
        BaseParamIoWidgetMixIn.__init__(self, param)
        self.update_validator()
        self.setText(f"{param.value}")
        self.editingFinished.connect(self.emit_signal)
        self.setSizePolicy(*POLICY_EXP_FIX)  # noqa E1120, E1121

    @property
    def current_text(self) -> str:
        """
        Get the current text in the line edit.

        Returns
        -------
        str
            The current text in the line edit.
        """
        return self.text()

    def update_widget_value(self, input: Any) -> None:
        """
        Update the widget value.

        Parameters
        ----------
        input : Any
            The new value to set in the widget.
        """
        self.setText(f"{input}")

    def update_validator(self) -> None:
        """Update the widget's validator based on the Parameter's configuration."""
        _validator = None
        if self._linked_param.dtype == numbers.Integral:
            if self._linked_param.allow_None:
                _validator = QT_REG_EXP_INT_VALIDATOR
            else:
                _validator = QtGui.QIntValidator()
        elif self._linked_param.dtype == numbers.Real:
            if self._linked_param.allow_None:
                _validator = QT_REG_EXP_FLOAT_VALIDATOR
            else:
                _validator = FLOAT_VALIDATOR
        if _validator is not None:
            self.setValidator(_validator)

# This file is part of pydidas.
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
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the ParamIoWidgetLineEdit class used to edit free-text Parameters.
There are no typechecks implemented in the widget and any input which is
accepted by the Parameter is valid.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ParamIoWidgetLineEdit"]


import numbers
from typing import Any

import numpy as np
from qtpy import QtCore, QtGui

from pydidas.core import Parameter, UserConfigError
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

    def __init__(self, param: Parameter, **kwargs: Any) -> None:
        self._precision = kwargs.pop("precision", 10)
        PydidasLineEdit.__init__(self, **kwargs)
        BaseParamIoWidgetMixIn.__init__(self, param)
        self._current_text_value: Any = None
        self._user_edited: bool = False
        if param.dtype is not numbers.Real:
            self._precision = None
        self.update_validator()
        self.textEdited.connect(self._mark_as_user_edited)
        self.editingFinished.connect(self._round_on_editing_finished)
        self.setSizePolicy(*POLICY_EXP_FIX)  # noqa E1120, E1121
        self.setText(param.value)

    def setText(self, value: Any) -> None:
        """
        Set the text in the line edit.

        This implementation also sets the precision if the linked Parameter
        holds a floating point value.

        Parameters
        ----------
        value : Any
            The text to be set in the line edit.
        """
        display_value = value
        if self._precision is not None and value not in [None, "None"]:
            try:
                _float_val = float(value)
                if np.isfinite(_float_val):
                    display_value = np.round(_float_val, self._precision)
            except (TypeError, ValueError):
                raise UserConfigError(
                    f"The given value `{value}` for the Parameter "
                    f"`{self._linked_param.refkey}` is not a valid floating point "
                    "value and cannot be converted to a floating point value."
                )
        self._current_text_value = str(value)
        super().setText(f"{display_value}")

    def update_display_value(self, value: Any) -> None:
        """
        Update the displayed value in the line edit.

        This method is defined in the BaseParamIoWidgetMixIn and is called
        by the ParameterWidget when the Parameter value is updated.
        Therefore, this alias is required.
        """
        self.setText(value)

    @property
    def current_text(self) -> str:
        """
        Get the current text in the line edit.

        Returns
        -------
        str
            The current text in the line edit.
        """
        return self._current_text_value

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

    @QtCore.Slot(str)
    def _mark_as_user_edited(self, _text: str) -> None:
        """
        Mark the QLineEdit input as being edited by the user.

        The `textEdited` signal - which is connected to this slot - is
        only emitted on manual edits, not on programmatic changes like
        `setText`.

        Parameters
        ----------
        _text : str
            The current text in the line edit (unused; received from the
            `textEdited` signal).
        """
        self._user_edited = True

    @QtCore.Slot()
    def _round_on_editing_finished(self) -> None:
        """
        Apply the precision fix, if necessary, before emitting signals.

        For all ParameterWidgets without precision or on programmatic changes,
        simply skip this step and emit the signal directly.
        """
        if not self._user_edited or self._precision is None:
            self.emit_signal()
            return
        self._user_edited = False
        with QtCore.QSignalBlocker(self):
            self.setText(self.text())
        self.emit_signal()

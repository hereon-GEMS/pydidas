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
Module with the BaseParamIoWidgetMixIn base class which all widgets for editing
Parameters should inherit from (in addition to their respective QWidget).
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["BaseParamIoWidgetMixIn", "BaseParamIoWidget"]


import numbers
import pathlib
from typing import Any, Type

import numpy as np
from numpy import nan, ndarray
from qtpy import QtCore, QtWidgets

from pydidas.core import Hdf5key, Parameter, UserConfigError
from pydidas.core.constants import (
    FLOAT_DISPLAY_ACCURACY,
    POLICY_EXP_FIX,
)
from pydidas.core.utils import NumpyParser


class BaseParamIoWidgetMixIn:
    """
    Base mixin class of widgets for I/O during Parameter editing.

    This class is intended to be used as a mixin in combination with a QWidget
    subclass to create widgets that can edit Parameter values.
    """

    sig_new_value = QtCore.Signal(str)
    sig_value_changed = QtCore.Signal()

    _SUPPORTED_TYPE_STRINGS = {"true": True, "false": False, "nan": nan, "none": None}
    _TYPE_CONVERTERS: dict[Type, Type | Any] = {
        numbers.Integral: int,
        numbers.Real: float,
        pathlib.Path: pathlib.Path,
        Hdf5key: Hdf5key,
        ndarray: NumpyParser,
    }

    def __init__(self, param: Parameter) -> None:
        self._linked_param = param
        self._old_value = None
        self.setSizePolicy(*POLICY_EXP_FIX)  # type: ignore[attr-defined]

    @property
    def current_text(self) -> str:
        """
        Get the current value as string.

        This method needs to be implemented by the subclass.

        Returns
        -------
        str
            The current text from the widget.
        """
        raise NotImplementedError

    @property
    def current_choices(self) -> list[str] | None:
        """
        Get the current list of choices in the widget.

        This method needs to be implemented by the subclass, if required.

        Returns
        -------
        list[str] | None
            The current list of choices in the widget, or None if not applicable.
        """
        return None

    def update_widget_value(self, value: Any) -> None:
        """
        Update the widget display to show the given value.

        This method needs to be implemented by the subclass while ensuring that
        no signals are emitted during the update.

        Parameters
        ----------
        value : Any
            The new value to be displayed in the widget.
        """
        raise NotImplementedError

    def is_special_type_string(self, text: str) -> bool:
        """
        Check if the input string is a special type string.

        Parameters
        ----------
        text : str
            The input string.

        Returns
        -------
        bool
            True if the input string is a special type string, False otherwise.
        """
        return text.strip().lower() in self._SUPPORTED_TYPE_STRINGS

    def special_type_from_string(self, text: str) -> Any:
        """
        Convert a string to the associated special type.

        Parameters
        ----------
        text : str
            The input string.

        Returns
        -------
        Any
            The input string converted to the appropriate datatype.
        """
        _input = text.strip().lower()
        return self._SUPPORTED_TYPE_STRINGS.get(_input, text)

    def get_value(self) -> Any:
        """
        Get the value from the input field.

        Returns
        -------
        Any
            The text converted to the datatype (int, float, Path) specified
            by the linked Parameter.
        """
        _text = self.current_text
        if self.is_special_type_string(_text):
            return self.special_type_from_string(_text)
        if (
            _text == ""
            and self._linked_param.allow_None
            and issubclass(self._linked_param.dtype, numbers.Real)
        ):
            return None
        try:
            _converter = self._TYPE_CONVERTERS.get(self._linked_param.dtype, None)
            if _converter is not None:
                return _converter(_text)  # noqa
        except ValueError as _error:
            _msg = str(_error).capitalize()
            raise UserConfigError(f'ValueError! {_msg} Input text was "{_text}"')
        return _text

    def set_value(self, value: Any) -> None:
        """
        Set the input field's value.

        This method changes the IO widget selection to the specified value.

        Warning: This method will *not* update the connected Parameter value.

        Parameters
        ----------
        value : Any
            The new value to be displayed in the widget.
        """
        if (
            self._linked_param.dtype == numbers.Real
            and value is not None
            and np.isfinite(value)
        ):
            value = np.round(value, decimals=FLOAT_DISPLAY_ACCURACY)
        self.update_widget_value(value)
        self.emit_signal()

    def set_unique_ref_name(self, name: str) -> None:
        """
        Set a unique reference.

        This reference name can be used to identify the Parameter in the
        QSettings, for example, to save the file dialog's current directory.

        This method needs to be implemented by the subclass, if required.

        Parameters
        ----------
        name : str
            The unique identifier to reference this Parameter in the QSettings.
        """
        if hasattr(self, "_io_dialog_config"):
            self._io_dialog_config["qsettings_ref"] = name

    def update_io_directory(self, path: str) -> None:
        """
        Update the input directory for the given Parameter.

        This method needs to be implemented by the subclass, if required.

        Parameters
        ----------
        path : str
            The path to the new directory.
        """
        if hasattr(self, "io_dialog"):
            self.io_dialog.set_curr_dir(id(self), path)

    def update_choices(
        self,
        new_choices: list[Any],
        selection: str | None = None,
        emit_signal: bool = True,
    ) -> None:
        """
        Update the choices of the BaseParamIoWidget in place.

        This method must be implemented by the subclass, if required.

        Parameters
        ----------
        new_choices : list[Any]
            The new choices to be set. While any type is accepted, the choices
            will be converted to strings for display.
        selection : str | None, optional
            The selection to be set after the update. If None, the first
            choice will be selected. Default is None.
        emit_signal : bool, optional
            Flag to toggle emitting a changed signal after updating the choices
            (if the selection has changed). The default is True.
        """
        raise NotImplementedError(
            "The update_choices method must is only implemented if the associated "
            "Parameter has defined choices."
        )

    @QtCore.Slot()
    def emit_signal(self, force_update: bool = False) -> None:
        """
        Emit a signal that the value has been edited.

        Parameters
        ----------
        force_update : bool
            Force an update even if the value has not changed. The default is False.
        """
        _cur_value = self.current_text
        if _cur_value != self._old_value or force_update:
            self._old_value = _cur_value
            self.sig_new_value.emit(_cur_value)  # type: ignore[attr-defined]
            self.sig_value_changed.emit()  # type: ignore[attr-defined]


class BaseParamIoWidget(BaseParamIoWidgetMixIn, QtWidgets.QWidget):
    def __init__(
        self, param: Parameter, parent: QtWidgets.QWidget | None = None, **kwargs: Any
    ) -> None:
        """Initialize the widget."""
        QtWidgets.QWidget.__init__(self, parent=parent)
        BaseParamIoWidgetMixIn.__init__(self, param)

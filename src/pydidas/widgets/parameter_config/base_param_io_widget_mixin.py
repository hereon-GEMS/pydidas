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
from typing import Any

from numpy import nan, ndarray
from qtpy import QtCore, QtGui, QtWidgets

from pydidas.core import Hdf5key, Parameter, UserConfigError
from pydidas.core.constants import (
    GENERIC_STANDARD_WIDGET_WIDTH,
    QT_REG_EXP_FLOAT_VALIDATOR,
    QT_REG_EXP_INT_VALIDATOR,
)
from pydidas.core.utils import NumpyParser


LOCAL_SETTINGS = QtCore.QLocale(QtCore.QLocale.C)
LOCAL_SETTINGS.setNumberOptions(QtCore.QLocale.RejectGroupSeparator)

FLOAT_VALIDATOR = QtGui.QDoubleValidator()
FLOAT_VALIDATOR.setNotation(QtGui.QDoubleValidator.ScientificNotation)
FLOAT_VALIDATOR.setLocale(LOCAL_SETTINGS)


class BaseParamIoWidgetMixIn:
    """
    Base mixin class of widgets for I/O during Parameter editing.

    Parameters
    ----------
    param : Parameter
        A Parameter instance.
    **kwargs : Any
        Any additional kwargs. Used keyword arguments are:

        linebreak : bool
            If True, the sizeHint will be increased to allow for a linebreak.
            The default is False.
    """

    sig_new_value = QtCore.Signal(str)
    sig_value_changed = QtCore.Signal()

    _SUPPORTED_TYPE_STRINGS = {"true": True, "false": False, "nan": nan, "none": None}
    _TYPE_CONVERTERS = {
        numbers.Integral: int,
        numbers.Real: float,
        pathlib.Path: pathlib.Path,
        Hdf5key: Hdf5key,
        ndarray: NumpyParser,
    }

    def __init__(self, param: Parameter, **kwargs: Any):
        self._linked_param = param
        self._ptype = param.dtype
        self._old_value = None
        self.__hint_factor = 1 + int(kwargs.get("linebreak", False))

    @property
    def validator(self) -> QtGui.QValidator | None:
        """
        Get the widget's validator based on the Parameter's configuration.

        Returns
        -------
        QtGui.QValidator | None
            The validator for the widget based on the Parameter options.
            If the Parameter has no specific validator, None is returned.
        """
        if self._linked_param.dtype == numbers.Integral:
            if self._linked_param.allow_None:
                return QT_REG_EXP_INT_VALIDATOR
            return QtGui.QIntValidator()
        elif self._linked_param.dtype == numbers.Real:
            if self._linked_param.allow_None:
                return QT_REG_EXP_FLOAT_VALIDATOR
            return FLOAT_VALIDATOR
        return None

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

    def type_from_string(self, text: str) -> Any:
        """
        Convert a string to the appropriate datatype.

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
        return self._SUPPORTED_TYPE_STRINGS[_input]

    def sizeHint(self) -> QtCore.QSize:  # noqa C0103
        """
        Set a large horizontal size hint to have the widget expand with big font sizes.

        Returns
        -------
        QtCore.QSize
            The sizeHint, depending on the "linebreak" setting.
        """
        return QtCore.QSize(self.__hint_factor * GENERIC_STANDARD_WIDGET_WIDTH, 25)

    def get_value_from_text(self, text: str) -> Any:
        """
        Get a value from the text entry to update the Parameter value.

        Parameters
        ----------
        text : str
            The input string from the input field.

        Returns
        -------
        Any
            The text converted to the stored datatype (e.g. int, float, path)
            of the associated Parameter.
        """
        if self.is_special_type_string(text):
            return self.type_from_string(text)
        try:
            if (
                text == ""
                and self._linked_param.allow_None
                and issubclass(self._linked_param.dtype, numbers.Real)
            ):
                return None
            _converter = self._TYPE_CONVERTERS.get(self._linked_param.dtype, None)
            if _converter is not None:
                return _converter(text)
        except ValueError as _error:
            _msg = str(_error).capitalize()
            raise UserConfigError(f'ValueError! {_msg} Input text was "{text}"')
        return text

    def emit_signal(self) -> None:
        """
        Emit a signal.

        This base method needs to be defined by the subclass.

        Raises
        ------
        NotImplementedError
            If the subclass has not implemented its own emit_signal method,
            this exception will be raised.
        """
        raise NotImplementedError

    def get_value(self) -> Any:
        """
        Get the value from the input field.

        This base method needs to be defined by the subclass.

        Raises
        ------
        NotImplementedError
            If the subclass has not implemented its own get_value method,
            this exception will be raised.
        """
        raise NotImplementedError

    def set_value(self, value: object) -> None:
        """
        Set the input field's value.

        This base method needs to be defined by the subclass.

        Raises
        ------
        NotImplementedError
            If the subclass has not implemented its own set_value method,
            this exception will be raised.
        """
        raise NotImplementedError

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
        pass

    def update_io_directory(self, path: str) -> None:
        """
        Update the input directory for the given Parameter.

        This method needs to be implemented by the subclass, if required.

        Parameters
        ----------
        path : str
            The path to the new directory.
        """
        pass

    def update_choices(self, new_choices: list, selection: str | None = None) -> None:
        """
        Update the choices of the BaseParamIoWidget in place.

        This method must be implemented by the subclass, if required.

        Parameters
        ----------
        new_choices : list
            The new choices to be set.
        selection : str | None, optional
            The selection to be set after the update. If None, the first
            choice will be selected. Default is None.
        """
        raise NotImplementedError(
            "The update_choices method must is only implemented if the associated "
            "Parameter has defined choices."
        )


class BaseParamIoWidget(BaseParamIoWidgetMixIn, QtWidgets.QWidget): ...

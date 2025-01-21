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
__all__ = ["BaseParamIoWidgetMixIn"]


import numbers
import pathlib

from numpy import nan, ndarray
from qtpy import QtCore, QtGui

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


_TYPE_STRINGS = {
    "true": True,
    "false": False,
    "nan": nan,
    "none": None,
}
_TYPE_CONVERTERS = {
    numbers.Integral: int,
    numbers.Real: float,
    pathlib.Path: pathlib.Path,
    Hdf5key: Hdf5key,
    ndarray: NumpyParser,
}


class BaseParamIoWidgetMixIn:
    """
    Base mixin class of widgets for I/O during Parameter editing.

    Parameters
    ----------
    param : Parameter
        A Parameter instance.
    **kwargs : dict
        Any additional kwargs.
    """

    io_edited = QtCore.Signal(str)

    def __init__(self, param: Parameter, **kwargs: dict):
        self._ptype = param.dtype
        self._allow_None = param.allow_None
        self._old_value = None
        self.__hint_factor = 1 + int(kwargs.get("linebreak", False))

    def sizeHint(self) -> QtCore.QSize:
        """
        Set a large horizontal size hint to have the widget expand with big font sizes.

        Returns
        -------
        QtCore.QSize
            The sizeHint, depending on the "linebreak" setting.
        """
        return QtCore.QSize(self.__hint_factor * GENERIC_STANDARD_WIDGET_WIDTH, 25)

    def set_validator(self, param: Parameter):
        """
        Set the widget's validator based on the Parameter's configuration.

        Parameters
        ----------
        param : pydidas.core.Parameter
            The associated Parameter.
        """
        if param.dtype == numbers.Integral:
            if param.allow_None:
                self.setValidator(QT_REG_EXP_INT_VALIDATOR)
            else:
                self.setValidator(QtGui.QIntValidator())
        elif param.dtype == numbers.Real:
            if param.allow_None:
                self.setValidator(QT_REG_EXP_FLOAT_VALIDATOR)
            else:
                self.setValidator(FLOAT_VALIDATOR)

    def get_value_from_text(self, text: str) -> object:
        """
        Get a value from the text entry to update the Parameter value.

        Parameters
        ----------
        text : str
            The input string from the input field.

        Returns
        -------
        type
            The text converted to the required datatype (int, float, path)
            to update the Parameter value.
        """
        # need to process True and False explicitly because bool is a subtype
        # of int but the strings 'True' and 'False' cannot be converted to int
        if text.lower() in _TYPE_STRINGS:
            return _TYPE_STRINGS[text.lower()]
        try:
            if (
                text == ""
                and self._allow_None
                and self._ptype in [numbers.Integral, numbers.Real]
            ):
                return None
            if self._ptype in _TYPE_CONVERTERS:
                return _TYPE_CONVERTERS[self._ptype](text)
        except ValueError as _error:
            _msg = str(_error)
            _msg = _msg[0].upper() + _msg[1:]
            raise UserConfigError(f'ValueError! {_msg} Input text was "{text}"')
        return text

    def emit_signal(self):
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

    def get_value(self):
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

    def set_value(self, value: object):
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

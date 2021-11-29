# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Module with the InputWidget class used to edit Parameters."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['InputWidget']

import numbers
import pathlib

from PyQt5 import QtWidgets, QtGui
from numpy import nan

from ...core import Hdf5key
from ...constants import (PARAM_INPUT_WIDGET_HEIGHT,
                          QT_REG_EXP_FLOAT_VALIDATOR,
                          QT_REG_EXP_INT_VALIDATOR)


class InputWidget(QtWidgets.QWidget):
    """Base class of widgets for I/O during plugin parameter editing."""

    def __init__(self, parent, param, width=255):
        """
        Setup the widget.

        Init method to setup the widget and set the links to the parameter
        and Qt parent widget.

        Parameters
        ----------
        parent : QWidget
            A QWidget instance.
        param : Parameter
            A Parameter instance.
        width: int, optional
            The width of the IO widget.
        """
        super().__init__(parent)
        self.setFixedWidth(width)
        self.setFixedHeight(PARAM_INPUT_WIDGET_HEIGHT)
        self.__ptype = param.type
        self._oldValue = None
        self.setToolTip(f'{param.tooltip}')

    def set_validator(self, param):
        """
        Set the widget's validator based on the Parameter datatype and
        allow_None settings.

        Parameters
        ----------
        param : pydidas.core.Parameter
            The associated Parameter.
        """
        if param.type == numbers.Integral:
            if param.allow_None:
                self.setValidator(QT_REG_EXP_INT_VALIDATOR)
            else:
                self.setValidator(QtGui.QIntValidator())
        elif param.type == numbers.Real:
            if param.allow_None:
                self.setValidator(QT_REG_EXP_FLOAT_VALIDATOR)
            else:
                _validator = QtGui.QDoubleValidator()
                _validator.setNotation(QtGui.QDoubleValidator.ScientificNotation)
                self.setValidator(_validator)

    def get_value_from_text(self, text):
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
        if text == 'True':
            return True
        if text == 'False':
            return False
        if text.upper() == 'NAN':
            return nan
        if text.upper() == 'NONE':
            return None
        if self.__ptype == numbers.Integral:
            return int(text)
        if self.__ptype == numbers.Real:
            return float(text)
        if self.__ptype == pathlib.Path:
            return pathlib.Path(text)
        if self.__ptype == Hdf5key:
            return Hdf5key(text)
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

    def set_value(self, value):
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

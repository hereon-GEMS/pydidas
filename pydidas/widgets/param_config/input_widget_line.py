#!/usr/bin/env python

# MIT License
#
# Copyright (c) 2021 Malte Storm, Helmholtz-Zentrum Hereon.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Module with the PluginParamConfig class used to edit plugin parameters."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['InputWidgetLine']

import numbers

from PyQt5 import QtWidgets, QtCore, QtGui
from .input_widget import InputWidget
from ...config import PARAM_INPUT_WIDGET_HEIGHT

class InputWidgetLine(QtWidgets.QLineEdit, InputWidget):
    """Widgets for I/O during plugin parameter editing without choices."""
    #for some reason, inhering the signal does not work
    io_edited = QtCore.pyqtSignal(str)

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
        width : int, optional
            The width of the IOwidget.
        """
        super().__init__(parent, param, width)
        if param.type == numbers.Integral:
            self.setValidator(QtGui.QIntValidator())
        elif param.type == numbers.Real:
            _validator = QtGui.QDoubleValidator()
            _validator.setNotation(QtGui.QDoubleValidator.ScientificNotation)
            self.setValidator(_validator)

        self.editingFinished.connect(self.emit_signal)
        self.setFixedHeight(PARAM_INPUT_WIDGET_HEIGHT)
        self.set_value(param.value)

    def emit_signal(self):
        """
        Emit a signal that the value has been edited.

        This method emits a signal that the combobox selection has been
        changed and the Parameter value needs to be updated.

        Returns
        -------
        None.
        """
        _curValue = self.text()
        if _curValue != self._oldValue:
            self._oldValue = _curValue
            self.io_edited.emit(_curValue)

    def get_value(self):
        """
        Get the current value from the combobox to update the Parameter value.

        Returns
        -------
        type
            The text converted to the required datatype (int, float, path)
            to update the Parameter value.
        """
        text = self.text()
        return self.get_value_from_text(text)

    def set_value(self, value):
        """
        Set the input field's value.

        This method changes the combobox selection to the specified value.
        Warning: This method will *not* update the connected parameter value.

        Returns
        -------
        None.
        """
        self._oldValue = value
        self.setText(f'{value}')

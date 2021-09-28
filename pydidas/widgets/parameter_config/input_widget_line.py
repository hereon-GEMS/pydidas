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

"""Module with the InputWidgetLine class used to edit Parameters."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['InputWidgetLine']

import numbers

from PyQt5 import QtWidgets, QtCore, QtGui
from .input_widget import InputWidget
from ...constants import PARAM_INPUT_WIDGET_HEIGHT

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

# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""Module with the PluginParamConfig class used to edit plugin parameters."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['InputWidget']



from PyQt5 import QtWidgets, QtCore
from .input_widget import InputWidget


class InputWidgetCombo(QtWidgets.QComboBox, InputWidget):
    """
    Widgets for I/O during plugin parameter editing with predefined
    choices.
    """
    #because of the double inheritance, inhering the signal does not work
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

        Returns
        -------
        None.
        """
        super().__init__(parent, param, width)
        for choice in param.choices:
            self.addItem(f'{choice}')
        self.__items = [self.itemText(i) for i in range(self.count())]
        self.currentIndexChanged.connect(self.emit_signal)
        self.set_value(param.value)

    def __convert_bool(self, value):
        """
        Convert boolean integers to string.

        This conversion is necessary because boolean "0" and "1" cannot be
        interpreted as "True" and "False" straight away.

        Parameters
        ----------
        value : any
            The input value from the field. This could be any object.

        Returns
        -------
        value : any
            The input value, with 0/1 converted it True or False are
            widget choices.
        """
        if value == 0 and 'False' in self.__items:
            value = 'False'
        elif value == 1 and 'True' in self.__items:
            value = 'True'
        return value

    def emit_signal(self):
        """
        Emit a signal that the value has been edited.

        This method emits a signal that the combobox selection has been
        changed and the Parameter value needs to be updated.

        Returns
        -------
        None.
        """
        _curValue = self.currentText()
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
        text = self.currentText()
        return self.get_value_from_text(text)

    def set_value(self, value):
        """
        Set the input field's value.

        This method changes the combobox selection to the specified value.

        Returns
        -------
        None.
        """
        value = self.__convert_bool(value)
        self._oldValue = value
        self.setCurrentIndex(self.findText(f'{value}'))

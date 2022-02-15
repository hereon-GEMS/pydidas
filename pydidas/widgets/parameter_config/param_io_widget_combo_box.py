# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the ParamIoWidgetComboBox class used to edit Parameters. This
class is used for all Parameters with predefined choices.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ParamIoWidgetComboBox']

from qtpy import QtWidgets, QtCore

from .base_param_io_widget import BaseParamIoWidget
from ...core.utils import (convert_unicode_to_ascii, SignalBlocker,
                           convert_special_chars_to_unicode)


class ParamIoWidgetComboBox(QtWidgets.QComboBox, BaseParamIoWidget):
    """
    Widgets for I/O during plugin parameter editing with predefined
    choices.
    """
    #because of the double inheritance, inhering the signal does not work
    io_edited = QtCore.Signal(str)

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
        for choice in param.choices:
            self.addItem(f'{convert_special_chars_to_unicode(str(choice))}')
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
        """
        _cur_value = convert_unicode_to_ascii(self.currentText())
        if _cur_value != self._old_value:
            self._old_value = _cur_value
            self.io_edited.emit(_cur_value)

    def get_value(self):
        """
        Get the current value from the combobox to update the Parameter value.

        Returns
        -------
        type
            The text converted to the required datatype (int, float, path)
            to update the Parameter value.
        """
        text = convert_unicode_to_ascii(self.currentText())
        return self.get_value_from_text(text)

    def set_value(self, value):
        """
        Set the input field's value.

        This method changes the combobox selection to the specified value.
        """
        value = self.__convert_bool(value)
        self._old_value = value
        _txt_repr = convert_special_chars_to_unicode(str(value))
        self.setCurrentText(_txt_repr)

    def update_choices(self, new_choices):
        """
        Update the choices of the BaseParamIoWidget in place.

        This method also selects the first new choice as new item.
        Note: This method does not update the associated Parameter and does
        not synchronize with the Parameter.

        Parameters
        ----------
        new_choices : collections.abc.Iterable
            Any iterable with new choices.
        """
        with SignalBlocker(self):
            self.clear()
            for choice in new_choices:
                _itemstr = convert_special_chars_to_unicode(str(choice))
                self.addItem(_itemstr)
            self.__items = [self.itemText(i) for i in range(self.count())]
            self.set_value(new_choices[0])

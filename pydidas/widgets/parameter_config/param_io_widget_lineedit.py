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
Module with the ParamIoWidgetLineEdit class used to edit free-text Parameters.
There are no typechecks implemented in the widget and any input which is
accepted by the Parameter is valid.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ParamIoWidgetLineEdit']

from PyQt5 import QtWidgets, QtCore

from .base_param_io_widget import BaseParamIoWidget
from ...core.constants import (PARAM_INPUT_WIDGET_HEIGHT,
                               PARAM_INPUT_WIDGET_WIDTH)


class ParamIoWidgetLineEdit(QtWidgets.QLineEdit, BaseParamIoWidget):
    """
    Widgets for I/O of Parameter editing without predefined choices.


    Parameters
    ----------
    parent : QWidget
        A QWidget instance.
    param : Parameter
        A Parameter instance.
    width : int, optional
        The width of the widget. The default is given by the
        PARAM_INPUT_WIDGET_WIDTH value in the
        pydidas.core.constants.gui_constants module.
    """
    io_edited = QtCore.pyqtSignal(str)

    def __init__(self, parent, param, width=PARAM_INPUT_WIDGET_WIDTH):
        super().__init__(parent, param, width)
        self.set_validator(param)
        self.editingFinished.connect(self.emit_signal)
        self.setFixedHeight(PARAM_INPUT_WIDGET_HEIGHT)
        self.set_value(param.value)

    def emit_signal(self):
        """
        Emit a signal that the value has been edited.

        This method emits a signal that the combobox selection has been
        changed and the Parameter value needs to be updated.
        """
        _cur_value = self.text()
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
        text = self.text()
        return self.get_value_from_text(text)

    def set_value(self, value):
        """
        Set the input field's value.

        This method changes the combobox selection to the specified value.
        Warning: This method will *not* update the connected parameter value.
        """
        self._old_value = value
        self.setText(f'{value}')

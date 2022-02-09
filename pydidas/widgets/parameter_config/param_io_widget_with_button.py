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
Module with the ParamIoWidgetWithButton which is a generic lineedit I/O with
the addition of a programmable button.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ParamIoWidgetWithButton']

from functools import partial

from PyQt5 import QtWidgets, QtCore, QtGui

from .base_param_io_widget import BaseParamIoWidget
from ...core.constants import PARAM_INPUT_WIDGET_HEIGHT


class ParamIoWidgetWithButton(BaseParamIoWidget):
    """
    Widgets for Parameter I/O which includes a freely programmable button
    for a dialog or other interactions.

    Parameters
    ----------
    parent : QWidget
        A QWidget instance.
    param : Parameter
        A Parameter instance.
    width: int, optional
        The width of the IO widget. The default is the PARAM_INPUT_EDIT_WIDTH
        specified in pydidas.core.constants.gui_constants.
    button_icon : Union[QIcon, None], optional
        The icon for the button. If None, the standard "file open" icon
        will be used.
    """
    io_edited = QtCore.pyqtSignal(str)

    def __init__(self, parent, param, width=255, button_icon=None):
        super().__init__(parent, param, width)
        self.ledit = QtWidgets.QLineEdit()
        self.ledit.setFixedWidth(width - PARAM_INPUT_WIDGET_HEIGHT - 2)
        self.ledit.setFixedHeight(PARAM_INPUT_WIDGET_HEIGHT)

        if not isinstance(button_icon, QtGui.QIcon):
            button_icon = self.style().standardIcon(42)

        self._button = QtWidgets.QPushButton(button_icon, '')
        self._button.setFixedWidth(PARAM_INPUT_WIDGET_HEIGHT)
        self._button.setFixedHeight(PARAM_INPUT_WIDGET_HEIGHT)
        _layout = QtWidgets.QHBoxLayout()
        _layout.setContentsMargins(0, 0, 0, 0)
        _layout.addWidget(self.ledit)
        _layout.addWidget(self._button)
        self.setLayout(_layout)

        self.ledit.editingFinished.connect(self.emit_signal)
        self.ledit.returnPressed.connect(partial(self.emit_signal, True))
        self._button.clicked.connect(self.button_function)
        self.set_value(param.value)

    def button_function(self):
        """
        Needs to be implemented by the subclass.
        """
        raise NotImplementedError

    def emit_signal(self, force_update=False):
        """
        Emit a signal that the value has been edited.

        This method emits a signal that the combobox selection has been
        changed and the Parameter value needs to be updated.

        Parameters
        ----------
        force_update : bool
            Force an update even if the value has not changed.
        """
        _curr_value = self.ledit.text()
        if _curr_value != self._old_value or force_update:
            self._old_value = _curr_value
            self.io_edited.emit(_curr_value)

    def get_value(self):
        """
        Get the current value from the QLineEdit to update the Parameter value.

        Returns
        -------
        str
            The input text.
        """
        text = self.ledit.text()
        return self.get_value_from_text(text)

    def set_value(self, value):
        """
        Set the input field's value.

        This method changes the combobox selection to the specified value.
        """
        self._old_value = value
        self.ledit.setText(f'{value}')

    def setText(self, text):
        """
        Set the line edit text to the input.

        This method will call the line edit setText method to update the
        displayed text.

        Parameters
        ----------
        text : object
            Any object, the object's str representation will be used.
        """
        self.ledit.setText(str(text))

# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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
Module with the ParamIoWidgetWithButton which is a generic lineedit I/O with
the addition of a programmable button.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ParamIoWidgetWithButton"]


from functools import partial

from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtWidgets import QStyle

from pydidas.core import Parameter
from pydidas.widgets.factory import PydidasLineEdit, SquareButton
from pydidas.widgets.parameter_config.base_param_io_widget_mixin import (
    BaseParamIoWidgetMixIn,
)


class ParamIoWidgetWithButton(BaseParamIoWidgetMixIn, QtWidgets.QWidget):
    """
    Widgets for Parameter I/O which includes a freely programmable button.

    Parameters
    ----------
    param : Parameter
        A Parameter instance.
    **kwargs : dict
        Optional keyword arguments. Supported kwargs are "width" (in pixel)
        to specify the size of the I/O field and "button_icon" to give an
        icon for the button.
    """

    io_edited = QtCore.Signal(str)

    def __init__(self, param: Parameter, **kwargs: dict):
        QtWidgets.QWidget.__init__(self, parent=kwargs.get("parent", None))
        BaseParamIoWidgetMixIn.__init__(self, param, **kwargs)
        self._io_lineedit = PydidasLineEdit()
        if not isinstance(kwargs.get("button_icon", None), QtGui.QIcon):
            kwargs["button_icon"] = self.style().standardIcon(
                QStyle.SP_DialogOpenButton
            )
        self._button = SquareButton(
            kwargs["button_icon"], "", font_metric_height_factor=1
        )
        _layout = QtWidgets.QHBoxLayout()
        _layout.setContentsMargins(0, 0, 0, 0)
        _layout.setSpacing(2)
        _layout.addWidget(self._io_lineedit)
        _layout.addWidget(self._button)
        self.setLayout(_layout)

        self._button.clicked.connect(self.button_function)
        self._io_lineedit.editingFinished.connect(self.emit_signal)
        self._io_lineedit.returnPressed.connect(partial(self.emit_signal, True))
        self._io_lineedit.setText(f"{param.value}")

    def button_function(self):
        """
        Needs to be implemented by the subclass.
        """
        raise NotImplementedError

    def emit_signal(self, force_update: bool = False):
        """
        Emit a signal that the value has been edited.

        This method emits a signal that the combobox selection has been
        changed and the Parameter value needs to be updated.

        Parameters
        ----------
        force_update : bool
            Force an update even if the value has not changed.
        """
        _curr_value = self._io_lineedit.text()
        if _curr_value != self._old_value or force_update:
            self._old_value = _curr_value
            self.io_edited.emit(_curr_value)

    def get_value(self) -> object:
        """
        Get the current value from the QLineEdit to update the Parameter value.

        Returns
        -------
        str
            The input text.
        """
        text = self._io_lineedit.text()
        return self.get_value_from_text(text)

    def set_value(self, value: object):
        """
        Set the input field's value.

        This method changes the combobox selection to the specified value.

        Parameters
        ----------
        value : object
            The value to be displayed for the Parameter.
        """
        self._old_value = self.get_value()
        self._io_lineedit.setText(f"{value}")

    def setText(self, text: object):
        """
        Set the line edit text to the input.

        This method will call the line edit setText method to update the
        displayed text.

        Parameters
        ----------
        text : object
            Any object, the object's str representation will be used.
        """
        self._io_lineedit.setText(str(text))

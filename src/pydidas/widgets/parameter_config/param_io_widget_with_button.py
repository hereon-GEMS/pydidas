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
from typing import Any

from qtpy import QtGui, QtWidgets
from qtpy.QtWidgets import QStyle

from pydidas.core import Parameter
from pydidas.widgets.factory import PydidasLineEdit, SquareButton
from pydidas.widgets.factory.pydidas_widget_mixin import PydidasWidgetMixin
from pydidas.widgets.parameter_config.base_param_io_widget import (
    BaseParamIoWidgetMixIn,
)
from pydidas.widgets.utilities import get_pyqt_icon_from_str


class ParamIoWidgetWithButton(
    BaseParamIoWidgetMixIn, PydidasWidgetMixin, QtWidgets.QWidget
):
    """
    Widgets for Parameter I/O which includes a freely programmable button.

    Parameters
    ----------
    param : Parameter
        A Parameter instance.
    **kwargs : Any
        Optional keyword arguments. Supported kwargs are

        button_icon : QtGui.QIcon
            The icon to use for the button.
    """

    def __init__(self, param: Parameter, **kwargs: Any) -> None:
        QtWidgets.QWidget.__init__(self, parent=kwargs.get("parent", None))
        BaseParamIoWidgetMixIn.__init__(self, param)
        PydidasWidgetMixin.__init__(self, **kwargs)
        _icon = kwargs.get("button_icon", None)
        if isinstance(_icon, str):
            _icon = get_pyqt_icon_from_str(_icon)
        if not isinstance(_icon, QtGui.QIcon):
            _icon = self.style().standardIcon(
                QStyle.StandardPixmap(QStyle.SP_DialogOpenButton)
            )

        self._io_lineedit = PydidasLineEdit()
        self._button = SquareButton(_icon, "", font_metric_height_factor=1)

        _layout = QtWidgets.QHBoxLayout()
        _layout.setContentsMargins(0, 0, 0, 0)
        _layout.setSpacing(2)
        _layout.addWidget(self._io_lineedit)
        _layout.addWidget(self._button)
        self.setLayout(_layout)
        self.setFocusProxy(self._io_lineedit)

        self._io_lineedit.setText(f"{param.value}")
        self._button.clicked.connect(self.button_function)
        self._io_lineedit.editingFinished.connect(self.emit_signal)
        self._io_lineedit.returnPressed.connect(partial(self.emit_signal, True))

    @property
    def current_text(self) -> str:
        """
        Get the text from the lineedit.

        Returns
        -------
        str
            The text in the lineedit.
        """
        return self._io_lineedit.text().strip()

    def update_widget_value(self, value: Any) -> None:
        """
        Update the widget value without emitting signals.

        Parameters
        ----------
        value : Any
            The new value to set in the widget.
        """
        # the setText method only emits the textChanged signal, not editingFinished
        self._io_lineedit.setText(f"{value}")

    def button_function(self) -> None:
        """
        Needs to be implemented by the subclass.
        """
        raise NotImplementedError

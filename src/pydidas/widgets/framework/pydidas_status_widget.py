# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
Module with the PydidasStatusWidget singleton instance of the _PydidasStatusWidget
which is used as a global logging and status widget.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasStatusWidget"]


from qtpy import QtCore, QtGui, QtWidgets

from ...core import SingletonFactory
from ...core.utils import get_time_string


class _PydidasStatusWidget(QtWidgets.QPlainTextEdit):
    """
    The PydidasStatusWidget is a subclassed QPlainTextEdit with an additional method
    to append text.
    """

    def __init__(self, **kwargs: dict):
        QtWidgets.QPlainTextEdit.__init__(self, kwargs.get("parent", None))
        self.setReadOnly(True)
        self.setMinimumHeight(50)
        self.resize(500, 50)
        QtWidgets.QApplication.instance().sig_status_message.connect(self.add_status)

    def sizeHint(self) -> QtCore.QSize:
        """
        Give a sizeHint which corresponds to a wide and short field.

        Returns
        -------
        QtCore.QSize
            The desired size.
        """
        return QtCore.QSize(500, 50)

    @QtCore.Slot(str)
    def add_status(self, text: str):
        """
        Add a status message to the PydidasStatusWidget.

        This method will add a status message to the Info/Log widget together
        with a timestamp.

        Parameters
        ----------
        text : str
            The text to add.
        """
        if text[-1] != "\n":
            text = text + "\n"
        _cursor = self.textCursor()
        _cursor.movePosition(QtGui.QTextCursor.Start, QtGui.QTextCursor.MoveAnchor, 1)
        self.setTextCursor(_cursor)
        self.insertPlainText(f"{get_time_string()}: {text}")
        self.verticalScrollBar().triggerAction(QtWidgets.QScrollBar.SliderToMinimum)


PydidasStatusWidget = SingletonFactory(_PydidasStatusWidget)

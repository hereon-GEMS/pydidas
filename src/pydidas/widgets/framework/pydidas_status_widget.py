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
Module with the PydidasStatusWidget singleton instance of the _PydidasStatusWidget
which is used as a global logging and status widget.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasStatusWidget"]


from qtpy import QtCore, QtGui, QtWidgets

from pydidas.core import SingletonFactory
from pydidas.core.utils import get_time_string
from pydidas.widgets.misc import ReadOnlyTextWidget
from pydidas_qtcore import PydidasQApplication


class _PydidasStatusWidget(QtWidgets.QDockWidget):
    """
    The PydidasStatusWidget is used for managing global status messages.
    """

    def __init__(self):
        QtWidgets.QDockWidget.__init__(self, "Logging and information")
        self._text_edit = ReadOnlyTextWidget(parent=None)
        self._text_edit.setMinimumHeight(50)
        self._text_edit.resize(500, 50)
        self.setWidget(self._text_edit)
        self.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable
            | QtWidgets.QDockWidget.DockWidgetFloatable
            | QtWidgets.QDockWidget.DockWidgetClosable
        )
        self.setAllowedAreas(
            QtCore.Qt.LeftDockWidgetArea
            | QtCore.Qt.RightDockWidgetArea
            | QtCore.Qt.BottomDockWidgetArea
        )
        self.setBaseSize(500, 50)
        self.resize(500, 50)

        _qt_app = PydidasQApplication.instance()

        _qt_app.sig_status_message.connect(self.add_status)
        # _qt_app.sig_font_size_changed.connect(self.reprint)

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
        _cursor = self._text_edit.textCursor()
        _cursor.movePosition(QtGui.QTextCursor.Start, QtGui.QTextCursor.MoveAnchor, 1)
        self._text_edit.setTextCursor(_cursor)
        self._text_edit.insertPlainText(f"{get_time_string()}: {text}")
        self._text_edit.verticalScrollBar().triggerAction(
            QtWidgets.QScrollBar.SliderToMinimum
        )

    @QtCore.Slot()
    def text(self) -> str:
        """
        Get the text of the widget.

        Returns
        -------
        str
            The text of the widget.
        """
        return self._text_edit.toPlainText()


PydidasStatusWidget = SingletonFactory(_PydidasStatusWidget)

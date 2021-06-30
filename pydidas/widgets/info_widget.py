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

"""Module with the WorkflowPluginWidget which is used to create the workflow
tree."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['GetInfoWidget']

from PyQt5 import QtWidgets, QtCore, QtGui
from ..core.utilities import get_time_string

class _InfoWidget(QtWidgets.QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setMinimumHeight(50)
        self.resize(500, 50)

    def sizeHint(self):
        return QtCore.QSize(500, 50)

    def add_status(self, text):
        _cursor = self.textCursor()
        _cursor.movePosition(QtGui.QTextCursor.Start,
                             QtGui.QTextCursor.MoveAnchor, 1)
        self.setTextCursor(_cursor)
        self.insertPlainText(f'{get_time_string()}: {text}\n')
        self.verticalScrollBar().triggerAction(
            QtWidgets.QScrollBar.SliderToMinimum)

class _InfoWidgetFactory:
    def __init__(self):
        self._instance = None

    def __call__(self):
        if not self._instance:
            self._instance = _InfoWidget()
        return self._instance

GetInfoWidget = _InfoWidgetFactory()

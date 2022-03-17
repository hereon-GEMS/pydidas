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
Module with the WorkflowTreeCanvas which is used to arrange the widgets for
editing the WorkflowTree.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['WorkflowTreeCanvas']

from qtpy import QtWidgets, QtGui

from ...core.constants import QT_STYLES


class WorkflowTreeCanvas(QtWidgets.QFrame):
    """
    The WorkflowTreeCanvas is the widget to draw the workflow tree and hold
    the individual plugin widgets. It is also responsible to draw the lines
    between plugins, if required.

    Parameters
    ----------
    parent : QtWidget, optional
        The parent widget. The default is None.
    """
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.title = QtWidgets.QLabel(self)
        self.title.setStyleSheet(QT_STYLES['title'])
        self.title.setText('Workflow tree editor')
        self.title.move(10, 10)
        self.painter =  QtGui.QPainter()
        self.setAutoFillBackground(True)

        self.setLineWidth(2)
        self.setFrameStyle(QtWidgets.QFrame.Raised)
        self.widget_connections = []

    def paintEvent(self, event):
        """
        Overload the paintEvent to also draw lines connecting
        parent and child plugins.

        Parameters
        ----------
        event : QtCore.QEvent
            The calling event.
        """
        self.painter.begin(self)
        self.painter.setPen(QtGui.QPen(QtGui.QColor(120, 120, 120), 2))
        self.draw_connections()
        self.painter.end()

    def draw_connections(self):
        """
        Draw connections between plugins.

        This method will draw connections between all parent and child plugins.
        Relationships must be supplied through the
        self.update_widget_connections method.
        """
        for _x0, _y0, _x1, _y1 in self.widget_connections:
            self.painter.drawLine(_x0, _y0, _x1, _y1)

    def update_widget_connections(self, widget_conns):
        """
        Store updated widget connections.

        This method will store updated widget connections internally and
        call the update method to draw these connections.

        Parameters
        ----------
        widget_conns : list
            A list with coordinate pairs to draw connections.
        """
        self.widget_connections = widget_conns
        self.update()

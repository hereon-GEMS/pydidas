# MIT License
#
# Copyright (c) 2021 Malte Storm, Helmholtz-Zentrum Hereon.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Module with the WorkflowTreeCanvas."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['WorkflowTreeCanvas']

from PyQt5 import QtWidgets, QtGui
from ..config import STYLES

class WorkflowTreeCanvas(QtWidgets.QFrame):
    """
    The WorkflowTreeCanvas is the widget to draw the workflow tree and hold
    the individual plugin widgets. It is also responsible to draw the lines
    between plugins, if required.
    """
    def __init__(self, parent=None):
        """
        Setup the WorkflowTreeCanvas instance.

        Parameters
        ----------
        parent : QtWidget, optional
            The parent widget. The default is None.

        Returns
        -------
        None.
        """
        super().__init__(parent=parent)
        self.title = QtWidgets.QLabel(self)
        self.title.setStyleSheet(STYLES['title'])
        self.title.setText('Workflow tree')
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
        event : object
            The calling event.

        Returns
        -------
        None.
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

        Returns
        -------
        None.
        """
        for x0, y0, x1, y1 in self.widget_connections:
            self.painter.drawLine(x0, y0, x1, y1)

    def update_widget_connections(self, widget_conns):
        """
        Store updated widget connections.

        This method will store updated widget connections internally and
        call the update method to draw these connections.

        Parameters
        ----------
        widget_conns : list
            A list with coordinate pairs to draw connections.

        Returns
        -------
        None.
        """
        self.widget_connections = widget_conns
        self.update()

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
Module with the WorkflowTreeCanvas which is used to arrange the widgets for
editing the WorkflowTree.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["WorkflowTreeCanvas"]


from qtpy import QtCore, QtGui, QtWidgets

from pydidas.core import constants
from pydidas.widgets.factory import CreateWidgetsMixIn


class WorkflowTreeCanvas(CreateWidgetsMixIn, QtWidgets.QFrame):
    """
    The WorkflowTreeCanvas is the widget to draw the workflow tree and hold
    the individual plugin widgets. It is also responsible to draw the lines
    between plugins, if required.

    Parameters
    ----------
    parent : QtWidget, optional
        The parent widget. The default is None.
    """

    def __init__(self, **kwargs: dict):
        QtWidgets.QFrame.__init__(self, parent=kwargs.get("parent", None))
        CreateWidgetsMixIn.__init__(self)
        self.setAcceptDrops(True)
        self.painter = QtGui.QPainter()
        self.setAutoFillBackground(True)

        self.setLineWidth(2)
        self.setSizePolicy(*constants.POLICY_EXP_EXP)
        self.setFrameStyle(QtWidgets.QFrame.Raised)
        self.widget_connections = []

    def paintEvent(self, event: QtCore.QEvent):
        """
        Overload the paintEvent to also draw lines connecting parent and child plugins.

        Parameters
        ----------
        event : QtCore.QEvent
            The calling event.
        """
        self.painter.begin(self)
        self.painter.setPen(QtGui.QPen(QtGui.QColor(120, 120, 120), 2))
        self.draw_connections()
        self.painter.end()
        super().paintEvent(event)

    def draw_connections(self):
        """
        Draw connections between plugins.

        This method will draw connections between all parent and child plugins.
        Relationships must be supplied through the
        self.update_widget_connections method.
        """
        for _x0, _y0, _x1, _y1 in self.widget_connections:
            self.painter.drawLine(_x0, _y0, _x1, _y1)

    def update_widget_connections(self, widget_conns: list):
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

    def sizeHint(self) -> QtCore.QSize:
        """
        Set the Qt sizeHint to be the widget's size.

        Note that the sizeHint is arbitrary large because it limits the QScrollArea's
        size.

        Returns
        -------
        QtCore.QSize
            The size of the widget.
        """
        return QtCore.QSize(5000, 3000)

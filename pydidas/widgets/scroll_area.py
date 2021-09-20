# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with ScrollArea, a QScrollArea implementation with convenience
features for formatting.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ScrollArea']

from PyQt5 import QtWidgets, QtCore

from .utilities import apply_widget_properties


class ScrollArea(QtWidgets.QScrollArea):
    """
    Convenience class to simplify the setup of a QScrollArea.
    """
    def __init__(self, parent=None, **kwargs):
        """
        Create a QScrollArea with defined widgets, width and height.

        Parameters
        ----------
        parent : QWidget, optional
            The parent widget. The default is None.
        **kwargs : keyword arguments

        Supported keywords
        ------------------
        widget : QWidget, optional
            The scroll area's own widget which is displayed.
            The default is None.
        fixedWidth : int, optional
            If the scroll area shall have a fixed width, this value can be
            defined in pixel. The default is None.
        fixedHeight : int, optional
            If the scroll area shall have a fixed height, this value can be
            defined in pixel. The default is None.
        """
        super().__init__(parent)
        kwargs['widgetResizable'] = True
        kwargs['autoFillBackground'] = True
        kwargs['sizePolicy'] = (QtWidgets.QSizePolicy.Expanding,
                                QtWidgets.QSizePolicy.Expanding)
        kwargs['frameShape'] = QtWidgets.QFrame.NoFrame
        apply_widget_properties(self, **kwargs)

    def sizeHint(self):
        if self.widget() is not None:
            return self.widget().sizeHint()
        else:
            return super().sizeHint()

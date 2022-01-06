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
Module with ScrollArea, a QScrollArea implementation with convenience
calling arguments for simplified formatting.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ScrollArea']

from PyQt5 import QtWidgets

from .utilities import apply_widget_properties


class ScrollArea(QtWidgets.QScrollArea):
    """
    Convenience class to simplify the setup of a QScrollArea.

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget. The default is None.
    **kwargs : dict
        Any additional keyword arguments. See below for supported arguments.
    **QtAttribute : depends on the attribute
        Any Qt attributes which are supported by the RadioButtonGroup. Use the
        Qt attribute name with a lowercase first character. Examples are
        ``widget``, ``fixedWidth``, ``fixedHeight``.
    """
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        kwargs['widgetResizable'] = True
        kwargs['autoFillBackground'] = True
        kwargs['sizePolicy'] = (QtWidgets.QSizePolicy.Expanding,
                                QtWidgets.QSizePolicy.Expanding)
        kwargs['frameShape'] = QtWidgets.QFrame.NoFrame
        apply_widget_properties(self, **kwargs)

    def sizeHint(self):
        """
        Get the size hint.

        If a widget has been set, the ScrollArea will use the widget's sizeHint
        to determine the required size. If no widget is set, it will default
        to the QScrollArea sizeHint.

        Returns
        -------
        QtCore.QSize
            The size hint for the ScrollArea.
        """
        if self.widget() is not None:
            return self.widget().sizeHint()
        return super().sizeHint()

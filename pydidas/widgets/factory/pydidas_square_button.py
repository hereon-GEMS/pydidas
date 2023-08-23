# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
The pydidas_square_button module defines the PydidasSquareButton class.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasSquareButton"]


from qtpy import QtCore, QtWidgets

from .pydidas_widget_mixin import PydidasWidgetMixin


class PydidasSquareButton(PydidasWidgetMixin, QtWidgets.QPushButton):
    """
    A PushButton which tries to stay square in size.
    """

    def __init__(self, *args: tuple, **kwargs: dict):
        QtWidgets.QPushButton.__init__(self, *args)
        PydidasWidgetMixin.__init__(self, **kwargs)
        self.__qtapp = QtWidgets.QApplication.instance()
        self.__qtapp.sig_new_font_height.connect(self.__update_min_sizes)

    def heightForWidth(self, width: int) -> int:
        """
        Get the same preferred height as the width.

        Parameters
        ----------
        width : int
            The widget width.

        Returns
        -------
        int
            The width.
        """
        return width

    @QtCore.Slot(float)
    def __update_min_sizes(self, font_height: float):
        """
        Update the widgets minimum sizes based on the font height.

        Parameters
        ----------
        font_height : float
            The font height metrics.
        """
        self.setMinimumWidth(font_height + 6)
        self.setMinimumHeight(font_height + 6)

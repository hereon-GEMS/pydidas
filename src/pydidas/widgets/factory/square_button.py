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
The pydidas_square_button module defines the SquareButton class.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["SquareButton"]


from qtpy import QtCore, QtWidgets

from pydidas.core.constants import MINIMUN_WIDGET_DIMENSIONS
from pydidas.widgets.factory.pydidas_widget_mixin import PydidasWidgetMixin
from pydidas.widgets.utilities import get_pyqt_icon_from_str


class SquareButton(PydidasWidgetMixin, QtWidgets.QPushButton):
    """
    A PushButton which tries to stay square in size.
    """

    init_kwargs = PydidasWidgetMixin.init_kwargs[:] + ["icon"]

    def __init__(self, *args: tuple, **kwargs: dict):
        if isinstance(kwargs.get("icon"), str):
            kwargs["icon"] = get_pyqt_icon_from_str(kwargs.get("icon"))
        QtWidgets.QPushButton.__init__(self, *args)
        PydidasWidgetMixin.__init__(self, **kwargs)
        self.__update_min_sizes(self._qtapp.font_height)

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

    @QtCore.Slot(float, float)
    def process_new_font_metrics(self, font_width: float, font_height: float):
        """
        Set the fixed width of the widget dynamically from the font metrics.

        Parameters
        ----------
        font_width: float
            The font width in pixels.
        font_height : float
            The font height in pixels.
        """
        self.__update_min_sizes(font_height)
        PydidasWidgetMixin.process_new_font_metrics(self, font_width, font_height)

    def __update_min_sizes(self, font_height: float):
        """
        Update the widgets minimum sizes based on the font height.

        Parameters
        ----------
        font_height : float
            The font height metrics.
        """
        self.__size = int(max(font_height + 6, MINIMUN_WIDGET_DIMENSIONS))
        self.setMinimumWidth(self.__size)
        self.setMinimumHeight(self.__size)

    def sizeHint(self):
        """
        Set the sizeHint based on the font size.
        """
        return QtCore.QSize(self.__size, self.__size)

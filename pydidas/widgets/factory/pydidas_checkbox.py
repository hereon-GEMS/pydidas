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
The pydidas_check_box module defines a custom QCheckBox with font formatting and
sizeHint adjustment.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasCheckBox"]


from qtpy import QtCore, QtWidgets

from ...core.constants import GENERIC_IO_WIDGET_WIDTH
from .pydidas_widget_mixin import PydidasWidgetMixin


class PydidasCheckBox(PydidasWidgetMixin, QtWidgets.QCheckBox):
    """
    Create a QCheckBox with automatic font formatting.
    """

    def __init__(self, *args: tuple, **kwargs: dict):
        self.__sizeHint = QtCore.QSize(GENERIC_IO_WIDGET_WIDTH, 5)
        QtWidgets.QCheckBox.__init__(self, *args)
        PydidasWidgetMixin.__init__(self, **kwargs)
        self.__qtapp = QtWidgets.QApplication.instance()
        self.__qtapp.sig_new_font_height.connect(self.__update_size_hint)
        self.__update_size_hint(self.__qtapp.standard_font_height)

    def sizeHint(self):
        """
        Set a reasonable large sizeHint so the LineEdit takes the available space.

        Returns
        -------
        QtCore.QSize
            The widget sizeHint
        """
        return self.__sizeHint

    @QtCore.Slot(float)
    def __update_size_hint(self, new_font_height: float):
        """
        Update the sizeHint based on the font's height.

        Parameters
        ----------
        new_font_height : float
            The font metric height in pixel.
        """
        _margins = self.contentsMargins()
        self.__sizeHint = QtCore.QSize(
            GENERIC_IO_WIDGET_WIDTH,
            new_font_height + 2 * _margins.top() + _margins.bottom(),
        )

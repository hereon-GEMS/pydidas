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
Module with a factory function to create an empty QWidget.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["EmptyWidget"]


from qtpy.QtWidgets import QGridLayout, QWidget, QApplication
from qtpy import QtCore

from ...core.constants import ALIGN_TOP_LEFT, GENERIC_STANDARD_WIDGET_WIDTH
from ...core.utils import apply_qt_properties


class EmptyWidget(QWidget):
    """
    Create an empty widget with a QGridLayout.

    The constructor also sets QProperties based on the supplied keywords, if
    a matching setter was found.
    """

    init_kwargs = [
        "init_layout",
        "font_metric_width_factor",
        "layout_column_stretches",
        "fix_width",
    ]

    def __init__(self, **kwargs: dict):
        self.__size_hint_width = GENERIC_STANDARD_WIDGET_WIDTH
        QWidget.__init__(self)
        self.__scale_with_font = False
        self.__fix_width = kwargs.get("fix_width", True)
        apply_qt_properties(self, **kwargs)
        if kwargs.get("init_layout", True):
            self.setLayout(QGridLayout())
            apply_qt_properties(
                self.layout(),
                contentsMargins=(0, 0, 0, 0),
                alignment=ALIGN_TOP_LEFT,
            )
        if "font_metric_width_factor" in kwargs:
            self.__scale_with_font = True
            self._qtapp = QApplication.instance()
            self.__font_metric_width_factor = kwargs.get("font_metric_width_factor")
            self.set_dynamic_width_from_font(self._qtapp.standard_font_height)
            self._qtapp.sig_new_font_height.connect(self.set_dynamic_width_from_font)
        if "layout_column_stretches" in kwargs:
            for _key, _val in kwargs.get("layout_column_stretches").items():
                self.layout().setColumnStretch(_key, _val)

    def sizeHint(self):
        """
        Set a reasonable wide sizeHint so the widget takes the available space.

        Returns
        -------
        QtCore.QSize
            The widget sizeHint
        """
        return QtCore.QSize(self.__size_hint_width, 25)

    @QtCore.Slot(float)
    def set_dynamic_width_from_font(self, font_height: float):
        """
        Set the fixed width of the widget dynamically from the font height metric.

        Parameters
        ----------
        font_height : float
            The font height in pixels.
        """
        self.__size_hint_width = int(self.__font_metric_width_factor * font_height)
        if self.__fix_width:
            self.setFixedWidth(self.__size_hint_width)
        self.updateGeometry()

    def update_dynamic_width(self):
        """
        Update the dynamic width.
        """
        if self.__scale_with_font:
            self.set_dynamic_width_from_font(self._qtapp.standard_font_height)

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


from qtpy.QtWidgets import QGridLayout, QWidget
from qtpy import QtCore

from ...core.constants import ALIGN_TOP_LEFT, GENERIC_STANDARD_WIDGET_WIDTH
from ...core.utils import apply_qt_properties


class EmptyWidget(QWidget):
    """
    Create an empty widget with a QGridLayout.

    The constructor also sets QProperties based on the supplied keywords, if
    a matching setter was found.
    """

    def __init__(self, **kwargs: dict):
        QWidget.__init__(self)
        init_layout = kwargs.get("init_layout", True)
        apply_qt_properties(self, **kwargs)
        if init_layout:
            self.setLayout(QGridLayout())
            apply_qt_properties(
                self.layout(),
                contentsMargins=(0, 0, 0, 0),
                alignment=ALIGN_TOP_LEFT,
            )

    def sizeHint(self):
        """
        Set a reasonable wide sizeHint so the widget takes the available space.

        Returns
        -------
        QtCore.QSize
            The widget sizeHint
        """
        return QtCore.QSize(GENERIC_STANDARD_WIDGET_WIDTH, 5)

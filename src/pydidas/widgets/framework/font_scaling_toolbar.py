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
Module with the PydidasToolbar which adds automatic scaling based on metrics.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["FontScalingToolbar"]


from qtpy import QtCore, QtWidgets


class FontScalingToolbar(QtWidgets.QToolBar):
    """
    A subclassed toolbar with automatic scaling based on the font metrics.
    """

    def __init__(self, *args):
        QtWidgets.QToolBar.__init__(self, *args)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.setMovable(False)
        self.toggleViewAction().setEnabled(False)

        self._qtapp = QtWidgets.QApplication.instance()
        self.process_new_font_metrics(*self._qtapp.font_metrics)
        self._qtapp.sig_new_font_metrics.connect(self.process_new_font_metrics)
        self._qtapp.sig_font_family_changed.connect(self.process_new_font_family)

    @QtCore.Slot()
    def process_new_font_family(self):
        """
        Redraw the toolbar with the new font family.
        """
        self.process_new_font_metrics(*self._qtapp.font_metrics)

    @QtCore.Slot(float, float)
    def process_new_font_metrics(self, font_width: float, font_height: float):
        """
        Process the new font height and adjust the ToolBar accordingly.

        Parameters
        ----------
        font_width: float
            The font width in pixels.
        font_height : float
            The font height in pixels.
        """
        self.setStyleSheet("QToolBar{spacing:" + f"{font_height}" + "px;}")

        self.setIconSize(QtCore.QSize(int(3 * font_height), int(3 * font_height)))
        self.setFixedWidth(int(14 * font_width))

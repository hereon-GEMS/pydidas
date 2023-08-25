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
The pydidas_label includes a subclassed QLabel with automatic font formatting.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasLabel"]


from qtpy import QtCore, QtWidgets

from ...core.constants import GENERIC_STANDARD_WIDGET_WIDTH, POLICY_EXP_FIX
from .pydidas_widget_mixin import PydidasWidgetMixin


class PydidasLabel(PydidasWidgetMixin, QtWidgets.QLabel):
    """
    Create a QLabel with automatic font formatting.
    """

    init_kwargs = PydidasWidgetMixin.init_kwargs[:] + ["number_of_lines"]

    def __init__(self, *args: tuple, **kwargs: dict):
        QtWidgets.QLabel.__init__(self, *args)
        PydidasWidgetMixin.__init__(self, **kwargs)
        if "sizePolicy" not in kwargs:
            self.setSizePolicy(*POLICY_EXP_FIX)
        if "number_of_lines" in kwargs:
            self._n_lines = kwargs.get("number_of_lines")
            self._qtapp.sig_new_font_height.connect(
                self.update_height_from_font_metrics
            )
            self.update_height_from_font_metrics(self._qtapp.standard_font_height)

    def sizeHint(self):
        """
        Set a reasonable wide sizeHint so the label takes the available space.

        Returns
        -------
        QtCore.QSize
            The widget sizeHint
        """
        return QtCore.QSize(GENERIC_STANDARD_WIDGET_WIDTH, 25)

    @QtCore.Slot(float)
    def update_height_from_font_metrics(self, new_font_metric_height: float):
        """
        Update the widget's height.

        Parameters
        ----------
        new_font_metric_height : float
            The height of the font metrics.
        """
        self.setFixedHeight(self._n_lines * new_font_metric_height + 2 * self.margin())

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
The pydidas_widget_with_gridlayout contains the PydidasWidgetWithGridLayout widget.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasWidgetWithGridLayout"]


from qtpy import QtCore, QtWidgets

from ...core.constants import GENERIC_IO_WIDGET_WIDTH
from ...core.utils import apply_qt_properties


class PydidasWidgetWithGridLayout(QtWidgets.QWidget):
    """
    An empty widget with a grid layout and tight contents margins.
    """

    def __init__(self, parent=None, **kwargs):
        QtWidgets.QWidget.__init__(self, parent)
        _layout = QtWidgets.QGridLayout()
        _layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(_layout)
        apply_qt_properties(self, **kwargs)

    def sizeHint(self):
        """
        Set a reasonable small sizeHint which can be expanded.

        Returns
        -------
        QtCore.QSize
            The widget sizeHint
        """
        return QtCore.QSize(GENERIC_IO_WIDGET_WIDTH, 25)

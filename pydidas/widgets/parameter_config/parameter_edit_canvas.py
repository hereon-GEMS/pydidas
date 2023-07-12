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
Module with the ParameterEditCanvas class which is a subclassed QFrame updated
with the ParameterWidgetsMixIn.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ParameterEditCanvas"]


from qtpy import QtCore, QtWidgets

from ...core.utils import apply_qt_properties
from .parameter_widgets_mixin import ParameterWidgetsMixIn


class ParameterEditCanvas(QtWidgets.QFrame, ParameterWidgetsMixIn):
    """
    The ParameterEditCanvas widget can be used to create a composite
    widget for updating multiple Parameter values.

    Parameters
    ----------
    parent : QtWidget, optional
        The parent widget. The default is None.
    init_layout : bool, optional
        Flag to toggle layout creation (with a VBoxLayout). The default
        is True.
    **kwargs : dict
        Additional keyword arguments
    """

    def __init__(self, parent=None, **kwargs):
        QtWidgets.QFrame.__init__(self, parent)
        ParameterWidgetsMixIn.__init__(self)
        init_layout = kwargs.get("init_layout", True)
        kwargs["lineWidth"] = kwargs.get("lineWidth", 2)
        kwargs["frameStyle"] = kwargs.get("frameStyle", QtWidgets.QFrame.Raised)
        kwargs["autoFillBackground"] = kwargs.get("autoFillBackground", True)
        apply_qt_properties(self, **kwargs)
        if init_layout:
            _layout = QtWidgets.QGridLayout()
            _layout.setContentsMargins(5, 5, 5, 5)
            _layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            self.setLayout(_layout)

    def next_row(self):
        """
        Get the next empty row in the layout.

        Returns
        -------
        int
            The next empty row.
        """
        return self.layout().rowCount() + 1

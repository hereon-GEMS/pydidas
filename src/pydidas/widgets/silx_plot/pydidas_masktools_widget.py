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
Module with the PydidasMaskToolsWidget class which changes the generic MaskToolWidget
button sizes.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasMaskToolsWidget"]


from typing import Union

from qtpy import QtCore, QtWidgets
from silx.gui.plot.MaskToolsWidget import MaskToolsWidget


class PydidasMaskToolsWidget(MaskToolsWidget):
    """
    A customized silx.gui.plot.MaskToolsWidget with larger buttons.
    """

    def __init__(
        self,
        parent: Union[None, QtWidgets.QWidget] = None,
        plot: Union[None, QtWidgets.QWidget] = None,
        **kwargs: dict,
    ):
        MaskToolsWidget.__init__(self, parent, plot)

        for _group_index in [0, 1, 2]:
            _group_layout = self.layout().itemAt(_group_index).widget().layout()
            _button_container = _group_layout.itemAt(0).widget().layout()
            for _index in range(_button_container.count()):
                _widget = _button_container.itemAt(_index).widget()
                if isinstance(_widget, QtWidgets.QAbstractButton):
                    _widget.setIconSize(QtCore.QSize(20, 20))

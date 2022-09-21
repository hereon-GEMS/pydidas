# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
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
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["PydidasMaskToolsWidget"]


from qtpy import QtCore, QtWidgets
from silx.gui.plot.MaskToolsWidget import MaskToolsWidget


class PydidasMaskToolsWidget(MaskToolsWidget):
    """
    A customized silx.gui.plot.MaskToolsWidget with larger buttons.
    """

    def __init__(self, parent=None, plot=None, **kwargs):
        MaskToolsWidget.__init__(self, parent, plot)

        for _group_index in [0, 1, 2]:
            _group_layout = self.layout().itemAt(_group_index).widget().layout()
            _button_container = _group_layout.itemAt(0).widget().layout()
            for _index in range(_button_container.count()):
                _widget = _button_container.itemAt(_index).widget()
                if isinstance(_widget, QtWidgets.QAbstractButton):
                    _widget.setIconSize(QtCore.QSize(20, 20))

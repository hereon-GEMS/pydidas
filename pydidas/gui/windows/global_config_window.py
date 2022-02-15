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
Module with the GlobalConfigWindow class which is a QMainWindow widget
to view and modify the global settings in a seperate Window.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['GlobalConfigWindow']

from qtpy import QtWidgets

from ..global_configuration_frame import GlobalConfigurationFrame


class GlobalConfigWindow(QtWidgets.QMainWindow):
    """
    The GlobalConfigWindow is a standalone QMainWindow with the
    GlobalConfigurationFrame as sole content.
    """
    def __init__(self, parent=None):

        super().__init__(parent)
        _frame = GlobalConfigurationFrame()
        _frame.frame_index = 0
        self.setVisible(False)
        self.setCentralWidget(_frame)

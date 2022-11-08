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
Module with the PydidasApp class which is the pydidas subclassed QApplication.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["PydidasApp"]


from qtpy import QtWidgets, QtCore

from ..core import constants
from ..widgets import PydidasFrameStack
from .utils.qtooltip_event_handler import QTooltipEventHandler


class PydidasApp(QtWidgets.QApplication):

    sig_close_gui = QtCore.Signal()

    def __init__(self, args):
        QtWidgets.QApplication.__init__(self, args)

        self.setOrganizationName("Hereon")
        self.setOrganizationDomain("Hereon/WPI")
        self.setApplicationName("pydidas")

        _font = self.font()
        if _font.pointSize() != constants.STANDARD_FONT_SIZE:
            _font.setPointSize(constants.STANDARD_FONT_SIZE)
            self.setFont(_font)

        self.installEventFilter(QTooltipEventHandler(self))

    @QtCore.Slot()
    def send_gui_close_signal(self):
        """
        Send the signal that the GUI is about to close to all Windows.

        This will also keep a copy of the PydidasFrameStack to prevent deletion.
        """
        self._stack = PydidasFrameStack()
        self.sig_close_gui.emit()

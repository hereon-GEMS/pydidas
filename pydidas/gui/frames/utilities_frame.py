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
Module with the UtilitiesFrame which allows to present and open various utilities.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["UtilitiesFrame"]

from functools import partial

from qtpy import QtCore

from .builders import UtilitiesFrameBuilder
from ..windows import ExportEigerPixelmaskWindow, FileSeriesOperationsWindow


class UtilitiesFrame(UtilitiesFrameBuilder):
    """
    The UtilitiesFrame allows to open various independent utilities.
    """

    menu_icon = "qta::fa.tasks"
    menu_title = "Utilities"
    menu_entry = "Utilities"

    def __init__(self, parent=None, **kwargs):
        UtilitiesFrameBuilder.__init__(self, parent=parent, **kwargs)
        self._child_windows = {}
        self.__window_counter = 0

    def connect_signals(self):
        """
        Connect the required signals and slots to add functionality to widgets.
        """
        self._widgets["button_eiger_mask"].clicked.connect(
            partial(self.create_and_show_temp_window, ExportEigerPixelmaskWindow)
        )
        self._widgets["button_series_operations"].clicked.connect(
            partial(self.create_and_show_temp_window, FileSeriesOperationsWindow)
        )

    @QtCore.Slot(object)
    def create_and_show_temp_window(self, window):
        """
        Show the given temporary window.

        Parameters
        ----------
        window : QtCore.QWidget
            The window to be shown.
        """
        _name = f"temp_window_{self.__window_counter:03d}"
        self.__window_counter += 1
        self._child_windows[_name] = window()
        self._child_windows[_name].sig_closed.connect(
            partial(self.remove_window_from_children, _name)
        )
        self._child_windows[_name].show()

    @QtCore.Slot(str)
    def remove_window_from_children(self, name):
        """
        Remove the specified window from the list of child window.

        Parameters
        ----------
        name : str
            The name key for the window.
        """
        if name in self._child_windows:
            del self._child_windows[name]

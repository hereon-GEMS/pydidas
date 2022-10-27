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
The pydidas.gui.utils.get_main_window module includes a utility function to get the
instance of the MainMenu.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["get_main_menu"]

from qtpy import QtWidgets

from ..main_menu import MainMenu


def get_main_menu():
    """
    Get the pydidas MainMenu instance.

    Returns
    -------
    pydidas.gui.MainMenu
        The instance.
    """
    for _widget in QtWidgets.QApplication.instance().topLevelWidgets():
        if isinstance(_widget, MainMenu):
            return _widget
    raise ValueError("Could not find MainMenu instance")

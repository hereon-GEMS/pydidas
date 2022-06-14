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
Module with the show_busy_mouse class which allows to execute code while showing
the mouse symbol as busy.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["ShowBusyMouse"]

from qtpy import QtCore, QtWidgets


class ShowBusyMouse:
    """
    The ShowBusyMouse class can be used to excute code while displaying the mouse
    as busy.

    Is it designed to be used in a "with ShowBusyMouse():" statement.

    Because the __exit__ method is always executed, even in the case of Exceptions,
    this is safe.
    """

    def __init__(self):
        ...

    def __enter__(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

    def __exit__(self, type_, value, traceback):
        QtWidgets.QApplication.restoreOverrideCursor()

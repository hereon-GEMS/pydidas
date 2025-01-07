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
Context manager which allows to execute code while showing the mouse symbol as busy.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ShowBusyMouse"]


from qtpy import QtCore, QtWidgets


class ShowBusyMouse:
    """
    A context manager which allows executing code while displaying the mouse as busy.

    Is it designed to be used in a "with ShowBusyMouse():" statement.
    """

    def __init__(self):
        pass

    def __enter__(self):
        """
        Set the cursor as busy.
        """
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

    def __exit__(self, type_, value, traceback):
        """
        Restore the generic cursor.

        Note that the exception trace is ignored here.
        """
        QtWidgets.QApplication.restoreOverrideCursor()

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
Module with the critical_warning function for creating a warning with a
simplified syntax.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["critical_warning"]


from qtpy import QtWidgets

from pydidas.widgets.utilities import get_pyqt_icon_from_str


def critical_warning(title: str, text: str):
    """
    Create a QMessageBox with a critical warning and show it.

    Parameters
    ----------
    title : str
        The warning title.
    text : str
        The warning message text.
    """
    _box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, title, text)
    _box.setWindowIcon(get_pyqt_icon_from_str("qt-std::SP_MessageBoxCritical"))
    _box.exec_()

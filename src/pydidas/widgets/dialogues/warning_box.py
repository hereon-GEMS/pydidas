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
Module with WarningBox class for displaying pop-up notifications.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["WarningBox"]


from qtpy import QtWidgets

from pydidas.widgets.utilities import get_pyqt_icon_from_str


class WarningBox(QtWidgets.QMessageBox):
    """
    A QMessageBox with simplified calling syntax to generate a user warning.

    The WarningBox class will set title and message of the QMessageBox
    and call the execute function to display it with a single line of
    code.

    Parameters
    ----------
    title : str
        The message box title.
    msg : str
        The message box text.
    info : str, optional
        Additional informative text. The default is an empty string.
    details : str, optional
        Addition details for the warning. The default is an empty string.
    """

    def __init__(self, title: str, msg: str, info: str = "", details: str = ""):
        super().__init__()
        self.setIcon(self.Warning)
        self.setWindowTitle(title)
        self.setWindowIcon(get_pyqt_icon_from_str("qt-std::SP_MessageBoxWarning"))
        self.setText(msg)
        if info != "":
            self.setInformativeText(info)
        if details != "":
            self.setDetailedText(details)
        self.setStandardButtons(self.Ok)
        self.__exec__()

    def __exec__(self):
        """
        Show the QMessageBox.
        """
        self.exec_()

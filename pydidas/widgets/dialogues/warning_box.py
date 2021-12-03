# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Module with Warning class for showing notifications."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['WarningBox']

from PyQt5 import QtWidgets

class WarningBox(QtWidgets.QMessageBox):
    """
    QMessageBox subclass which simplifies the calling syntax to generate
    user warning.
    """
    def __init__(self, title, msg, info=None, details=None):
        """
        Generate a warning box.

        The __init__ function will set title and message of the QMessageBox
        and call the ececute function to display it with a single line of
        code.

        Parameters
        ----------
        title : str
            The message box title.
        msg : str
            The message box text.
        info : str, optional
            Additional informative text. The default is None.
        details : str, optional
            Addition details for the warning. The default is None.

        Returns
        -------
        None.
        """
        super().__init__()
        self.setIcon(self.Warning)
        self.setWindowTitle(title)
        self.setText(msg)
        if info:
            self.setInformativeText(info)
        if details:
            self.setDetailedText(details)
        self.setStandardButtons(self.Ok)
        self.__exec__()

    def __exec__(self):
        """
        Show the QMessageBox

        Returns
        -------
        None.
        """
        self.exec_()

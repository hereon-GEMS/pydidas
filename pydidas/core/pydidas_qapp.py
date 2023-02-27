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
Module with the PydidasQApplication class which is the pydidas subclassed QApplication.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["PydidasQApplication"]

import sys
import argparse

from qtpy import QtWidgets, QtCore

from . import constants


def parse_cmd_args():
    """
    Parse commandline arguments.

    Returns
    -------
    dict :
        The parsed command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-fontsize", type=int, help="The default font size in points.")
    _kwargs = dict(vars(parser.parse_args()))
    for _name in ["fontsize"]:
        if f"-{_name}" in sys.argv:
            _pos = sys.argv.index(f"-{_name}")
            sys.argv.pop(_pos)
            sys.argv.pop(_pos)
    return _kwargs


class PydidasQApplication(QtWidgets.QApplication):
    """
    PydidasQApplication is the subclassed QApplication used in pydidas for controlling
    the UI and event loops.
    """

    sig_close_gui = QtCore.Signal()
    sig_fontsize_changed = QtCore.Signal(int)

    def __init__(self, args):
        QtWidgets.QApplication.__init__(self, args)

        self._point_size = self.font().pointSize()

        self.setOrganizationName("Hereon")
        self.setOrganizationDomain("Hereon/WPI")
        self.setApplicationName("pydidas")

        _kwargs = parse_cmd_args()
        _point_size = (
            _kwargs.get("fontsize")
            if _kwargs.get("fontsize") is not None
            else constants.STANDARD_FONT_SIZE
        )
        if self._point_size != _point_size:
            self.standard_fontsize = _point_size

    @QtCore.Slot()
    def send_gui_close_signal(self):
        """
        Send the signal that the GUI is about to close to all Windows.
        """
        self.sig_close_gui.emit()

    @property
    def standard_fontsize(self):
        """
        Return the standard fontSize set for the app.

        Returns
        -------
        int
            The font size.
        """
        return self._point_size

    @standard_fontsize.setter
    def standard_fontsize(self, value):
        """
        Set the standard fontsize for the PydidasApp.

        Parameters
        ----------
        value : int
            The new standard fontsize.
        """
        if value == self._point_size:
            return
        self._point_size = value
        _font = self.font()
        _font.setPointSize(self._point_size)
        self.setFont(_font)
        self.sig_fontsize_changed.emit(self._point_size)

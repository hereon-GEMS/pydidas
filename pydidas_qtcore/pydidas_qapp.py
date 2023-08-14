# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
Module with the PydidasQApplication class which is the pydidas subclassed QApplication.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasQApplication"]


import argparse
import sys

from qtpy import QtCore, QtWidgets

from . import fontsize


def parse_cmd_args():
    """
    Parse commandline arguments.

    Returns
    -------
    dict :
        The parsed command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-fontsize",
        type=int,
        help="The default font size in points.",
        default=fontsize.STANDARD_FONT_SIZE,
    )
    parser.add_argument("--qt6", action="store_true")

    _args, _unknown = parser.parse_known_args()
    _kwargs = dict(vars(_args))
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
        _point_size = _kwargs.get("fontsize")
        fontsize.STANDARD_FONT_SIZE = _point_size
        if self._point_size != _point_size:
            self.standard_fontsize = _point_size

    @QtCore.Slot()
    def send_gui_close_signal(self):
        """Send the signal that the GUI is about to close to all Windows."""
        self.sig_close_gui.emit()

    @property
    def standard_fontsize(self) -> int:
        """
        Return the standard fontSize set for the app.

        Returns
        -------
        int
            The font size.
        """
        return self._point_size

    @standard_fontsize.setter
    def standard_fontsize(self, value: int):
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
        fontsize.STANDARD_FONT_SIZE = value
        _font = self.font()
        _font.setPointSizeF(self._point_size)
        self.setFont(_font)
        self.sig_fontsize_changed.emit(self._point_size)

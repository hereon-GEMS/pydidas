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
The pydidas.gui.utils.main_menu_utils module includes a utility functions used in the
MainMenu class or relating to the MainMenu class.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = [
    "get_main_menu",
    "get_standard_state_full_filename",
    "clear_local_log_files",
    "open_doc_in_browser",
]

import os

from qtpy import QtWidgets, QtCore, QtGui

from ..main_menu import MainMenu
from ...core import utils, UserConfigError
from ...widgets.dialogues import QuestionBox


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


def get_standard_state_full_filename(filename):
    """
    Get the standard full path for the state filename.

    This method will search all stored config paths and return the first
    match.

    Parameters
    ----------
    filename : str
        The filename of the state.

    Returns
    -------
    _fname : str
        The file name and path to the config file.
    """
    _paths = QtCore.QStandardPaths.standardLocations(
        QtCore.QStandardPaths.ConfigLocation
    )
    for _path in _paths:
        _fname = os.path.join(_path, filename)
        if os.path.isfile(_fname) and os.access(_fname, os.R_OK):
            return _fname
    raise UserConfigError(
        "No state config file found: Cannot restore the pydidas state because the "
        "current user has not yet stored a pydidas state for the current version."
    )


@QtCore.Slot()
def clear_local_log_files():
    """
    Clear all local log files for this pydidas version.
    """
    _logdir = utils.get_logging_dir()
    _reply = QuestionBox(
        "Clear all local log files",
        "Do you want to delete all local log files for this pydidas version? "
        f"\nLog directory: {_logdir}"
        "\n\nNote that the currently active logfile will be excluded.",
    ).exec_()
    if _reply:
        _access_error = utils.clear_logging_dir()
        if len(_access_error) > 0:
            raise UserConfigError(
                "Could not delete the following log file(s):\n - "
                + "\n - ".join(_access_error)
            )


@QtCore.Slot()
def open_doc_in_browser():
    """
    Open the link to the documentation in the system web browser.
    """
    _ = QtGui.QDesktopServices.openUrl(utils.get_doc_home_qurl())

# This file is part of pydidas.
#
# Copyright 2024, Helmholtz-Zentrum Hereon
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
The pydidas.gui.utils.main_menu_utils module includes a utility functions used in the
MainMenu class or relating to the MainMenu class.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "get_standard_state_full_filename",
    "clear_local_log_files",
    "open_doc_in_browser",
    "get_remote_version",
]

import os
from pathlib import Path

import requests
from qtpy import QtCore, QtGui

from ...core import UserConfigError, utils
from ...core.constants import PYDIDAS_CONFIG_PATHS, PYDIDAS_STANDARD_CONFIG_PATH
from ...widgets.dialogues import QuestionBox


def get_standard_state_full_filename(filename: str) -> Path:
    """
    Get the standard full path for the state filename.

    This method will search all stored config paths and return the first match of
    path/filename combinations which is an accessible file.

    Parameters
    ----------
    filename : str
        The filename of the state.

    Returns
    -------
    _fname : Path
        The file name and path to the config file.
    """
    for _path in PYDIDAS_CONFIG_PATHS:
        _fname = _path.joinpath(filename)
        if _fname.is_file() and os.access(_fname, os.R_OK):
            return _fname
    return PYDIDAS_STANDARD_CONFIG_PATH.joinpath(filename)


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
    _ = QtGui.QDesktopServices.openUrl(utils.DOC_HOME_QURL)


def get_remote_version() -> str:
    """
    Get the remove pydidas version number available on github.

    Returns
    -------
    str :
        The string for the remote version.
    """
    _url = (
        "https://raw.githubusercontent.com/"
        "hereon-GEMS/pydidas/master/pydidas/version.py"
    )
    try:
        _lines = requests.get(_url, timeout=0.5).text.split("\n")
        for _line in _lines:
            if _line.startswith("__version__ ="):
                return _line.split('"')[1]
    except requests.RequestException:
        return "-1"

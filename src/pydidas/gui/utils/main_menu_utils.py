# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "get_standard_state_full_filename",
    "clear_local_log_files",
    "open_doc_in_browser",
    "get_latest_release_tag",
    "get_update_check_text",
    "restore_global_objects",
]

import os
from pathlib import Path

import requests
from qtpy import QtCore, QtGui

from pydidas.contexts import GLOBAL_CONTEXTS
from pydidas.core import UserConfigError, utils
from pydidas.core.constants import PYDIDAS_CONFIG_PATHS, PYDIDAS_STANDARD_CONFIG_PATH
from pydidas.version import VERSION
from pydidas.widgets.dialogues import QuestionBox
from pydidas.workflow import WorkflowTree


TREE = WorkflowTree()


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


def get_latest_release_tag() -> str:
    """
    Get the latest release version of pydidas from GitHub.

    Returns
    -------
    str :
        The string for the latest release version.
    """
    _url = "https://api.github.com/repos/hereon-GEMS/pydidas/releases/latest"
    try:
        _response = requests.get(_url, timeout=1)
        _response.raise_for_status()
    except requests.RequestException:
        return "-1"
    _tag = _response.json()["tag_name"]
    if not isinstance(_tag, str):
        return "-1"
    if _tag.startswith("v"):
        return _tag[1:]
    return _tag


def get_update_check_text(
    remote_version: str, acknowledged_update: str, auto_check: bool
) -> str:
    """
    Get the text with the result of the update check for the user.

    Parameters
    __________
    remote_version : str
        The latest released version of pydidas.
    acknowledged_update : str
        The latest remote version for which the update has been acknowledged.
    auto_check : bool
        Flag to set the information if the update check was performed automatically.
    """
    if remote_version > VERSION:
        _text = (
            "A new version of pydidas is available.\n\n"
            f"    Locally installed version: {VERSION}\n"
            f"    Latest release: {remote_version}.\n\n"
        )
        if auto_check and remote_version not in ["-1", acknowledged_update]:
            _text += "Please update pydidas to benefit from the latest improvements."
    else:
        _text = (
            f"The locally installed version of pydidas (version {VERSION}) \n"
            "is the latest available version. No actions required."
        )
    return _text


def restore_global_objects(state: dict):
    """
    Get the states of pydidas's global objects (ScanContext,
    DiffractionExperimentContext, WorkflowTree)

    Parameters
    ----------
    state : dict
        The restored global states which includes the states for the
        global objects.
    """
    try:
        TREE.restore_from_string(state["workflow_tree"])
    except KeyError:
        raise UserConfigError("Cannot import Workflow. Not all plugins found.")
    for _context_key, _context in GLOBAL_CONTEXTS.items():
        for _key, _val in state[_context_key].items():
            _context.set_param_value(_key, _val)

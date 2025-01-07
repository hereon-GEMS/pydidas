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
Script to remove all files with stored GUI states, for example if they are broken.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["remove_pydidas_stored_gui_states", "remove_pydidas_log_files"]


import os
import shutil
from pathlib import Path
from typing import Union

from qtpy import QtCore


def remove_pydidas_stored_gui_states(
    version: Union[None, str] = None, confirm_finish: bool = True, verbose: bool = True
):
    """
    Remove the stored GUI states in case they are broken.

    Parameters
    ----------
    version : Union[None, str]
        The version string. If None, this defaults to the installed version. The
        default is None.
    confirm_finish : bool, optional
        Flag to confirm the script is finished. The default is True.
    verbose : bool, optional
        Flag to print status messages. The default is True.
    """
    from pydidas.version import VERSION

    _version = version if version is not None else VERSION
    _config_path = Path(
        QtCore.QStandardPaths.standardLocations(QtCore.QStandardPaths.ConfigLocation)[0]
    )
    if not _config_path.stem == "pydidas":
        if not _config_path.stem == "Hereon":
            _config_path = _config_path.joinpath("Hereon")
        _config_path = _config_path.joinpath("pydidas")
    _state_fname = _config_path.joinpath(f"pydidas_gui_state_{_version}.yaml")
    _exit_state_fname = _config_path.joinpath(f"pydidas_gui_exit_state_{_version}.yaml")
    if _state_fname.is_file():
        os.remove(_state_fname)
    if _exit_state_fname.is_file():
        os.remove(_exit_state_fname)
    if verbose:
        print(
            "\n"
            + "=" * 80
            + "\n=== Successfully removed the files with pydidas's stored GUI states.\n"
            + "=" * 80
            + "\n"
        )
    if confirm_finish:
        input("Press <Enter> to exit the script. ")


def remove_pydidas_log_files(
    version: Union[None, str] = None, confirm_finish: bool = True, verbose: bool = True
):
    """
    Remove the stored log and exception files for the given version.

    If no version is given, this defaults to the currently installed version.

    Parameters
    ----------
    version : Union[None, str]
        The version string. If None, this defaults to the installed version. The
        default is None.
    confirm_finish : bool, optional
        Flag to confirm the script is finished. The default is True.
    verbose : bool, optional
        Flag to print status messages. The default is True.
    """
    from pydidas.version import VERSION

    _version = version if version is not None else VERSION
    _qt_docs_path = QtCore.QStandardPaths.standardLocations(
        QtCore.QStandardPaths.DocumentsLocation
    )[0]
    _docs_path = Path(_qt_docs_path).joinpath("pydidas", _version)
    try:
        shutil.rmtree(_docs_path)
    except (FileNotFoundError, PermissionError):
        pass
    if verbose:
        print(
            "\n"
            + "=" * 80
            + "\n=== Successfully removed pydidas's logfiles.\n"
            + "=" * 80
            + "\n"
        )
    if confirm_finish:
        input("Press <Enter> to exit the script. ")


def run():
    """
    Remove local files from the system.
    """
    remove_pydidas_stored_gui_states(confirm_finish=False, verbose=True)
    remove_pydidas_log_files(confirm_finish=True, verbose=True)


if __name__ == "__main__":
    run()

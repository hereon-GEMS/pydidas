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
Script to reset all stored QSettings to default in case a setting breaks
the GUI startup.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["remove_pydidas"]


import os
import shutil
import sys

from qtpy import QtCore


def remove_pydidas():
    """
    Clear all stored pydidas QSettings and all local logs and config files.
    """
    print(
        "#####################################################\n"
        "# Note: pydidas system information is user specific #\n"
        "# and will only be removed for the current user!    #\n"
        "#####################################################\n"
    )
    _reply = input(
        "Do you really want to remove all local pydidas settings from the system? "
        "(y/[n]) "
    )
    if _reply.upper() not in ["Y", "YES"]:
        input("\nAborted by user request. \n\nPress <Enter> to continue.")
        return

    # Remove all system registry settings
    print("\nRemoving registry settings...", end="")
    if sys.platform.startswith("win"):
        _qs = QtCore.QSettings("Hereon", "pydidas")
        _hereon_entry = _qs.fileName()[: -len(os.sep + "pydidas")]
        _hereon_qs = QtCore.QSettings(_hereon_entry, QtCore.QSettings.NativeFormat)
        _hereon_qs.remove("pydidas")
        if len(_hereon_qs.allKeys()) == 0:
            _parent_entry = _hereon_qs.fileName()[: -len(os.sep + "Hereon")]
            _parent_qs = QtCore.QSettings(_parent_entry, QtCore.QSettings.NativeFormat)
            _parent_qs.remove("Hereon")
    elif sys.platform == "linux":
        _qs = QtCore.QSettings("Hereon", "pydidas")
        _qs_file = _qs.fileName()
        _qs_dir = os.path.dirname(_qs_file)
        if os.path.exists(_qs_file):
            shutil.remove(_qs_file)
        if len(os.listdir(_qs_dir)) == 0:
            shutil.remove(_qs_dir)
    else:
        raise TypeError("The system architecture is not supported by pydidas!")
    print("done!")

    # Remove all local config files
    print("\nRemoving local configuration files...", end="")
    _path = QtCore.QStandardPaths.standardLocations(
        QtCore.QStandardPaths.ConfigLocation
    )[0]
    if not _path.replace(os.sep, "/").endswith("Hereon/pydidas"):
        _path = os.path.join(_path, "Hereon", "pydidas")
    if os.path.exists(_path):
        shutil.rmtree(_path)
    _top_path = os.path.dirname(_path)
    if os.path.exists(_top_path) and len(os.listdir(_top_path)) == 0:
        shutil.rmtree(_top_path)
    print("done!")

    # Remove all local documents and logs
    print("\nRemoving local documents and logfiles...", end="")
    _qt_docs_path = QtCore.QStandardPaths.standardLocations(
        QtCore.QStandardPaths.DocumentsLocation
    )[0]
    _docs_path = os.path.join(_qt_docs_path, "pydidas")
    shutil.rmtree(_docs_path)
    print("done!")

    print("\nSuccessfully removed all pydidas entries from the operating system.")
    input("Press <Enter> to continue.")


if __name__ == "__main__":
    remove_pydidas()

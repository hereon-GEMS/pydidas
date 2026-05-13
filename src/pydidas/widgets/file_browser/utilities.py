# This file is part of pydidas.
#
# Copyright 2026, Helmholtz-Zentrum Hereon
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
#
# This content was created using the AI tool GPT-5.3-Codex


"""
Module utility function for the file browser widgets and models.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ChangeFilter", "is_network_volume"]

import platform
from typing import Any

from PyQt5.QtCore import QSortFilterProxyModel
from qtpy import QtCore

from pydidas import IS_QT6


# The network filesystem types are based on common types used across platforms,
# but NFS mounts are not included as they are checked separately:
_NETWORK_FS_TYPES = {"cifs", "smbfs", "smb2", "fuse.sshfs", "fuse.s3fs", "davfs"}

__SYSTEM = platform.system().lower()


class ChangeFilter:
    """
    The ChangeFilter context is used to change the filter and
    wrap the different Qt5 / Qt6 method calls."""

    def __init__(self, model: QSortFilterProxyModel) -> None:
        self._model = model

    def __enter__(self) -> "ChangeFilter":
        """Start the context manager."""
        if IS_QT6:
            self._model.beginFilterChange()
        return self

    def __exit__(
        self,
        type_: type[BaseException] | None,
        value: BaseException | None,
        traceback: Any,
    ) -> None:
        """Exit the context manager."""
        if IS_QT6:
            self._model.endFilterChange()
        else:
            self._model.invalidateFilter()


def is_network_volume(volume: QtCore.QStorageInfo) -> bool:
    """Heuristic check whether volume is network-mounted."""
    _device = bytes(volume.device()).decode(errors="ignore")
    _fs_type = bytes(volume.fileSystemType()).decode(errors="ignore").lower()

    if _fs_type in _NETWORK_FS_TYPES or _fs_type.startswith("nfs"):
        return True

    if __SYSTEM == "windows":
        # Local volumes start with \\\\?\\Volume
        return not _device.startswith("\\\\?\\Volume")
    if __SYSTEM in ["linux", "unix"]:
        # SMB/CIFS style: //server/share
        # NFS style: hostname:/path
        return _device.startswith("//") or (
            ":/" in _device and not _device.startswith("/")
        )
    if __SYSTEM == "darwin":
        return str(volume.rootPath()).startswith("/Volumes/") and ":" in _device
    return False

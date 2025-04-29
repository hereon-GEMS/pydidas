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
Module with the DirectoryExplorerFilterModel widget, which is used to filter
the file system.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DirectoryExplorerFilterModel"]


import platform

from qtpy import QtCore
from qtpy.QtCore import QSortFilterProxyModel

from pydidas.core import PydidasQsettings


AscendingOrder = QtCore.Qt.AscendingOrder


class DirectoryExplorerFilterModel(QSortFilterProxyModel):
    """
    A proxy sort model which allows hiding network drives and filter for files.
    """

    def __init__(self, parent=None):
        QSortFilterProxyModel.__init__(self, parent)
        self.setRecursiveFilteringEnabled(True)
        self.__accept_network_locations = PydidasQsettings().q_settings_get(
            "directory_explorer/show_network_drives", dtype=bool, default=True
        )
        __storage = QtCore.QStorageInfo()
        if platform.system() == "Windows":
            __prefix = "\\\\?\\Volume"
        elif platform.system() in ["Unix", "Linux"]:
            __prefix = "/dev/"
        elif platform.system() == "Darwin":  # for macOS
            __prefix = "/Volumes"
        else:
            raise SystemError(
                "Only Windows, Linux, and macOS operating systems are supported!"
            )
        self.__network_drives = [
            _vol.rootPath()
            for _vol in __storage.mountedVolumes()
            # if not _vol.device().toStdString().startswith(__prefix)
            # because toStdString does not work with Qt 5.15.2, fall back :
            if not bytes(_vol.device()).decode().startswith(__prefix)
        ]
        self.__filename_filter_active: bool = False
        self.__filter_pattern: QtCore.QRegularExpression | None = None

    @QtCore.Slot(bool)
    def toggle_network_location_acceptance(self, acceptance: bool):
        """
        Toggle the acceptance of network locations.

        Parameters
        ----------
        acceptance : bool
            Flag whether to accept network drives in the filter or not.
        """
        self.__accept_network_locations = acceptance
        self.invalidateFilter()

    @QtCore.Slot(str)
    def toggle_filter_string(self, filter_string: str):
        """
        Toggle the filter string.

        Parameters
        ----------
        filter_string : str
            The filter string to be used.
        """
        self.__filename_filter_active = len(filter_string) > 0
        escaped_filter_string = QtCore.QRegularExpression.escape(filter_string)
        self.__filter_pattern = QtCore.QRegularExpression(
            escaped_filter_string.replace("\\*", ".*").replace("\\?", ".")
        )
        self.invalidateFilter()

    def filterAcceptsRow(
        self, source_row: int, source_parent: QtCore.QModelIndex
    ) -> bool:
        """
        Filter rows based on them being a network drive.

        Parameters
        ----------
        source_row : int
            The model source row.
        source_parent : QtCore.QModelIndex
            The parent index.
        """
        _index = self.sourceModel().index(source_row, 0, source_parent)
        _filter_accepted = True
        if self.__filename_filter_active:
            _file_info = self.sourceModel().fileInfo(_index)
            if _file_info.isFile():
                _filter_accepted = self.__filter_pattern.match(
                    _file_info.fileName()
                ).hasMatch()

        if self.__accept_network_locations:
            _network_accepted = True
        else:
            while _index.parent().isValid():
                _index = _index.parent()
            _network_accepted = (
                self.sourceModel().filePath(_index) not in self.__network_drives
            )
        return _filter_accepted and _network_accepted

    def lessThan(
        self, entry_a: QtCore.QModelIndex, entry_b: QtCore.QModelIndex
    ) -> bool:
        """
        Reimplement lessThan to sort directories and files separately.

        Parameters
        ----------
        entry_a : QtCore.QModelIndex
            The first entry to be compared.
        entry_b : QtCore.QModelIndex
            The second entry to be compared.

        Returns
        -------
        bool
            Flag whether entry_a should be displayed before entry_b.
        """
        _ascending = self.sortOrder() == AscendingOrder
        _info_a = self.sourceModel().fileInfo(entry_a)
        _info_b = self.sourceModel().fileInfo(entry_b)

        if (not _info_a.isDir()) and _info_b.isDir():
            return not _ascending
        if _info_a.isDir() and not _info_b.isDir():
            return _ascending
        return QSortFilterProxyModel.lessThan(self, entry_a, entry_b)

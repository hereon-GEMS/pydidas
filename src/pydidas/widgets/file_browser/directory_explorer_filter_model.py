# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DirectoryExplorerFilterModel"]


import platform

from qtpy import QtCore, QtWidgets
from qtpy.QtCore import QSortFilterProxyModel, Qt

from pydidas.core import PydidasQsettings
from pydidas.widgets.file_browser.utilities import ChangeFilter


class DirectoryExplorerFilterModel(QSortFilterProxyModel):
    """
    A proxy sort/filter model for ``QFileSystemModel``.

    Supports hiding network drives and filtering visible files by a
    filename pattern.  Large-directory loads can be bracketed with
    :meth:`suspend_filtering` / :meth:`resume_filtering` to avoid
    per-row Python overhead during bulk insertion.
    """

    def __init__(self, parent=None):
        """
        Initialise the filter model.

        Parameters
        ----------
        parent : QObject or None, optional
            The parent object. The default is None.
        """
        QSortFilterProxyModel.__init__(self, parent)  # type: ignore[arg-type]
        self.setRecursiveFilteringEnabled(False)
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
        self.__network_drives = {
            _vol.rootPath()
            for _vol in __storage.mountedVolumes()
            # if not _vol.device().toStdString().startswith(__prefix)
            # because toStdString does not work with Qt 5.15.2, fall back :
            if not bytes(_vol.device()).decode().startswith(__prefix)
        }
        self.__filter_str: str = ""
        self.__filename_filter_active: bool = False
        self.__filter_pattern: QtCore.QRegularExpression | None = None
        self.__sort_ascending: bool = True
        self.__filtering_suspended: bool = False
        # Key: file path string (stable, unique per file — avoids internalId reuse
        # collisions when navigating between directories in QFileSystemModel).
        self.__file_info_cache: dict[str, tuple[bool, str]] = {}
        self.__top_root_cache: dict[tuple[int, int, int], str] = {}
        self.__network_acceptance_cache: dict[str, bool] = {}

    def setSourceModel(self, sourceModel: QtCore.QAbstractItemModel) -> None:
        """Set source model and connect invalidation hooks for runtime caches."""
        if not isinstance(sourceModel, QtWidgets.QFileSystemModel):
            raise TypeError("DirectoryExplorerFilterModel requires a QFileSystemModel.")
        super().setSourceModel(sourceModel)  # type: ignore[arg-type]
        self.__clear_runtime_caches()
        sourceModel.modelReset.connect(self.__clear_runtime_caches)  # type: ignore[arg-type]
        if hasattr(sourceModel, "directoryLoaded"):
            sourceModel.directoryLoaded.connect(self.__clear_row_info_cache)  # type: ignore[attr-defined]

    @staticmethod
    def __index_key(index: QtCore.QModelIndex) -> tuple[int, int, int]:
        """Get a lightweight cache key for top-root lookups (parent-chain walks)."""
        return int(index.internalId()), index.row(), index.column()

    @QtCore.Slot()
    def __clear_runtime_caches(self) -> None:
        """Clear caches used for fast filtering and sorting."""
        self.__file_info_cache.clear()
        self.__top_root_cache.clear()
        self.__network_acceptance_cache.clear()

    @QtCore.Slot()
    def __clear_row_info_cache(self) -> None:
        """Clear only the row metadata cache on directory load."""
        self.__file_info_cache.clear()
        self.__top_root_cache.clear()

    def __get_file_info_from_index(self, index: QtCore.QModelIndex) -> tuple[bool, str]:
        """Cache and return file metadata as (is_file, file_name)."""
        _path = self.sourceModel().filePath(index)  # type: ignore[attr-defined]
        _cached = self.__file_info_cache.get(_path)
        if _cached is not None:
            return _cached
        _file_info = self.sourceModel().fileInfo(index)  # type: ignore[attr-defined]
        _info = (_file_info.isFile(), _file_info.fileName())
        self.__file_info_cache[_path] = _info
        return _info

    def __get_top_root_path(self, index: QtCore.QModelIndex) -> str:
        """Return cached top-level root path for a source index."""
        _key = self.__index_key(index)
        _cached = self.__top_root_cache.get(_key)
        if _cached is not None:
            return _cached
        _root_index = index
        while _root_index.parent().isValid():  # type: ignore[attr-defined]
            _root_index = _root_index.parent()
        _root_path = self.sourceModel().filePath(_root_index)  # type: ignore[attr-defined]
        self.__top_root_cache[_key] = _root_path
        return _root_path

    def __is_network_location_accepted(self, index: QtCore.QModelIndex) -> bool:
        """Check and cache network acceptance for an index root path."""
        if self.__accept_network_locations:
            return True
        _root_path = self.__get_top_root_path(index)
        _cached = self.__network_acceptance_cache.get(_root_path)
        if _cached is not None:
            return _cached
        _accepted = _root_path not in self.__network_drives
        self.__network_acceptance_cache[_root_path] = _accepted
        return _accepted

    @QtCore.Slot(bool)
    def show_network_drives(self, acceptance: bool) -> None:
        """
        Toggle the filtering of network locations.

        Parameters
        ----------
        acceptance : bool
            Flag whether to accept network drives in the filter or not.
        """
        if self.__accept_network_locations == acceptance:
            return
        with ChangeFilter(self):  # type: ignore[arg-type]
            self.__accept_network_locations = acceptance
            self.__network_acceptance_cache.clear()

    @QtCore.Slot(str)
    def change_filter_string(self, filter_string: str) -> None:
        """
        Change and update the filter string.

        Parameters
        ----------
        filter_string : str
            The filter string to be used.
        """
        if filter_string == self.__filter_str:
            return
        with ChangeFilter(self):  # type: ignore[arg-type]
            self.__filename_filter_active = len(filter_string) > 0
            self.__filter_str = filter_string
            escaped_filter_string = QtCore.QRegularExpression.escape(filter_string)
            self.__filter_pattern = QtCore.QRegularExpression(
                escaped_filter_string.replace("\\*", ".*").replace("\\?", ".")
            )
            self.__file_info_cache.clear()

    def suspend_filtering(self) -> None:
        """
        Suspend per-row filtering to avoid Python call overhead during large
        directory loads.

        While suspended, filterAcceptsRow returns True immediately for all rows.
        Call resume_filtering() once the directory has finished loading to
        re-apply the active filter in a single pass.
        """
        self.__filtering_suspended = True

    def resume_filtering(self) -> None:
        """
        Resume filtering after a directory load is complete.

        Clears the row metadata cache and – only when active filter criteria
        could reject rows – invalidates the filter so criteria are applied in
        one pass.  When no filename filter is active and network locations are
        accepted (the common navigation case) no invalidation is needed because
        every row already passes: skipping it avoids an O(n) re-evaluation over
        the entire accumulated model.
        """
        if not self.__filtering_suspended:
            return
        self.__filtering_suspended = False
        self.__clear_row_info_cache()
        # Only force a full re-evaluation when something could actually reject rows.
        if self.__filename_filter_active or not self.__accept_network_locations:
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
        if self.__filtering_suspended:
            return True
        _index = self.sourceModel().index(source_row, 0, source_parent)
        if not self.__is_network_location_accepted(_index):
            return False
        if not self.__filename_filter_active:
            return True
        _is_file, _file_name = self.__get_file_info_from_index(_index)
        if not _is_file:
            return True
        return self.__filter_pattern.match(_file_name).hasMatch()

    def sort(
        self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder
    ) -> None:
        """Re-implement sort to store the sort order."""
        self.__sort_ascending = bool(order == Qt.SortOrder.AscendingOrder)
        self.__file_info_cache.clear()
        super().sort(column, order)

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
        _is_file_a, _ = self.__get_file_info_from_index(entry_a)
        _is_file_b, _ = self.__get_file_info_from_index(entry_b)

        if _is_file_a and not _is_file_b:
            return not self.__sort_ascending
        if (not _is_file_a) and _is_file_b:
            return self.__sort_ascending
        return QSortFilterProxyModel.lessThan(self, entry_a, entry_b)  # type: ignore[arg-type]

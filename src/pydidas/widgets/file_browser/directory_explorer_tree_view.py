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
Module with the DirectoryExplorerTreeView widget, which is an implementation of a
QTreeView for a file system model.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DirectoryExplorerTreeView"]


import os
from pathlib import Path
from typing import Any, cast

from qtpy import QtCore, QtWidgets

from pydidas.core.constants import POLICY_EXP_EXP
from pydidas.core.utils import apply_qt_properties, get_directory


AscendingOrder = QtCore.Qt.AscendingOrder
QSortFilterProxyModel = QtCore.QSortFilterProxyModel


class _DirectoryExplorerTreeView(QtWidgets.QTreeView):
    """
    The DirectoryExplorerTreeView is an implementation of a QTreeView widget with a
    file system model to display the contents of directories.

    Parameters
    ----------
    **kwargs : Any
        Supported keywords are any keywords that are supported by QTreeView.
    """

    init_kwargs = ["parent"]

    def __init__(self, **kwargs: Any) -> None:
        QtWidgets.QTreeView.__init__(self, kwargs.get("parent", None))  # type: ignore[arg-type]
        apply_qt_properties(self, **kwargs)  # type: ignore[arg-type]
        self.raw_model: QtCore.QAbstractItemModel | None = None
        self._proxy_models: list[QtCore.QSortFilterProxyModel] = []
        self._pending_expand_paths: list[str] = []
        self._pending_expand_retry_count = 0

    def setModel(self, model: QtCore.QAbstractItemModel) -> None:
        """
        Set the model of the directory explorer.

        Parameters
        ----------
        model : QtCore.QAbstractItemModel
            The model to be used.
        """
        self._proxy_models = []
        _raw_model = model
        while isinstance(_raw_model, QtCore.QSortFilterProxyModel):
            self._proxy_models.append(_raw_model)
            _raw_model = _raw_model.sourceModel()
        self.raw_model = _raw_model
        QtWidgets.QTreeView.setModel(self, model)  # type: ignore[arg-type]
        self.setAnimated(False)
        self.setUniformRowHeights(True)
        self.setIndentation(12)
        self._connect_model_ready_signal()
        self.setColumnWidth(0, 400)
        self.setColumnWidth(1, 70)
        self.setColumnWidth(2, 100)
        self.setColumnWidth(3, 140)
        self.setSizePolicy(*POLICY_EXP_EXP)

    def _connect_model_ready_signal(self) -> None:
        """Connect to model ready signal for deferred sorting."""
        if self.raw_model is None:
            return
        if hasattr(self.raw_model, "directoryLoaded"):
            try:
                cast(Any, self.raw_model).directoryLoaded.connect(
                    self._on_directory_loaded
                )
            except (AttributeError, TypeError):
                self._fallback_defer_sorting()
        else:
            self._fallback_defer_sorting()

    def _fallback_defer_sorting(self) -> None:
        """Fallback timer-based deferred sorting for non-filesystem models."""
        QtCore.QTimer.singleShot(1000, self._enable_deferred_sorting)

    @QtCore.Slot(str)
    def _on_directory_loaded(self, path: str) -> None:
        """Enable sorting when the first directory is loaded."""
        if self.raw_model is None:
            return
        _root_path = (
            cast(Any, self.raw_model).rootPath()
            if hasattr(self.raw_model, "rootPath")
            else ""
        )
        _norm_loaded = os.path.normcase(os.path.normpath(path))
        _norm_root = os.path.normcase(os.path.normpath(str(_root_path)))
        if _norm_loaded == _norm_root:
            self._enable_deferred_sorting()
            try:
                cast(Any, self.raw_model).directoryLoaded.disconnect(
                    self._on_directory_loaded
                )
            except (AttributeError, TypeError):
                pass

    @QtCore.Slot()
    def _enable_deferred_sorting(self) -> None:
        """Enable sorting after initial tree render is complete."""
        self.setSortingEnabled(True)
        self.sortByColumn(0, QtCore.Qt.SortOrder.AscendingOrder)

    def _map_from_source(self, index: QtCore.QModelIndex) -> QtCore.QModelIndex:
        """
        Map a source-model index to the tree view model index.

        Parameters
        ----------
        index : QtCore.QModelIndex
            The source-model index.

        Returns
        -------
        QtCore.QModelIndex
            The mapped view index.
        """
        _index = index
        for _proxy_model in reversed(self._proxy_models):
            _index = _proxy_model.mapFromSource(_index)
        return _index

    def _schedule_expand_step(self) -> None:
        """Schedule the next deferred expansion step."""
        QtCore.QTimer.singleShot(0, self._expand_next_pending_path)

    def _expand_next_pending_path(self) -> None:
        """Expand the next pending source path in the tree view."""
        if self.raw_model is None or len(self._pending_expand_paths) == 0:
            self._pending_expand_retry_count = 0
            return

        _source_index = cast(Any, self.raw_model).index(self._pending_expand_paths[0])
        if not _source_index.isValid():
            self._pending_expand_retry_count += 1
            if self._pending_expand_retry_count <= 10:
                self._schedule_expand_step()
            else:
                self._pending_expand_paths = []
                self._pending_expand_retry_count = 0
            return

        _view_index = self._map_from_source(_source_index)
        if not _view_index.isValid():
            self._pending_expand_paths = []
            self._pending_expand_retry_count = 0
            return

        self._pending_expand_retry_count = 0
        self.expand(_view_index)
        self._pending_expand_paths.pop(0)
        if len(self._pending_expand_paths) == 0:
            self.scrollTo(_view_index)
            return
        self._schedule_expand_step()

    def expand_to_path(self, path: str) -> None:
        """
        Expand the treeview to a given path.

        Parameters
        ----------
        path : str
            The full path to expand.
        """
        if self.raw_model is None:
            return

        _path = get_directory(Path(path))
        _expand_paths = [str(_path)]
        _source_root = (
            cast(Any, self.raw_model).rootPath()
            if hasattr(self.raw_model, "rootPath")
            else ""
        )
        _norm_source_root = os.path.normcase(os.path.normpath(str(_source_root)))
        while _path.parent != _path:
            _norm_path = os.path.normcase(os.path.normpath(str(_path)))
            if _norm_source_root and _norm_path == _norm_source_root:
                break
            _path = _path.parent
            _expand_paths.insert(0, str(_path))
        if _expand_paths != self._pending_expand_paths:
            self._pending_expand_paths = _expand_paths
            self._pending_expand_retry_count = 0
            self._schedule_expand_step()

    def sizeHint(self) -> QtCore.QSize:
        """
        Overload the generic sizeHint.

        Returns
        -------
        QtCore.QSize
            The updated size hint.
        """
        return QtCore.QSize(400, 4000)


class DirectoryExplorerTreeView(QtWidgets.QTreeView):
    """
    The DirectoryExplorerTreeView is an implementation of a QTreeView widget with a
    file system model to display the contents of directories.

    Parameters
    ----------
    **kwargs : Any
        Supported keywords are any keywords that are supported by QTreeView.
    """

    init_kwargs = ["parent"]

    def __init__(self, **kwargs: Any) -> None:
        QtWidgets.QTreeView.__init__(self, kwargs.get("parent", None))
        apply_qt_properties(self, **kwargs)
        self.raw_model: QtCore.QAbstractItemModel | None = None

    def setModel(self, model: QtCore.QAbstractItemModel):
        """
        Set the model of the directory explorer.

        Parameters
        ----------
        model : QtCore.QAbstractItemModel
            The model to be used. This must be an instance of a QFileSystemModel
            or a QSortFilterProxyModel with a QFileSystemModel as source.
        """
        if isinstance(model, QtCore.QSortFilterProxyModel):
            _source = model.sourceModel()
            if not isinstance(_source, QtWidgets.QFileSystemModel):
                raise TypeError(
                    "The DirectoryExplorerTreeView only supports QFileSystemModel "
                    "or QSortFilterProxyModel with QFileSystemModel as source."
                )
            self.raw_model = _source
        elif isinstance(model, QtWidgets.QFileSystemModel):
            self.raw_model = model
        else:
            raise TypeError(
                "The DirectoryExplorerTreeView only supports QFileSystemModel"
            )
        QtWidgets.QTreeView.setModel(self, model)
        self.setAnimated(False)
        self.setIndentation(12)
        self.setSortingEnabled(True)
        for _col, _width in [(0, 400), (1, 70), (2, 100), (3, 140)]:
            self.setColumnWidth(_col, _width)
        self.setSizePolicy(*POLICY_EXP_EXP)
        self.sortByColumn(0, QtCore.Qt.SortOrder.AscendingOrder)

    def expand_to_path(self, path: str):
        """
        Expand the tree view to a given path.

        Parameters
        ----------
        path : str
            The full path to expand.
        """
        _index = self.raw_model.index(path)
        _indices = []
        while _index.isValid():
            _indices.insert(0, _index)
            _index = _index.parent()
        for _ix in _indices:
            self.setExpanded(self.model().mapFromSource(_ix), True)

    def sizeHint(self) -> QtCore.QSize:
        """
        Overload the generic sizeHint.

        Returns
        -------
        QtCore.QSize
            The updated size hint.
        """
        return QtCore.QSize(400, 4000)

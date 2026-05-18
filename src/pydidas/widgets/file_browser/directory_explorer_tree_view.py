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


from pathlib import Path
from typing import Any

from qtpy import QtCore, QtWidgets

from pydidas.core.constants import POLICY_EXP_EXP
from pydidas.core.utils import apply_qt_properties, get_directory


AscendingOrder = QtCore.Qt.AscendingOrder
QSortFilterProxyModel = QtCore.QSortFilterProxyModel

_EXPAND_PATH_RETRY_LIMIT = 10


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
        QtWidgets.QTreeView.__init__(self, kwargs.get("parent", None))  # type: ignore[arg-type]
        apply_qt_properties(self, **kwargs)  # type: ignore[arg-type]
        self._raw_model: QtWidgets.QFileSystemModel | None = None
        self._proxy_model: QtCore.QSortFilterProxyModel | None = None
        self._pending_expand_paths: list[str] = []
        self._pending_expand_retry_count = 0
        self.__expand_scroll_hint: QtWidgets.QAbstractItemView.ScrollHint = (
            QtWidgets.QAbstractItemView.EnsureVisible
        )

    def setModel(self, model: QtCore.QAbstractItemModel) -> None:
        """
        Set the model of the directory explorer.

        Parameters
        ----------
        model : QtCore.QAbstractItemModel
            The model to be used.
        """
        if not isinstance(
            model, (QtCore.QSortFilterProxyModel, QtWidgets.QFileSystemModel)
        ):
            raise TypeError(
                "The DirectoryExplorerTreeView only supports QFileSystemModel or "
                "QSortFilterProxyModel with QFileSystemModel as source."
            )
        if isinstance(model, QtCore.QSortFilterProxyModel):
            _raw_model = model.sourceModel()
            if not isinstance(_raw_model, QtWidgets.QFileSystemModel):
                raise TypeError(
                    "The DirectoryExplorerTreeView only supports QFileSystemModel or "
                    "QSortFilterProxyModel with QFileSystemModel as source."
                )
            self._proxy_model = model
            self._raw_model = _raw_model
        elif isinstance(model, QtWidgets.QFileSystemModel):
            self._proxy_model = None
            self._raw_model = model
        super().setModel(model)  # type: ignore[arg-type]
        self.setAnimated(False)
        self.setUniformRowHeights(True)
        self.setIndentation(12)
        for _col, _width in [(0, 400), (1, 70), (2, 100), (3, 140)]:
            self.setColumnWidth(_col, _width)
        self.setSizePolicy(*POLICY_EXP_EXP)
        self._raw_model.directoryLoaded.connect(self._on_directory_loaded)

    def sizeHint(self) -> QtCore.QSize:
        """
        Overload the generic sizeHint.

        Returns
        -------
        QtCore.QSize
            The updated size hint.
        """
        return QtCore.QSize(400, 4000)

    @QtCore.Slot(str)
    def _on_directory_loaded(self, path: str) -> None:
        """Enable sorting when the first directory is loaded."""
        _root_path = Path(self._raw_model.rootPath())
        _loaded_path = Path(path)
        if _root_path == _loaded_path:
            self._raw_model.directoryLoaded.disconnect(self._on_directory_loaded)
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
        if not index.isValid() or self._raw_model is None:
            return QtCore.QModelIndex()
        if self._proxy_model is None:
            return index
        return self._proxy_model.mapFromSource(index)

    def _expand_next_pending_path(self) -> None:
        """Expand the next pending source path in the tree view."""
        if self._raw_model is None or len(self._pending_expand_paths) == 0:
            self._pending_expand_retry_count = 0
            return

        _source_index = self._raw_model.index(self._pending_expand_paths[0])
        # Check if the model has loaded the requested directory:
        if not _source_index.isValid():
            self._pending_expand_retry_count += 1
            if self._pending_expand_retry_count <= _EXPAND_PATH_RETRY_LIMIT:
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

        self.expand(_view_index)
        self._pending_expand_paths.pop(0)
        self._pending_expand_retry_count = 0
        if len(self._pending_expand_paths) == 0:
            self.scrollTo(_view_index, self.__expand_scroll_hint)
            _selection_model = self.selectionModel()
            _selection_model.select(_view_index, QtCore.QItemSelectionModel.Select)
            self.setCurrentIndex(_view_index)
            return
        self._schedule_expand_step()

    def _schedule_expand_step(self) -> None:
        """
        Schedule the next deferred expansion step.

        This timer will allow the Qt event loop to process other signals
        and events, such as loading the directory contents, before attempting
        to expand the next path.
        """
        QtCore.QTimer.singleShot(0, self._expand_next_pending_path)

    def expand_to_path(self, path: Path | str, show_at_top: bool = False) -> None:
        """
        Expand the QTreeView to a given path.

        Parameters
        ----------
        path : Path or str
            The full path to expand.
        show_at_top : bool, optional
            Flag whether to show the given path at the top of the
            QTreeView or leave the current layout.
        """
        if self._raw_model is None:
            return
        self.__expand_scroll_hint = (
            QtWidgets.QAbstractItemView.PositionAtTop
            if show_at_top
            else QtWidgets.QAbstractItemView.EnsureVisible
        )
        _path = get_directory(path)
        _expand_paths = [str(_path)]
        _source_root = Path(self._raw_model.rootPath())
        for _ancestor in _path.parents:
            _expand_paths.insert(0, str(_ancestor))
            if _source_root is not None and _ancestor == _source_root:
                break
        self._pending_expand_paths = _expand_paths
        self._pending_expand_retry_count = 0
        self._schedule_expand_step()
        if _expand_paths != self._pending_expand_paths:
            self._pending_expand_paths = _expand_paths
            self._pending_expand_retry_count = 0
            self._schedule_expand_step()

    def select_item(self, name: str) -> None:
        """
        Select the item with the given name to highlight.

        Parameters
        ----------
        name : str
            The name of the item to highlight.
        """
        _index = self._raw_model.index(name)
        if self._proxy_model is not None:
            _index = self._map_from_source(_index)
            _model = self._proxy_model
        else:
            _model = self._raw_model
        _selection_model = self.selectionModel()
        _selection_model.select(_index, QtCore.QItemSelectionModel.Select)
        self.setCurrentIndex(_index)
        self.scrollTo(_index)

# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
Module with the DirectoryExplorer widget which is an implementation of a
QTreeView with a file system model.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DirectoryExplorer"]


import os
import platform
from typing import Self, Union

from qtpy import QtCore, QtWidgets

from ...core import PydidasQsettings, PydidasQsettingsMixin
from ...core.constants import POLICY_EXP_EXP
from ...core.utils import apply_qt_properties
from ..factory import CreateWidgetsMixIn, EmptyWidget


class DirectoryExplorer(EmptyWidget, CreateWidgetsMixIn, PydidasQsettingsMixin):
    """
    The DirectoryExplorer is an implementation of a QTreeView widget with a
    file system model to display the contents of directories.

    Parameters
    ----------
    parent : Union[QWidget, None], optional
        The parent widget, if appplicable. The default is None.
    current_path : str, optional
        The default path in the file system. The default is ''.
    **kwargs : dict
        Any additional keyword arguments
    """

    sig_new_file_selected = QtCore.Signal(str)

    def __init__(self, parent=None, **kwargs) -> Self:
        EmptyWidget.__init__(self, parent=parent, **kwargs)
        CreateWidgetsMixIn.__init__(self)
        PydidasQsettingsMixin.__init__(self)
        self._create_widgets()
        self._set_up_filemodel(**kwargs)
        self._widgets["explorer"].clicked.connect(self.__file_highlighted)
        self._widgets["explorer"].doubleClicked.connect(self.__file_selected)
        self._widgets["map_network_drives"].stateChanged.connect(
            self.__update_filesystem_network_drive_usage
        )

    def _create_widgets(self):
        """
        Create the widgets required for the Directory explorer.
        """
        self.create_check_box(
            "map_network_drives",
            "Show network drives",
            checked=self.q_settings_get_value(
                "directory_explorer/show_network_drives", dtype=bool, default=True
            ),
        )
        self.create_any_widget("explorer", _DirectoryExplorer)

    def _set_up_filemodel(self, **kwargs: dict):
        """
        Set up the file model for the QTreeView.

        Parameters
        ----------
        **kwargs : dict
            The calling kwargs.
        """
        _path = kwargs.get("current_path", None)
        if _path is None:
            _path = self.q_settings_get_value("directory_explorer/path", default="")
        self._file_model = QtWidgets.QFileSystemModel()
        self._file_model.setRootPath(_path)
        self._file_model.setReadOnly(True)
        self._filter_model = _NetworkLocationFilterModel()
        self._filter_model.setSourceModel(self._file_model)
        self._widgets["explorer"].setModel(self._filter_model)
        self._widgets["explorer"].expand_to_path(_path)

    def sizeHint(self) -> QtCore.QSize:
        """
        Overload the generic sizeHint.

        Returns
        -------
        QtCore.QSize
            The updated size hint.
        """
        return QtCore.QSize(400, 4000)

    @QtCore.Slot(bool)
    def __update_filesystem_network_drive_usage(self, state: QtCore.Qt.CheckState):
        """
        Update the filesystem model network drive usage.

        Parameters
        ----------
        state : QtCore.Qt.CheckState
            The checkbox's state.
        """
        _usage = state == QtCore.Qt.Checked.value
        self.q_settings_set_key("directory_explorer/show_network_drives", _usage)
        self._filter_model.toggle_network_location_acceptance(_usage)
        self._filter_model.sort(0, self._filter_model.sortOrder())

    @QtCore.Slot()
    def __file_highlighted(self):
        """
        Store the selected filename after highlighting,
        """
        _filter_index = self._widgets["explorer"].selectedIndexes()[0]
        _index = self._filter_model.mapToSource(_filter_index)
        _name = self._file_model.filePath(_index)
        if os.path.isfile(_name):
            _name = os.path.dirname(_name)
        self.q_settings_set_key("directory_explorer/path", _name)

    @QtCore.Slot()
    def __file_selected(self):
        """
        Open a file after sit has been selected in the DirectoryExplorer.
        """
        _filter_index = self._widgets["explorer"].selectedIndexes()[0]
        _index = self._filter_model.mapToSource(_filter_index)
        _name = self._file_model.filePath(_index)
        if os.path.isfile(_name):
            self.sig_new_file_selected.emit(_name)


class _DirectoryExplorer(QtWidgets.QTreeView):
    """
    The DirectoryExplorer is an implementation of a QTreeView widget with a
    file system model to display the contents of directories.

    Parameters
    ----------
    parent : Union[QWidget, None], optional
        The parent widget, if appplicable. The default is None.
    **kwargs : dict
        Any additional keyword arguments
    """

    def __init__(
        self,
        parent: Union[QtWidgets.QWidget, None] = None,
        **kwargs,
    ):
        QtWidgets.QTreeView.__init__(self, parent)
        apply_qt_properties(self, **kwargs)
        self.raw_model = None

    def setModel(self, model: QtCore.QAbstractItemModel):
        """
        Set the model of the directory explorer.

        Parameters
        ----------
        model : QtCore.QAbstractItemModel
            The model to be used.
        """
        if isinstance(model, QtCore.QSortFilterProxyModel):
            self.raw_model = model.sourceModel()
        else:
            self.raw_model = model
        QtWidgets.QTreeView.setModel(self, model)
        self.setAnimated(False)
        self.setIndentation(12)
        self.setSortingEnabled(True)
        self.setColumnWidth(0, 400)
        self.setColumnWidth(1, 70)
        self.setColumnWidth(2, 100)
        self.setColumnWidth(3, 140)
        self.setSizePolicy(*POLICY_EXP_EXP)
        self.sortByColumn(0, QtCore.Qt.SortOrder.AscendingOrder)

    def expand_to_path(self, path: str):
        """
        Expand the treeview to a given path.

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


class _NetworkLocationFilterModel(QtCore.QSortFilterProxyModel):
    """
    A proxy sort model which allows to hide network drives.
    """

    def __init__(self, parent=None):
        QtCore.QSortFilterProxyModel.__init__(self, parent)
        self.setRecursiveFilteringEnabled(True)
        self.__accept_network_locations = PydidasQsettings().q_settings_get_value(
            "directory_explorer/show_network_drives", dtype=bool, default=True
        )
        __storage = QtCore.QStorageInfo()
        if platform.system() == "Windows":
            __prefix = "\\\\?\\Volume"
        elif platform.system() == "Unix":
            __prefix = "/dev/"
        else:
            raise SystemError("Only windows and unix operating systems are supported!")
        self.__network_drives = [
            _vol.rootPath()
            for _vol in __storage.mountedVolumes()
            if not _vol.device().toStdString().startswith(__prefix)
        ]

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
        if self.__accept_network_locations:
            return True
        _index = self.sourceModel().index(source_row, 0, source_parent)
        while _index.parent().isValid():
            _index = _index.parent()
        return self.sourceModel().filePath(_index) not in self.__network_drives

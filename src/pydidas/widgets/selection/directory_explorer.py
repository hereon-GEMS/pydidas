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
Module with the DirectoryExplorer widget, which is an implementation of a
QTreeView with a file system model.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DirectoryExplorer"]


import os
from pathlib import Path
from typing import Any

import qtpy
from qtpy import QtCore, QtWidgets

from pydidas.core import (
    get_generic_parameter,
)
from pydidas.widgets.selection.directory_explorer_filter_model import (
    DirectoryExplorerFilterModel,
)
from pydidas.widgets.selection.directory_explorer_tree_view import (
    DirectoryExplorerTreeView,
)
from pydidas.widgets.widget_with_parameter_collection import (
    WidgetWithParameterCollection,
)


AscendingOrder = QtCore.Qt.AscendingOrder
QSortFilterProxyModel = QtCore.QSortFilterProxyModel


class DirectoryExplorer(WidgetWithParameterCollection):
    """
    The DirectoryExplorer is an implementation of a QTreeView widget with a
    file system model to display the contents of directories.

    Parameters
    ----------
    **kwargs : Any
        Supported keywords are any keywords that are supported by QTreeView
        as well as:

        parent : Union[QWidget, None], optional
            The parent widget, if applicable. The default is None.
        current_path : str, optional
            The default path in the file system. The default is ''.
    """

    sig_new_file_selected = QtCore.Signal(str)

    def __init__(self, **kwargs: Any):
        WidgetWithParameterCollection.__init__(self, **kwargs)
        self.add_param(get_generic_parameter("current_directory"))
        self._create_widgets()
        self._set_up_file_model(**kwargs)
        self._connect_signals()

    def _create_widgets(self):
        """
        Create the widgets required for the Directory explorer.
        """
        self.create_check_box(
            "map_network_drives",
            "Show network drives",
            checked=self.q_settings_get(
                "directory_explorer/show_network_drives", dtype=bool, default=True
            ),
        )
        self.create_check_box(
            "case_sensitive",
            "Sorting is case sensitive",
            checked=self.q_settings_get(
                "directory_explorer/is_case_sensitive", dtype=bool, default=True
            ),
        )
        self.create_param_widget(
            self.params["current_directory"], linebreak=True, hide_button=True
        )
        self.param_composite_widgets["current_directory"]._widgets[
            "io"
        ]._button.setVisible(False)
        self.create_empty_widget("option_container")
        self.create_lineedit(
            "filter_edit",
            font_metric_width_factor=24,
            parent_widget="option_container",
            placeholderText="Filename filter...",
        )
        self.create_button(
            "button_reset_filter",
            "Reset filter",
            font_metric_width_factor=16,
            gridPos=(0, -1, 1, 1),
            parent_widget="option_container",
        )
        self.create_spacer(
            None, parent_widget="option_container", gridPos=(0, -1, 1, 1)
        )
        self.create_button(
            "button_collapse",
            "Collapse all",
            font_metric_width_factor=16,
            gridPos=(0, -1, 1, 1),
            parent_widget="option_container",
        )
        self._widgets["option_container"].layout().setColumnStretch(2, 1)
        self.create_any_widget("explorer", DirectoryExplorerTreeView)

    def _set_up_file_model(self, **kwargs: Any):
        """
        Set up the file model for the QTreeView.

        Parameters
        ----------
        **kwargs : Any
            The calling kwargs.
        """
        _path = kwargs.get("current_path", None)
        if _path is None:
            _path = self.q_settings_get("directory_explorer/path", default="")
        self.set_param_value_and_widget("current_directory", _path)
        self._file_model = QtWidgets.QFileSystemModel()
        self._file_model.setRootPath(_path)
        self._file_model.setReadOnly(True)
        self._filter_model = DirectoryExplorerFilterModel()
        self._filter_model.setSourceModel(self._file_model)
        self._widgets["explorer"].setModel(self._filter_model)
        self._widgets["explorer"].expand_to_path(_path)

    def _connect_signals(self):
        """Connect the signals of the widgets to the slots."""
        self._widgets["explorer"].clicked.connect(self.__file_highlighted)
        self._widgets["explorer"].doubleClicked.connect(self.__file_selected)
        self._widgets["map_network_drives"].stateChanged.connect(
            self.__update_filesystem_network_drive_usage
        )
        self._widgets["case_sensitive"].stateChanged.connect(
            self.__update_filter_case_sensitivity
        )
        self.param_widgets["current_directory"].io_edited.connect(self.__user_dir_input)
        self._widgets["button_collapse"].clicked.connect(self.__collapse_all)
        self._widgets["button_reset_filter"].clicked.connect(self.__reset_filter)
        self._widgets["filter_edit"].textChanged.connect(
            self._filter_model.toggle_filter_string
        )

    def sizeHint(self) -> QtCore.QSize:
        """
        Overload the generic sizeHint.

        Returns
        -------
        QtCore.QSize
            The updated size hint.
        """
        return QtCore.QSize(400, 4000)

    @QtCore.Slot(int)
    def __update_filesystem_network_drive_usage(self, state: QtCore.Qt.CheckState):
        """
        Update the filesystem model network drive usage.

        Parameters
        ----------
        state : QtCore.Qt.CheckState
            The checkbox's state.
        """
        if qtpy.QT_VERSION.startswith("6"):
            _usage = state == QtCore.Qt.Checked.value
        else:
            _usage = state == QtCore.Qt.Checked
        self.q_settings_set("directory_explorer/show_network_drives", _usage)
        self._filter_model.toggle_network_location_acceptance(_usage)
        self._filter_model.sort(0, self._filter_model.sortOrder())

    @QtCore.Slot(int)
    def __update_filter_case_sensitivity(self, state: QtCore.Qt.CheckState):
        """
        Update the filter's case sensitivity.

        Parameters
        ----------
        state : QtCore.Qt.CheckState
            The checkbox's state.
        """
        if qtpy.QT_VERSION.startswith("6"):
            _usage = state == QtCore.Qt.Checked.value
        else:
            _usage = state == QtCore.Qt.Checked
        self.q_settings_set("directory_explorer/is_case_sensitive", _usage)
        self._filter_model.setSortCaseSensitivity(
            QtCore.Qt.CaseSensitive if _usage else QtCore.Qt.CaseInsensitive
        )
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
        self.q_settings_set("directory_explorer/path", _name)

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
        elif os.path.isdir(_name):
            self.set_param_value_and_widget("current_directory", _name)

    @QtCore.Slot(str)
    def __user_dir_input(self, path: str):
        """
        Process the user file / directory input.

        Parameters
        ----------
        path : str
            The file or directory to be set as active.
        """
        self._file_model.setRootPath(path)
        self._widgets["explorer"].expand_to_path(path)
        _proxy_index = self._filter_model.mapFromSource(self._file_model.index(path))
        self._widgets["explorer"].selectionModel().select(
            _proxy_index, QtCore.QItemSelectionModel.Select
        )
        self._widgets["explorer"].scrollToBottom()
        self._widgets["explorer"].setCurrentIndex(_proxy_index)
        _path = Path(path)
        if _path.is_file():
            with QtCore.QSignalBlocker(self.param_widgets["current_directory"]):
                self.set_param_value_and_widget("current_directory", _path.parent)
            self.sig_new_file_selected.emit(path)

    @QtCore.Slot()
    def __collapse_all(self):
        """Collapse all directories in the explorer."""
        for row in range(self._filter_model.rowCount()):
            index = self._filter_model.index(row, 0)
            self._widgets["explorer"].collapse(index)

    @QtCore.Slot()
    def __reset_filter(self):
        """Reset the filter to show all files."""
        self._widgets["filter_edit"].setText("")

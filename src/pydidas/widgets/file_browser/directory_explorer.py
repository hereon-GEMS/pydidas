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
Module with the DirectoryExplorer widget, which is an implementation of a
QTreeView with a file system model.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DirectoryExplorer"]


import os
from pathlib import Path
from typing import Any

from qtpy import QtCore, QtWidgets

from pydidas.widgets.file_browser._directory_explorer_config import (
    DIRECTORY_EXPLORER_DEFAULT_PARAMS,
    DIRECTORY_EXPLORER_WIDGET_BUILD_CONFIG,
)
from pydidas.widgets.selection.directory_explorer_filter_model import (
    DirectoryExplorerFilterModel,
)
from pydidas.widgets.widget_with_parameter_collection import (
    WidgetWithParameterCollection,
)


class DirectoryExplorer(WidgetWithParameterCollection):
    """
    The DirectoryExplorer is an implementation of a QTreeView widget with a
    file system model to display the contents of directories.

    Parameters
    ----------
    **kwargs : Any
        Supported keywords are any keywords that are supported by QTreeView
        as well as:

        parent : QtWidgets.QWidget or None, optional
            The parent widget, if applicable. The default is None.
        current_path : str, optional
            The default path in the file system. The default is ''.
    """

    sig_new_file_selected = QtCore.Signal(str)
    default_params = DIRECTORY_EXPLORER_DEFAULT_PARAMS

    def __init__(self, **kwargs: Any) -> None:
        WidgetWithParameterCollection.__init__(self, **kwargs)
        self.set_default_params()
        self._create_widgets()
        self._set_up_file_model(**kwargs)
        self._connect_signals()
        self._finalize_ui()

    def _create_widgets(self) -> None:
        """Create the widgets required for the Directory explorer."""
        for _method, _args, _kwargs in DIRECTORY_EXPLORER_WIDGET_BUILD_CONFIG:
            getattr(self, _method)(*_args, **_kwargs)

        self.param_composite_widgets["current_directory"]._widgets[
            "io"
        ]._button.setVisible(False)  # type: ignore[attr-defined]
        self._widgets["filter_container"].layout().setColumnStretch(2, 1)

    def _set_up_file_model(self, **kwargs: Any) -> None:
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
        _path = str(_path)
        self.set_param_and_widget_value("current_directory", _path)
        self._file_model = QtWidgets.QFileSystemModel()
        if hasattr(self._file_model, "DontUseCustomDirectoryIcons"):
            self._file_model.setOption(
                self._file_model.DontUseCustomDirectoryIcons, True
            )
        self._file_model.setReadOnly(True)
        self._file_model.setRootPath(_path)
        self._filter_model = DirectoryExplorerFilterModel()
        self._filter_model.setSourceModel(self._file_model)  # type: ignore[arg-type]
        self._widgets["explorer"].setModel(self._filter_model)
        self._widgets["explorer"].expand_to_path(_path)

    def _connect_signals(self) -> None:
        """Connect the signals of the widgets to the slots."""
        self._widgets["explorer"].clicked.connect(self.__file_highlighted)
        self._widgets["explorer"].doubleClicked.connect(self.__file_selected)
        self.param_composite_widgets["map_network_drives"].sig_new_value.connect(
            self.__update_filesystem_network_drive_usage
        )
        self.param_composite_widgets["case_sensitive"].sig_new_value.connect(
            self.__update_filter_case_sensitivity
        )
        self.param_widgets["current_directory"].sig_new_value.connect(
            self.__user_dir_input
        )
        self._widgets["button_collapse"].clicked.connect(self.__collapse_all)
        self._widgets["button_reset_filter"].clicked.connect(self.__reset_filter)
        # Signals for file browser root handling
        self._widgets["button_apply_roots"].clicked.connect(self._apply_new_roots)
        self.param_composite_widgets["use_custom_roots"].sig_new_value.connect(
            self.__toggle_root_widget_visibility
        )

    def _finalize_ui(self) -> None:
        """Finalize the widget initalization."""
        self.check_root_up_to_date()

        # Set up the filter to only accept the final entry after the used
        # did not change the edit for 500 ms to prevent multiple calls during
        # editing
        self.__pending_filter_text = ""
        self.__filter_timer = QtCore.QTimer(self)
        self.__filter_timer.setSingleShot(True)
        self.__filter_timer.setInterval(500)
        self.__filter_timer.timeout.connect(self.__apply_filter_string)
        self._widgets["filter_edit"].textChanged.connect(self.__queue_filter_update)

    def check_root_up_to_date(self) -> None:
        """Check if the root of the directory is up to date."""
        _roots = self.q_settings_get("user/data_browsing_root", dtype=str)
        if _roots != self.get_param_value("data_browsing_root"):
            self.set_param_and_widget_value("data_browsing_root", _roots)
            self._apply_new_roots()
        self.set_param_and_widget_value("use_custom_roots", _roots != "")

    @QtCore.Slot()
    def _apply_new_roots(self) -> None:
        """Update the roots of the DataBrowsingFrame"""
        self.q_settings_set(
            "user/data_browsing_root", self.get_param_value("data_browsing_root")
        )
        print(
            "Updating data browsing roots...",
            self.get_param_value("data_browsing_root"),
        )

    @QtCore.Slot(str)
    def __queue_filter_update(self, filter_text: str) -> None:
        """Queue a debounced update of the filename filter."""
        self.__pending_filter_text = filter_text
        self.__filter_timer.start()

    @QtCore.Slot()
    def __apply_filter_string(self) -> None:
        """Apply the filename filter to the filter model."""
        self._filter_model.toggle_filter_string(self.__pending_filter_text)

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
    def __update_filesystem_network_drive_usage(self, value_repr: str) -> None:
        """
        Update the filesystem model network drive usage.

        Parameters
        ----------
        value_repr : str
            The string representation of the checkbox's state
            (as defined in QtCore.Qt.CheckState).
        """
        _usage = value_repr == "True"
        self.q_settings_set("directory_explorer/show_network_drives", _usage)
        self._filter_model.toggle_network_location_acceptance(_usage)
        self._filter_model.sort(0, self._filter_model.sortOrder())

    @QtCore.Slot(str)
    def __update_filter_case_sensitivity(self, value_repr: str) -> None:
        """
        Update the filter's case sensitivity.

        Parameters
        ----------
        value_repr : str
            The string representation of the checkbox's state
            (as defined in QtCore.Qt.CheckState).
        """
        _usage = value_repr == "True"
        self.q_settings_set("directory_explorer/is_case_sensitive", _usage)
        self._filter_model.setSortCaseSensitivity(
            QtCore.Qt.CaseSensitive if _usage else QtCore.Qt.CaseInsensitive  # type: ignore[arg-type]
        )
        self._filter_model.sort(0, self._filter_model.sortOrder())

    @QtCore.Slot()
    def __file_highlighted(self) -> None:
        """Store the selected filename after highlighting."""
        _filter_index = self._widgets["explorer"].selectedIndexes()[0]
        _index = self._filter_model.mapToSource(_filter_index)
        _name = self._file_model.filePath(_index)
        if Path(_name).is_file():
            _name = Path(_name).parent
        self.q_settings_set("directory_explorer/path", str(_name))

    @QtCore.Slot()
    def __file_selected(self) -> None:
        """Open a file after it has been selected in the DirectoryExplorer."""
        _filter_index = self._widgets["explorer"].selectedIndexes()[0]
        _index = self._filter_model.mapToSource(_filter_index)
        _name = self._file_model.filePath(_index)
        if Path(_name).is_file():
            self.sig_new_file_selected.emit(_name)  # type: ignore[attr-defined]
        elif Path(_name).is_dir():
            self.set_param_and_widget_value("current_directory", _name)
        _row_cache = getattr(
            self._filter_model,
            "_DirectoryExplorerFilterModel__file_info_cache",
            {},
        )
        _root_cache = getattr(
            self._filter_model,
            "_DirectoryExplorerFilterModel__top_root_cache",
            {},
        )
        print("row cache: ", len(_row_cache))
        print("root cache", len(_root_cache))

    @QtCore.Slot(str)
    def __user_dir_input(self, path: str) -> None:
        """
        Process the user file / directory input.

        Parameters
        ----------
        path : str
            The file or directory to be set as active.
        """
        _target_dir = str(Path(path).parent if Path(path).is_file() else Path(path))
        _norm_target = os.path.normcase(os.path.normpath(_target_dir))

        # Only suspend filtering/sorting when the directory is not yet loaded.
        # For already-cached directories, directoryLoaded may not fire again,
        # and with no active filter the suspension is unnecessary anyway.
        _target_index = self._file_model.index(_target_dir)
        _already_loaded = (
            _target_index.isValid() and self._file_model.rowCount(_target_index) > 0
        )

        if not _already_loaded:
            _explorer = self._widgets["explorer"]
            _sort_col = _explorer.header().sortIndicatorSection()
            _sort_order = _explorer.header().sortIndicatorOrder()

            # Safety timer ensures resume always fires even if directoryLoaded
            # does not emit (already cached, permission errors, etc.).
            _safety_timer = QtCore.QTimer(self)
            _safety_timer.setSingleShot(True)
            _safety_timer.setInterval(5000)  # 5 s hard cap

            def _resume() -> None:
                self._filter_model.resume_filtering()
                _explorer.setSortingEnabled(True)
                _explorer.sortByColumn(_sort_col, _sort_order)

            def _on_loaded(loaded_path: str) -> None:
                if os.path.normcase(os.path.normpath(loaded_path)) == _norm_target:
                    _safety_timer.stop()
                    _resume()
                    try:
                        self._file_model.directoryLoaded.disconnect(_on_loaded)
                    except RuntimeError:
                        pass

            def _on_timeout() -> None:
                try:
                    self._file_model.directoryLoaded.disconnect(_on_loaded)
                except RuntimeError:
                    pass
                _resume()

            # Suspend both filtering and sorting so new rows arrive without
            # triggering O(n log n) re-sort over all accumulated rows.
            self._filter_model.suspend_filtering()
            _explorer.setSortingEnabled(False)
            self._file_model.directoryLoaded.connect(_on_loaded)
            _safety_timer.timeout.connect(_on_timeout)
            _safety_timer.start()

        self._file_model.setRootPath(path)
        self._widgets["explorer"].expand_to_path(path)
        _proxy_index = self._filter_model.mapFromSource(self._file_model.index(path))
        self._widgets["explorer"].selectionModel().select(
            _proxy_index, QtCore.QItemSelectionModel.Select
        )
        self._widgets["explorer"].scrollTo(_proxy_index)
        self._widgets["explorer"].setCurrentIndex(_proxy_index)
        _path = Path(path)
        if _path.is_file():
            with QtCore.QSignalBlocker(self.param_widgets["current_directory"]):
                self.set_param_and_widget_value("current_directory", _path.parent)
            self.sig_new_file_selected.emit(path)  # type: ignore[attr-defined]

    @QtCore.Slot()
    def __collapse_all(self) -> None:
        """Collapse all directories in the explorer."""
        for row in range(self._filter_model.rowCount()):
            index = self._filter_model.index(row, 0)
            self._widgets["explorer"].collapse(index)

    @QtCore.Slot()
    def __reset_filter(self) -> None:
        """Reset the filter to show all files."""
        self._widgets["filter_edit"].setText("")

    @QtCore.Slot(str)
    def __toggle_root_widget_visibility(self, vis_repr: str) -> None:
        """
        Toggle the visibility of the data browsing root widgets.

        Parameters
        ----------
        vis_repr : str
            The string representation of the bool visibility.
        """
        _vis = vis_repr == "True"
        self.toggle_param_widget_visibility("data_browsing_root", _vis)
        for _name in ["button_apply_roots", "button_reset_roots"]:
            self._widgets[_name].setVisible(_vis)

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


from pathlib import Path
from typing import Any

from qtpy import QtCore, QtWidgets

from pydidas.core import UserConfigError
from pydidas.core.utils import get_directory, get_single_shot_timer
from pydidas.widgets.file_browser._directory_explorer_config import (
    DIRECTORY_EXPLORER_DEFAULT_PARAMS,
    DIRECTORY_EXPLORER_WIDGET_BUILD_CONFIG,
)
from pydidas.widgets.file_browser.directory_explorer_filter_model import (
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
            Initial file system path. If omitted, the value is read from
            settings and falls back to ''.
    """

    sig_new_file_selected = QtCore.Signal(str)
    default_params = DIRECTORY_EXPLORER_DEFAULT_PARAMS

    def __init__(self, **kwargs: Any) -> None:
        WidgetWithParameterCollection.__init__(self, **kwargs)
        self.set_default_params()
        self._create_widgets()
        self._set_up_file_model(**kwargs)
        self._set_up_filter()
        self._connect_signals()
        self._widgets["tree_view"].expand_to_path(self._file_model.rootPath())
        self.check_root_up_to_date()

    # +-------------------------+
    # | initialization methods  |
    # +-------------------------+

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
            Optional setup kwargs. Supported key: ``current_path``.
        """
        _path = kwargs.get("current_path", None)
        if _path is None:
            _path = self.q_settings_get("directory_explorer/path", default="")
        self.set_param_and_widget_value("current_directory", _path)
        _path = str(_path)
        self._file_model = QtWidgets.QFileSystemModel()
        if hasattr(self._file_model, "DontUseCustomDirectoryIcons"):
            self._file_model.setOption(
                self._file_model.DontUseCustomDirectoryIcons, True
            )
        self._file_model.setReadOnly(True)
        self._file_model.setRootPath(_path)

    def _set_up_filter(self) -> None:
        """
        Set up the filter.

        The filter is set up to only accept the final entry after the user
        did not change the edit for 500 ms to prevent multiple calls during
        editing.
        """
        self._filter_model = DirectoryExplorerFilterModel()
        self._filter_model.setSourceModel(self._file_model)  # type: ignore[arg-type]
        self._widgets["tree_view"].setModel(self._filter_model)
        self.__pending_filter_text = ""
        self.__filter_timer = QtCore.QTimer(self)
        self.__filter_timer.setSingleShot(True)
        self.__filter_timer.setInterval(500)

    def _connect_signals(self) -> None:
        """Connect the signals of the widgets to the slots."""
        self._widgets["tree_view"].clicked.connect(self._file_highlighted)
        self._widgets["tree_view"].doubleClicked.connect(self._item_selected)
        self.param_composite_widgets["map_network_drives"].sig_new_value.connect(
            self._update_filesystem_network_drive_usage
        )
        self.param_composite_widgets["case_sensitive"].sig_new_value.connect(
            self._update_filter_case_sensitivity
        )
        self.param_composite_widgets["current_directory"].sig_new_value.connect(
            self._user_dir_selection
        )
        self._widgets["button_collapse"].clicked.connect(self._collapse_all)
        self._widgets["button_reset_filter"].clicked.connect(self._reset_filter)
        # Signals for file browser root handling
        self._widgets["button_apply_root"].clicked.connect(self._apply_new_root)
        self._widgets["button_reset_root"].clicked.connect(self._reset_root)
        self.param_composite_widgets["use_custom_root"].sig_new_value.connect(
            self._toggle_custom_root_usage
        )
        # Filter signals:
        self.__filter_timer.timeout.connect(self._apply_filter_string)
        self._widgets["filter_edit"].textChanged.connect(self._queue_filter_update)

    # +-----------------------------------+
    # | public API methods and properties |
    # +-----------------------------------+

    @property
    def selected_item(self) -> Path | None:
        """
        Get the selected item (i.e. the file or directory)

        Returns
        -------
        Path or None
            The currently selected file or directory in the DirectoryExplorer
            or None if no item is selected.
        """
        _filter_index = self._widgets["tree_view"].selectedIndexes()
        if len(_filter_index) == 0:
            return None
        _filter_index = _filter_index[0]
        _index = self._filter_model.mapToSource(_filter_index)
        _name = self._file_model.filePath(_index)
        return Path(_name)

    def check_root_up_to_date(self) -> None:
        """Check if the root of the directory is up to date."""
        _root = self.q_settings_get("user/data_browsing_root", dtype=str)
        _custom_root = self.q_settings_get(
            "directory_explorer/use_custom_root", dtype=bool, default=False
        )
        self.set_param_and_widget_value("use_custom_root", _custom_root)
        if _custom_root and _root != self.get_param_value("data_browsing_root"):
            self.set_param_and_widget_value("data_browsing_root", _root)
            self._apply_new_root()

    # +---------------------------+
    # | re-implemented Qt methods |
    # +---------------------------+

    def sizeHint(self) -> QtCore.QSize:
        """
        Overload the generic sizeHint.

        Returns
        -------
        QtCore.QSize
            The updated size hint.
        """
        return QtCore.QSize(400, 4000)

    # +----------------------+
    # | private Slot methods |
    # +----------------------+

    @QtCore.Slot()
    def _apply_new_root(self) -> None:
        """Update the root of the DirectoryExplorer."""
        if not self.get_param_value("use_custom_root"):
            _root_dir = Path()
        else:
            _root_dir = get_directory(self.get_param_value("data_browsing_root"))
            if not _root_dir.is_dir():
                self._widgets["tree_view"].setRootIndex(QtCore.QModelIndex())

                raise UserConfigError(
                    "Warning: The given directory does not exist and the entry has "
                    "been ignored and reset to the file system root."
                )
        if _root_dir == Path():
            self.q_settings_set("user/data_browsing_root", "")
            self._widgets["tree_view"].setRootIndex(QtCore.QModelIndex())
            return
        self.q_settings_set("user/data_browsing_root", str(_root_dir))
        _index = self._filter_model.mapFromSource(
            self._file_model.index(str(_root_dir))
        )
        if not _index.isValid():
            _index = QtCore.QModelIndex()
            _root_dir = Path()
        self._widgets["tree_view"].setRootIndex(_index)
        _current_dir = get_directory(self.get_param_value("current_directory"))
        if _root_dir not in _current_dir.parents:
            with QtCore.QSignalBlocker(self.param_widgets["current_directory"]):
                self.set_param_and_widget_value("current_directory", _root_dir)

    @QtCore.Slot()
    def _reset_root(self) -> None:
        """Reset the user root to the default (empty) value."""
        self.set_param_and_widget_value("data_browsing_root", "")
        self._apply_new_root()

    @QtCore.Slot(str)
    def _queue_filter_update(self, filter_text: str) -> None:
        """
        Queue a debounced update of the filename filter.

        Parameters
        ----------
        filter_text : str
            The new filter text to be applied after the debounce interval.
        """
        self.__pending_filter_text = filter_text
        self.__filter_timer.start()

    @QtCore.Slot()
    def _apply_filter_string(self) -> None:
        """Apply the filename filter to the filter model."""
        self._filter_model.change_filter_string(self.__pending_filter_text)

    @QtCore.Slot(str)
    def _update_filesystem_network_drive_usage(self, value_repr: str) -> None:
        """
        Update the filesystem model network drive usage.

        Parameters
        ----------
        value_repr : str
            The string representation of the checkbox's state.
        """
        _usage = value_repr == "True"
        self.q_settings_set("directory_explorer/show_network_drives", _usage)
        self._filter_model.show_network_drives(_usage)
        self._filter_model.sort(0, self._filter_model.sortOrder())

    @QtCore.Slot(str)
    def _update_filter_case_sensitivity(self, value_repr: str) -> None:
        """
        Update the filter's case sensitivity.

        Parameters
        ----------
        value_repr : str
            The string representation of the checkbox's state.
        """
        _usage = value_repr == "True"
        self.q_settings_set("directory_explorer/is_case_sensitive", _usage)
        _sensitivity = QtCore.Qt.CaseSensitive if _usage else QtCore.Qt.CaseInsensitive
        self._filter_model.setSortCaseSensitivity(
            _sensitivity  # type: ignore[arg-type]
        )
        self._filter_model.sort(0, self._filter_model.sortOrder())

    @QtCore.Slot()
    def _file_highlighted(self) -> None:
        """Store the selected filename after highlighting."""
        _dir = get_directory(self.selected_item)
        self.q_settings_set("directory_explorer/path", str(_dir))

    @QtCore.Slot()
    def _item_selected(self) -> None:
        """Open a file/dir after it has been selected in the DirectoryExplorer."""
        _item = self.selected_item
        _dir = get_directory(_item)
        self.set_param_and_widget_value(
            "current_directory", _dir, emit_signal=_item == _dir
        )
        if _item.is_file():
            self.sig_new_file_selected.emit(str(_item))  # type: ignore[attr-defined]

    @QtCore.Slot(str)
    def _user_dir_selection(self, name: str) -> None:
        """
        Process the user's selection of a file / directory to display.

        Parameters
        ----------
        name : str
            The file or directory name to be set as active.
        """
        _target_dir = get_directory(name).resolve()
        if self.get_param_value("use_custom_root"):
            _root_dir = Path(self.get_param_value("data_browsing_root"))
            if _root_dir not in _target_dir.parents and _target_dir != _root_dir:
                raise UserConfigError(
                    f"The selected directory\n    {_target_dir}\nis not included "
                    f"in the custom browsing root\n    {_root_dir}\nand cannot be "
                    "selected or displayed. Request ignored."
                )
        # Only suspend filtering/sorting when the directory is not yet loaded.
        # For already-cached directories, directoryLoaded may not fire again,
        # and with no active filter the suspension is unnecessary anyway.
        _target_index = self._file_model.index(str(_target_dir))
        _already_loaded = (
            _target_index.isValid() and self._file_model.rowCount(_target_index) > 0
        )
        if not _already_loaded:
            self.__prepare_directory_loading(_target_dir)

        self._file_model.setRootPath(name)
        self._widgets["tree_view"].expand_to_path(name)
        _proxy_index = self._filter_model.mapFromSource(self._file_model.index(name))
        self._widgets["tree_view"].selectionModel().select(
            _proxy_index, QtCore.QItemSelectionModel.Select
        )
        self._widgets["tree_view"].scrollTo(_proxy_index)
        self._widgets["tree_view"].setCurrentIndex(_proxy_index)
        _path = Path(name)
        if _path.is_file():
            with QtCore.QSignalBlocker(self.param_widgets["current_directory"]):
                self.set_param_and_widget_value("current_directory", _path.parent)
            self.sig_new_file_selected.emit(name)  # type: ignore[attr-defined]

    @QtCore.Slot()
    def _collapse_all(self) -> None:
        """Collapse all directories in the explorer."""
        self._widgets["tree_view"].collapseAll()

    @QtCore.Slot()
    def _reset_filter(self) -> None:
        """Reset the filter to show all files."""
        self._widgets["filter_edit"].setText("")

    @QtCore.Slot(str)
    def _toggle_custom_root_usage(self, vis_repr: str) -> None:
        """
        Toggle the visibility of the data browsing root widgets.

        Parameters
        ----------
        vis_repr : str
            The string representation of the bool visibility.
        """
        _vis = vis_repr == "True"
        self.toggle_param_widget_visibility("data_browsing_root", _vis)
        self.q_settings_set("directory_explorer/use_custom_root", _vis)
        for _name in ["button_apply_root", "button_reset_root"]:
            self._widgets[_name].setVisible(_vis)
        self._apply_new_root()

    # +---------------------------+
    # | private helper methods    |
    # +---------------------------+

    def __prepare_directory_loading(self, target_dir: Path) -> None:
        """
        Prepare directory loading while filtering and sorting are suspended.

        Parameters
        ----------
        target_dir : Path
            The selected directory.
        """
        _explorer = self._widgets["tree_view"]
        _sort_col = _explorer.header().sortIndicatorSection()
        _sort_order = _explorer.header().sortIndicatorOrder()

        # Safety timer ensures resume always fires even if directoryLoaded
        # does not emit (e.g. because it is already cached):
        _safety_timer = get_single_shot_timer(self, timeout=5000)

        def _resume() -> None:
            self._filter_model.resume_filtering()
            _explorer.setSortingEnabled(True)
            _explorer.sortByColumn(_sort_col, _sort_order)

        def _on_loaded(loaded_path: str) -> None:
            _loaded_dir = get_directory(loaded_path).resolve()
            if _loaded_dir == target_dir:
                _safety_timer.stop()
                _finalize()

        def _finalize() -> None:
            try:
                self._file_model.directoryLoaded.disconnect(_on_loaded)
            except RuntimeError:
                pass
            _resume()

        # Suspend both filtering and sorting so new rows arrive without
        # triggering re-sort over all accumulated rows.
        self._filter_model.suspend_filtering()
        _explorer.setSortingEnabled(False)
        self._file_model.directoryLoaded.connect(_on_loaded)
        _safety_timer.timeout.connect(_finalize)
        _safety_timer.start()

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

from pydidas.core import (
    Parameter,
    ParameterCollection,
    get_generic_parameter,
)
from pydidas.core.constants import (
    FONT_METRIC_CONSOLE_WIDTH,
    FONT_METRIC_HALF_CONSOLE_WIDTH,
    FONT_METRIC_WIDE_BUTTON_WIDTH,
)
from pydidas.widgets.selection.directory_explorer_filter_model import (
    DirectoryExplorerFilterModel,
)
from pydidas.widgets.selection.directory_explorer_tree_view import (
    DirectoryExplorerTreeView,
)
from pydidas.widgets.selection.toggle_options_button import ToggleOptionsButton
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
    default_params = ParameterCollection(
        get_generic_parameter("current_directory"),
        get_generic_parameter("data_browsing_root"),
        Parameter(
            "map_network_drives", bool, 1, name="Show network drives", choices=[0, 1]
        ),
        Parameter(
            "case_sensitive", bool, 1, name="Sorting is case sensitive", choices=[0, 1]
        ),
        Parameter(
            "use_custom_roots",
            bool,
            0,
            name="Use custom broowsing roots",
            choices=[0, 1],
        ),
    )

    def __init__(self, **kwargs: Any) -> None:
        WidgetWithParameterCollection.__init__(self, **kwargs)
        self.set_default_params()
        self.__pending_filter_text = ""
        self.__filter_timer = QtCore.QTimer(self)
        self.__filter_timer.setSingleShot(True)
        self.__filter_timer.setInterval(150)
        self.__filter_timer.timeout.connect(self.__apply_filter_string)
        self._create_widgets()
        self._set_up_file_model(**kwargs)
        self._connect_signals()

    def _create_widgets(self) -> None:
        """Create the widgets required for the Directory explorer."""
        self.create_empty_widget(
            "header_container",
            font_metric_width_factor=FONT_METRIC_CONSOLE_WIDTH,
        )
        self.create_empty_widget(
            "option_container",
            font_metric_width_factor=FONT_METRIC_CONSOLE_WIDTH,
        )
        self.create_label(
            "label_option_header",
            "Data browsing options",
            bold=True,
            font_metric_width_factor=FONT_METRIC_HALF_CONSOLE_WIDTH,
            fontsize_offset=1,
            parent_widget="header_container",
        )
        self.create_any_widget(
            "button_toggle_options",
            ToggleOptionsButton,
            gridPos=(0, 2, 1, 1),
            font_metric_width_factor=FONT_METRIC_HALF_CONSOLE_WIDTH,
            linked_widget="option_container",
            linked_widget_visible=True,
            parent_widget="header_container",
            toggle_text_shown="Hide browsing options",
            toggle_text_hidden="Show browsing options",
        )
        self.create_param_widget(
            "map_network_drives",
            font_metric_width_factor=FONT_METRIC_HALF_CONSOLE_WIDTH,
            gridPos=(0, 0, 1, 1),
            parent_widget="option_container",
        )
        self.create_param_widget(
            "case_sensitive",
            font_metric_width_factor=FONT_METRIC_HALF_CONSOLE_WIDTH,
            gridPos=(0, 1, 1, 1),
            parent_widget="option_container",
        )
        self.create_param_widget(
            "use_custom_roots",
            font_metric_width_factor=FONT_METRIC_CONSOLE_WIDTH,
            gridPos=(-1, 0, 1, 2),
            parent_widget="option_container",
        )
        self.create_param_widget(
            "data_browsing_root",
            font_metric_width_factor=FONT_METRIC_CONSOLE_WIDTH,
            gridPos=(-1, 0, 1, 2),
            linebreak=True,
            parent_widget="option_container",
        )
        self.create_button(
            "button_apply_roots",
            "Apply new roots",
            icon="qt-std::SP_DialogApplyButton",
            font_metric_width_factor=FONT_METRIC_HALF_CONSOLE_WIDTH,
            parent_widget="option_container",
        )
        self.create_button(
            "button_reset_roots",
            "Clear root selection",
            icon="qt-std::SP_BrowserReload",
            font_metric_width_factor=FONT_METRIC_HALF_CONSOLE_WIDTH,
            parent_widget="option_container",
            gridPos=("::current::", 1, 1, 1),
        )
        self.create_param_widget(
            "current_directory",
            font_metric_width_factor=FONT_METRIC_CONSOLE_WIDTH,
            linebreak=True,
            parent_widget="option_container",
            gridPos=(-1, 0, 1, 2),
        )
        self.create_empty_widget(
            "filter_container",
            font_metric_width_factor=FONT_METRIC_CONSOLE_WIDTH,
        )
        self.create_lineedit(
            "filter_edit",
            font_metric_width_factor=FONT_METRIC_WIDE_BUTTON_WIDTH,
            parent_widget="filter_container",
            placeholderText="Filename filter...",
        )
        self.create_button(
            "button_reset_filter",
            "Reset filter",
            font_metric_width_factor=20,
            gridPos=(0, -1, 1, 1),
            parent_widget="filter_container",
        )
        self.create_spacer(
            None, parent_widget="filter_container", gridPos=(0, -1, 1, 1)
        )
        self.create_button(
            "button_collapse",
            "Collapse all",
            font_metric_width_factor=20,
            gridPos=(0, -1, 1, 1),
            parent_widget="filter_container",
        )
        self.param_composite_widgets["current_directory"]._widgets[
            "io"
        ]._button.setVisible(False)  # type: ignore[attr-defined]
        self.create_any_widget(
            "explorer", DirectoryExplorerTreeView, gridPos=(-1, 0, 1, 2)
        )
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
        self._widgets["filter_edit"].textChanged.connect(self.__queue_filter_update)
        # Signals for file browser root handling
        self._widgets["button_apply_roots"].clicked.connect(self._update_roots)

    def check_root_update(self) -> None:
        """Check if the root of the directory is up to date."""
        _roots = self.q_settings_get("user/data_browsing_root", dtype=str)
        if _roots != self.get_param_value("data_browsing_root"):
            self.set_param_and_widget_value("data_browsing_root", _roots)
            self._update_roots()

    def _update_roots(self) -> None:
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
        """Apply the pending filename filter after debounce timeout."""
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
        print(
            "row cache: ",
            len(self._filter_model._DirectoryExplorerFilterModel__file_info_cache),
        )
        print(
            "root cache",
            len(self._filter_model._DirectoryExplorerFilterModel__top_root_cache),
        )

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

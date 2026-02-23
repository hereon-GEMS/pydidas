# This file is part of pydidas.
#
# Copyright 2024 - 2026, Helmholtz-Zentrum Hereon
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
Module with PydidasFileDialog which is a persistent QFileDialog that allows keeping
persistent references to the selected directory.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasFileDialog"]


import os
from pathlib import Path
from typing import Any

from qtpy import QtCore, QtWidgets

from pydidas.contexts import ScanContext
from pydidas.core import (
    PydidasQsettingsMixin,
    SingletonObject,
    UserConfigError,
)
from pydidas.core.constants import FONT_METRIC_EXTRAWIDE_BUTTON_WIDTH
from pydidas.core.utils import update_child_qobject
from pydidas.core.utils.file_utils import get_extension
from pydidas.resources import icons
from pydidas.widgets.factory import CreateWidgetsMixIn
from pydidas_qtcore import PydidasQApplication


SCAN = ScanContext()
ITEM_SELECTABLE = QtCore.Qt.ItemIsSelectable
QStandardPaths = QtCore.QStandardPaths


class SelectionModel(QtCore.QIdentityProxyModel):
    """
    A selection proxy model which allows showing files but make them
    unselectable.
    """

    def flags(self, index) -> QtCore.Qt.ItemFlags:
        """
        Return item flags for the given index.

        Parameters
        ----------
        index
            The model index.

        Returns
        -------
        QtCore.Qt.ItemFlags
            The flags for the given index.
        """
        _flags = QtCore.QIdentityProxyModel.flags(self, index)
        if not self.sourceModel().isDir(index):  # type: ignore[attr-defined]
            _flags &= ~ITEM_SELECTABLE
        return _flags


class PydidasFileDialog(
    SingletonObject, QtWidgets.QFileDialog, CreateWidgetsMixIn, PydidasQsettingsMixin
):
    """
    pydidas's subclassed QFileDialog with additional functionality.

    The PydidasFileDialogWidget is a subclassed QFileDialog with two additional
    buttons which allow fast navigation to the ScanContext base directory and to the
    latest selected directory (in any dialog).

    The usage is the same as for the generic QFileDialog.
    """

    def initialize(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the PydidasFileDialog.

        Parameters
        ----------
        *args : Any
            Positional arguments.
        **kwargs : Any
            Keyword arguments. Supported keywords are:

            parent : QWidget or None, optional
                The dialog's parent widget. The default is None.
            caption : str or None, optional
                The dialog caption. If None, the caption will be
                selected based on the type of dialog. The default is
                None.
            dialog_type : str
                The type of the dialog. Must be open_file, save_file,
                or open_directory. The default is open_file.
            formats : str or None, optional
                The list of format filters for filenames, if used. The
                default is None.
            info_string : str or None, optional
                An additional information string which is displayed in
                the FileDialog widget. The default is None.
        """
        self._files_unselectable_model = SelectionModel(self)
        self._config = {
            "caption": kwargs.get("caption", None),
            "type": kwargs.get("dialog_type", "open_file"),
            "formats": kwargs.get("formats", None),
            "info_string": kwargs.get("info_string", None),
            "default_suffix": kwargs.get("default_suffix", None),
        }
        self._stored_dirs = {}
        self._stored_selections = {}
        self._calling_kwargs = {}

        self._configure_dialog()
        self._insert_buttons_into_sidebar()
        self._widgets["but_latest_location"].clicked.connect(self.goto_latest_location)
        self._widgets["but_scan_home"].clicked.connect(self.goto_scan_base_dir)

    # ========================================================================
    # Private initialization and setup methods
    # ========================================================================

    def _configure_dialog(self) -> None:
        """Set up the basic configuration for the FileDialog."""
        self.setViewMode(QtWidgets.QFileDialog.Detail)
        self.setOptions(
            QtWidgets.QFileDialog.DontUseNativeDialog  # type: ignore[operator]
            | QtWidgets.QFileDialog.DontResolveSymlinks
            | QtWidgets.QFileDialog.DontUseCustomDirectoryIcons
        )
        _desktop = QStandardPaths.standardLocations(QStandardPaths.DesktopLocation)[0]
        _docs = QStandardPaths.standardLocations(QStandardPaths.DocumentsLocation)[0]
        self.setSidebarUrls(
            [
                QtCore.QUrl("file:"),
                QtCore.QUrl.fromLocalFile(QtCore.QDir.homePath()),
                QtCore.QUrl.fromLocalFile(_desktop),
                QtCore.QUrl.fromLocalFile(_docs),
            ]
        )
        self._widgets["selection"] = self.findChild(QtWidgets.QLineEdit)

    def _insert_buttons_into_sidebar(self) -> None:
        """Insert buttons to access specific locations and optional text fields."""
        _splitter = self.findChild(QtWidgets.QSplitter)
        _sidebar = _splitter.widget(0)
        _fileview = _splitter.widget(1)
        # Create a container widget for the sidebar to hold the buttons and the
        # original sidebar content:
        _sidebar.setMinimumWidth(180)
        _sidebar.setParent(None)
        self.create_empty_widget(
            "sidebar_container",
            font_metric_width_factor=FONT_METRIC_EXTRAWIDE_BUTTON_WIDTH,
            parent_widget=None,
        )
        self.create_button(
            "but_latest_location",
            "Open latest selected location",
            icon="qt-std::SP_BrowserReload",
            parent_widget=self._widgets["sidebar_container"],
        )
        self.create_button(
            "but_scan_home",
            "Open scan base directory",
            icon=icons.get_pydidas_qt_icon("scan_home.png"),
            parent_widget=self._widgets["sidebar_container"],
        )
        self.add_any_widget(
            "sidebar", _sidebar, parent_widget=self._widgets["sidebar_container"]
        )
        # Create a container widget for the file view to hold the original
        # file view and an additional label for information:
        _fileview.setParent(None)
        self.create_empty_widget("fileview_frame", parent_widget=None)
        self.create_label(
            "info_label",
            "",
            parent_widget=self._widgets["fileview_frame"],
            margin=15,
        )
        self.add_any_widget(
            "fileview", _fileview, parent_widget=self._widgets["fileview_frame"]
        )
        # Re-insert the new container widgets into the splitter:
        _splitter.insertWidget(0, self._widgets["sidebar_container"])
        _splitter.insertWidget(1, self._widgets["fileview_frame"])

    # ========================================================================
    # Slot handlers for navigation buttons
    # ========================================================================

    @QtCore.Slot()
    def goto_latest_location(self) -> None:
        """Open the latest location from any dialogue."""
        self.setDirectory(self.q_settings_get("dialogues/current"))

    @QtCore.Slot()
    def goto_scan_base_dir(self) -> None:
        """Open the ScanContext home directory, if set."""
        _scan_base = SCAN.get_param_value("scan_base_directory", dtype=str)
        self.setDirectory(_scan_base)

    # ========================================================================
    # Core public API methods - Dialog execution
    # ========================================================================

    def exec_(self) -> int:
        """
        Execute the dialog.

        Returns
        -------
        int
            The return code of the file dialog.
        """
        _char_width, _char_height = PydidasQApplication.instance().font_metrics
        _geo_width = int(_char_width * 160)
        _geo_height = int(_char_height * 32)
        # noinspection PyTypeChecker
        update_child_qobject(  # type: ignore[arg-type]
            self, "geometry", width=_geo_width, height=_geo_height
        )

        _info_text = self._calling_kwargs.get("info_string", "")
        self._widgets["info_label"].setText(_info_text)
        self._widgets["info_label"].setVisible(len(_info_text) > 0)

        _scan_base = SCAN.get_param_value("scan_base_directory")
        _scan_base_valid = _scan_base.is_dir() and _scan_base != Path()
        self._widgets["but_scan_home"].setEnabled(_scan_base_valid)
        _latest = self.q_settings_get("dialogues/current")
        if _latest is not None:
            self._widgets["but_latest_location"].setEnabled(Path(_latest).is_dir())
        _stored_selection, _stored_dir = self._get_stored_entries()
        if _stored_dir is not None:
            self.setDirectory(_stored_dir)
            self.selectFile(_stored_selection)
        self._widgets["selection"].setText(_stored_selection)
        return QtWidgets.QFileDialog.exec_(self)

    def get_existing_directory(self, **kwargs: Any) -> str | None:
        """
        Execute the dialog and get an existing directory.

        Parameters
        ----------
        **kwargs : Any
            Optional keyword arguments. Supported keywords are:

            caption : str, optional
                The window title caption. The default is 'Select directory'.
            reference : str or int, optional
                A reference key to store the selection only during the
                active instance. The default is None.
            qsettings_ref : str, optional
                The reference key for storing the selection in the
                QSettings registry. The qsettings_ref will take
                precedence over the reference keyword.
            info_string : str, optional
                An additional info string to be displayed at the top
                of the file selection for user information.

        Returns
        -------
        str or None
            The directory path, if selected or None.
        """
        self._store_calling_kwargs(kwargs)
        self.setWindowTitle(kwargs.get("caption", "Select directory"))
        self.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
        self.setFileMode(QtWidgets.QFileDialog.Directory)
        self.setProxyModel(self._files_unselectable_model)
        res = self.exec_()
        if res == 0:
            return None
        _selection = self.selectedFiles()[0]
        self._store_current_directory()
        return _selection

    def get_existing_filename(self, **kwargs: Any) -> str | None:
        """
        Execute the dialog and get the full path of an existing file.

        Parameters
        ----------
        **kwargs : Any
            Optional keyword arguments. Supported keywords are:

            caption : str, optional
                The window title caption. The default is 'Select existing file'.
            formats : str, optional
                The list of format filters for filenames. The formats
                string should be in the format of
                "Description (*.ext1 *.ext2);;Another description (*.ext3)".
            reference : str or int, optional
                A reference key to store the selection only during the
                active instance. The default is None.
            select_multiple : bool, optional
                If True, multiple files can be selected. The default is False.
            qsettings_ref : str, optional
                The reference key for storing the selection in the
                QSettings registry. The qsettings_ref will take
                precedence over the reference keyword.

        Returns
        -------
        str or None
            The full file path, if selected, or None.
        """
        self._store_calling_kwargs(kwargs)
        _select_multiple = kwargs.get("select_multiple", False)
        self.setWindowTitle(kwargs.get("caption", "Select existing file"))
        self._set_name_filter()
        self.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
        self.setFileMode(
            QtWidgets.QFileDialog.ExistingFiles
            if _select_multiple
            else QtWidgets.QFileDialog.ExistingFile
        )
        self.setProxyModel(None)  # type: ignore[arg-type]
        res = self.exec_()
        if res == 0:
            return None
        self._store_current_directory()
        if _select_multiple:
            return self.selectedFiles()  # type: ignore[return-value]
        return self.selectedFiles()[0]

    def get_existing_filenames(self, **kwargs: Any) -> list[str]:
        """
        Execute the dialog and get a list of existing files.

        This is a wrapper around get_existing_filename with the necessary
        kwargs settings taken care of for the user.

        Please refer to get_existing_filename for more information and
        Parameters.
        """
        kwargs["caption"] = "Select existing files"
        kwargs["select_multiple"] = True
        _names = self.get_existing_filename(**kwargs)
        return [] if _names is None else _names

    def get_saving_filename(self, **kwargs: Any) -> str | None:
        """
        Execute the dialog and get the full path of a file for saving.

        The file may exist or a new filename can be entered.

        Parameters
        ----------
        **kwargs : Any
            Optional keyword arguments. Supported keywords are:

            caption : str, optional
                The window title caption. The default is 'Select
                filename'.
            reference : str or int, optional
                A reference key to store the selection only during the
                active instance. The default is None.
            qsettings_ref : str, optional
                The reference key for storing the selection in the
                QSettings registry. The qsettings_ref will take
                precedence over the reference keyword.

        Returns
        -------
        str or None
            The full file path, if selected, or None.
        """
        self._store_calling_kwargs(kwargs)
        self._set_name_filter()
        self.setWindowTitle(kwargs.get("caption", "Select filename"))
        self.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        self.setFileMode(QtWidgets.QFileDialog.AnyFile)
        self.setProxyModel(None)  # type: ignore[arg-type]
        res = self.exec_()
        if res == 0:
            return None
        _selection = self.selectedFiles()[0]
        _ext = get_extension(_selection)
        if len(_ext) == 0:
            _selection = _selection + self._get_extension()
        else:
            self._check_extension(_ext)
        self._store_current_directory()
        return _selection

    # ========================================================================
    # Public utility methods
    # ========================================================================

    def set_curr_dir(self, reference: str | int, item: Path | str) -> None:
        """
        Set the current directory to the directory of the given item.

        Parameters
        ----------
        reference : str or int
            The stored reference name.
        item : Path or str
            The filename or directory name.
        """
        if isinstance(item, Path):
            item = str(item)
        if os.path.isfile(item):
            item = os.path.dirname(item)
        elif not os.path.isdir(item):
            raise UserConfigError(
                f"The given entry {item} is neither a valid directory "
                "nor file. Please check the input and try again."
            )
        self._stored_dirs[reference] = item

    # ========================================================================
    # Private helper methods
    # ========================================================================

    def _store_calling_kwargs(self, kwarg_dict: dict[str, Any]) -> None:
        """
        Store the kwargs of the calling method for later use.

        Parameters
        ----------
        kwarg_dict : dict[str, Any]
            The kwargs to store.
        """
        if "reference" in kwarg_dict and "qsettings_ref" in kwarg_dict:
            raise UserConfigError(
                "Both `reference` and `qsettings_ref` keys are given in the kwargs. "
                "Please only use one of them to avoid conflicts."
            )
        self._calling_kwargs = kwarg_dict

    def _get_stored_entries(self) -> tuple[str, str | None]:
        """
        Get the stored directory and selection based on the reference name.

        If a 'qsettings_ref' key is given, this takes precedence over the 'reference'
        key.

        Returns
        -------
        str
            The stored selection or an empty string if no selection was saved.
        str | None
            The stored directory, if existing or None.
        """
        if self._calling_kwargs.get("qsettings_ref") is not None:
            _key = "dialogues/" + self._calling_kwargs.get("qsettings_ref")
            return self._stored_selections.get(_key, ""), self.q_settings_get(_key)
        if "reference" in self._calling_kwargs:
            _key = self._calling_kwargs.get("reference")
            return self._stored_selections.get(_key, ""), self._stored_dirs.get(_key)
        return "", None

    def _store_current_directory(self) -> None:
        """Store the active directory for re-opening the file dialog."""
        _selection = Path(self.selectedFiles()[0])
        if not _selection.is_dir():
            _selection = _selection.parent
        _curr_dir = str(_selection)
        self.q_settings_set("dialogues/current", _curr_dir)
        _key = None
        if self._calling_kwargs.get("qsettings_ref") is not None:
            _key = "dialogues/" + self._calling_kwargs.get("qsettings_ref")
            self.q_settings_set(_key, _curr_dir)
        if "reference" in self._calling_kwargs:
            _key = self._calling_kwargs.get("reference")
            self._stored_dirs[_key] = _curr_dir
        if _key is not None:
            self._stored_selections[_key] = self._widgets["selection"].text()

    def _set_name_filter(self) -> None:
        """Set the file dialog's nameFilter based on the specified formats."""
        _formats = self._calling_kwargs.get("formats")
        self.setNameFilter(_formats)
        self._config["valid_extensions"] = None
        if _formats is not None:
            if len(_formats) >= 2 and _formats.split(";;")[0] == "All files (*)":
                self.selectNameFilter(_formats.split(";;")[1])
            _exts = []
            for _fmt in _formats.split(";;"):
                _suffixes = [_ext.strip() for _ext in _fmt.strip(")").split("*")[1:]]
                _curr_exts = [_ext for _ext in _suffixes if _ext and _ext not in _exts]
                _exts.extend(_curr_exts)
            if "*" in _exts:
                _exts.pop(_exts.index("*"))
            if _exts:
                self._config["valid_extensions"] = _exts

    def _get_extension(self) -> str:
        """
        Get an extension for the selected filename.

        The extension will be selected from the list of selected extensions, if
        possible.

        Returns
        -------
        str
            The extension for the filename.
        """
        _global_default_suffixes = [".yaml", ".nxs", ".npy", ".tif", ".h5"]
        _filter = self.selectedNameFilter()
        _filtered_extensions = [
            _e.strip() for _e in _filter.removesuffix(")").split("*")[1:]
        ]
        if _filtered_extensions in ([""], []):
            return ""
        _default = self._calling_kwargs.get("default_suffix")
        if _default is not None and _default in _filtered_extensions:
            return _default
        for _suffix in _global_default_suffixes:
            if _suffix in _filtered_extensions:
                return _suffix
        return _filtered_extensions[0]

    def _check_extension(self, extension: str) -> None:
        """
        Check the given extension and confirm that it is valid.

        Parameters
        ----------
        extension : str
            The extension.
        """
        if self._config["valid_extensions"] is None:
            return
        if extension not in self._config["valid_extensions"]:
            raise UserConfigError(
                f"The given extension `{extension}` is invalid because the file type "
                "is not supported for this use case."
            )

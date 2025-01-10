# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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
Module with PydidasFileDialog which is a persistent QFileDialog which allows to keep
persistent references to the selected directory.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasFileDialog"]


import os
import pathlib
from typing import Union

from qtpy import QtCore, QtWidgets

from pydidas.contexts import ScanContext
from pydidas.core import PydidasQsettingsMixin, SingletonFactory, UserConfigError
from pydidas.core.constants import FONT_METRIC_EXTRAWIDE_BUTTON_WIDTH
from pydidas.core.utils import flatten, update_child_qobject
from pydidas.resources import icons
from pydidas.widgets.factory import CreateWidgetsMixIn


SCAN = ScanContext()
ITEM_SELECTABLE = QtCore.Qt.ItemIsSelectable


class SelectionModel(QtCore.QIdentityProxyModel):
    """A selection proxy model which allows to show files but make them unselectable."""

    def flags(self, index):
        _flags = QtCore.QIdentityProxyModel.flags(self, index)
        if not self.sourceModel().isDir(index):
            _flags &= ~ITEM_SELECTABLE
        return _flags


class PydidasFileDialogWidget(
    QtWidgets.QFileDialog, CreateWidgetsMixIn, PydidasQsettingsMixin
):
    """
    pydidas's subclassed QFileDialog with additional functionality.

    The PydidasFileDialogWidget is a subclassed QFileDialog with two additional
    buttons which allow fast navigation to the ScanContext base directory and to the
    latest selected directory (in any dialog).

    The usage is the same as for the generic QFileDialog.

    Parameters
    ----------
    parent : Union[None, QWidget], optional
        The dialog's parent widget. The default is None.
    caption : Union[None, str], optional
        The dialog caption. If None, the caption will be selected based on the
        type of dialog. The default is None.
    dialog_type : str
        The type of the dialog. Must be open_file, save_file, or open_directory.
        The default is open_file.
    formats : Union[None, str], optional
        The list of format filters for filenames, if used. The default is None.
    info_string : Union[None, str], optional
        An additional information string which is displayed in the FileDialog widget.
        The default is None.
    """

    def __init__(self, **kwargs: dict):
        QtWidgets.QFileDialog.__init__(self, kwargs.get("parent", None))
        CreateWidgetsMixIn.__init__(self)
        PydidasQsettingsMixin.__init__(self)
        self._files_unselectable_model = SelectionModel(self)
        self._config = {
            "caption": kwargs.get("caption", None),
            "type": kwargs.get("dialog_type", "open_file"),
            "formats": kwargs.get("formats", None),
            "info_string": kwargs.get("info_string", None),
            "default_extension": kwargs.get("default_extension", None),
        }
        self._stored_dirs = {}
        self._stored_selections = {}
        self._calling_kwargs = {}

        self._set_basic_widget_configuration()
        self._update_widgets()
        self._widgets["but_latest_location"].clicked.connect(self.goto_latest_location)
        self._widgets["but_scan_home"].clicked.connect(self.goto_scan_base_dir)

    def _set_basic_widget_configuration(self):
        """Set the basic configuration for the widget."""
        self.setViewMode(QtWidgets.QFileDialog.Detail)
        self.setOption(QtWidgets.QFileDialog.DontUseNativeDialog)
        self.setSidebarUrls(
            [
                QtCore.QUrl("file:"),
                QtCore.QUrl.fromLocalFile(QtCore.QDir.homePath()),
                QtCore.QUrl.fromLocalFile(
                    QtCore.QStandardPaths.standardLocations(
                        QtCore.QStandardPaths.DesktopLocation
                    )[0]
                ),
                QtCore.QUrl.fromLocalFile(
                    QtCore.QStandardPaths.standardLocations(
                        QtCore.QStandardPaths.DocumentsLocation
                    )[0]
                ),
            ]
        )
        _sidebar = self.findChild(QtWidgets.QListView, "sidebar")
        _sidebar.setMinimumWidth(180)
        self._widgets["selection"] = self.findChild(QtWidgets.QLineEdit)

    def _update_widgets(self):
        """Insert buttons to access specific locations and optional text fields."""
        self.create_empty_widget(
            "sidebar_frame",
            font_metric_width_factor=FONT_METRIC_EXTRAWIDE_BUTTON_WIDTH,
            parent_widget=None,
        )
        self.create_empty_widget("fileview_frame", parent_widget=None)
        self.create_button(
            "but_latest_location",
            "Open latest selected location",
            icon="qt-std::SP_BrowserReload",
            parent_widget=self._widgets["sidebar_frame"],
        )
        self.create_button(
            "but_scan_home",
            "Open scan base directory",
            icon=icons.get_pydidas_qt_icon("scan_home.png"),
            parent_widget=self._widgets["sidebar_frame"],
        )
        _splitter = self.layout().itemAt(2).widget()
        _listview = _splitter.widget(0)
        _listview.setParent(None)
        self.add_any_widget(
            "listview", _listview, parent_widget=self._widgets["sidebar_frame"]
        )
        _splitter.insertWidget(0, self._widgets["sidebar_frame"])
        _fileview = _splitter.widget(1)
        _fileview.setParent(None)
        self.create_label(
            "info_label",
            "",
            parent_widget=self._widgets["fileview_frame"],
            margin=15,
        )
        self.add_any_widget(
            "fileview", _fileview, parent_widget=self._widgets["fileview_frame"]
        )
        _splitter.insertWidget(1, self._widgets["fileview_frame"])

    @QtCore.Slot()
    def goto_latest_location(self):
        """Open the latest location from any dialogue."""
        self.setDirectory(self.q_settings_get("dialogues/current"))

    @QtCore.Slot()
    def goto_scan_base_dir(self):
        """Open the ScanContext home directory, if set."""
        _scan_base = SCAN.get_param_value("scan_base_directory", dtype=str)
        self.setDirectory(_scan_base)

    def exec_(self) -> int:
        """
        Execute the dialog.

        Returns
        -------
        int
            The return code of the file dialog.
        """
        _char_width, _char_height = QtWidgets.QApplication.instance().font_metrics
        _geo_width = int(_char_width * 160)
        _geo_height = int(_char_height * 32)
        update_child_qobject(self, "geometry", width=_geo_width, height=_geo_height)

        self._widgets["info_label"].setText(self._calling_kwargs.get("info_string", ""))
        self._widgets["info_label"].setVisible(
            len(self._widgets["info_label"].text()) > 0
        )

        _scan_base = SCAN.get_param_value("scan_base_directory", dtype=str)
        self._widgets["but_scan_home"].setEnabled(os.path.isdir(_scan_base))
        _latest = self.q_settings_get("dialogues/current")
        if _latest is not None:
            self._widgets["but_latest_location"].setEnabled(os.path.isdir(_latest))
        _stored_selection, _stored_dir = self._get_stored_entries()
        if _stored_dir is not None:
            self.setDirectory(_stored_dir)
            self.selectFile(_stored_selection)
        self._widgets["selection"].setText(_stored_selection)
        return QtWidgets.QFileDialog.exec_(self)

    def _get_stored_entries(self) -> Union[str, None]:
        """
        Get the stored directory and selection based on the reference name.

        If a 'qsettings_ref' key is given, this takes precendence over the 'reference'
        key.

        Returns
        -------
        str
            The stored selection or an empty string if no selection was saved.
        Union[str, None]
            The stored directory, if existing or None.
        """
        if self._calling_kwargs.get("qsettings_ref") is not None:
            _key = "dialogues/" + self._calling_kwargs.get("qsettings_ref")
            return self._stored_selections.get(_key, ""), self.q_settings_get(_key)
        if "reference" in self._calling_kwargs:
            _key = self._calling_kwargs.get("reference")
            return self._stored_selections.get(_key, ""), self._stored_dirs.get(_key)
        return "", None

    def get_existing_directory(self, **kwargs: dict) -> Union[None, str]:
        """
        Execute the dialog and get an existing directory.

        Parameters
        ----------
        **kwargs : dict
            Optional keyword arguments. Supported keywords are:

            caption : str, optional
                The window title caption. The default is 'Select directory'.
            reference : Union[str, int], optional
                A reference key to store the selection only during the active instance.
                The default is None.
            qsettings_ref : str, optional
                The reference key for storing the selection in the QSettings registry.
                The qsettings_ref will take precedence over the reference keyword.
            info_string : str, optional
                An additional info string to be displayed at the top of the file
                selection for user information.

        Returns
        -------
        Union[str, None]
            The directory path, if selected or None.
        """
        self._calling_kwargs = kwargs
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

    def get_existing_filename(self, **kwargs: dict) -> Union[None, str]:
        """
        Execute the dialog and get the full path of an existing file.

        Parameters
        ----------
        **kwargs : dict
            Optional keyword arguments. Supported keywords are:

            caption : str, optional
                The window title caption. The default is 'Select existing file'.
            reference : Union[str, int], optional
                A reference key to store the selection only during the active instance.
                The default is None.
            select_multiple : bool, optional
                If True, multiple files can be selected. The default is False.
            qsettings_ref : str, optional
                The reference key for storing the selection in the QSettings registry.
                The qsettings_ref will take precedence over the reference keyword.

        Returns
        -------
        Union[str, None]
            The full file path, if selected, or None.
        """
        self._calling_kwargs = kwargs
        _select_multiple = kwargs.get("select_multiple", False)
        self.setWindowTitle(kwargs.get("caption", "Select existing file"))
        self._set_name_filter()
        self.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
        self.setFileMode(
            QtWidgets.QFileDialog.ExistingFiles
            if _select_multiple
            else QtWidgets.QFileDialog.ExistingFile
        )
        self.setProxyModel(None)
        res = self.exec_()
        if res == 0:
            return None
        self._store_current_directory()
        if _select_multiple:
            return self.selectedFiles()
        return self.selectedFiles()[0]

    def get_existing_filenames(self, **kwargs: dict) -> list[str]:
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

    def _set_name_filter(self):
        """
        Set the file dialog's nameFilter based on the specified formats.
        """
        _formats = self._calling_kwargs.get("formats")
        self.setNameFilter(_formats)
        if _formats is not None:
            if _formats.split(";;")[0] == "All files (*.*)":
                self.selectNameFilter(_formats.split(";;")[1])
            if "All supported files" in _formats:
                _exts = [
                    [_ext.strip() for _ext in _entry.strip(")").split("*.")[1:]]
                    for _entry in _formats.split(";;")
                    if _entry.startswith("All supported files")
                ][0]
            else:
                _exts = flatten(
                    [_ext.strip() for _ext in _entry.strip(")").split("*.")[1:]]
                    for _entry in _formats.split(";;")
                )
            if "*" in _exts:
                _exts.pop(_exts.index("*"))
            self._calling_kwargs["extensions"] = _exts if len(_exts) > 0 else None

    def _store_current_directory(self):
        """
        Store the active directory for re-opening the file dialog.
        """
        _selection = self.selectedFiles()[0]
        if not os.path.isdir(_selection):
            _selection = os.path.dirname(_selection)
        self.q_settings_set("dialogues/current", _selection)
        if self._calling_kwargs.get("qsettings_ref", None) is not None:
            _key = "dialogues/" + self._calling_kwargs.get("qsettings_ref")
            self.q_settings_set(_key, _selection)
            self._stored_selections[_key] = self._widgets["selection"].text()
            return
        if "reference" in self._calling_kwargs:
            self._stored_dirs[self._calling_kwargs.get("reference")] = _selection
            self._stored_selections[self._calling_kwargs.get("reference")] = (
                self._widgets["selection"].text()
            )

    def get_saving_filename(self, **kwargs: dict) -> Union[None, str]:
        """
        Execute the dialog and get the full path of a file for saving.

        The file may exist or a new filename can be entered.

        Parameters
        ----------
        **kwargs : dict
            Optional keyword arguments. Supported keywords are:

            caption : str, optional
                The window title caption. The default is 'Select filename'.
            reference : Union[str, int], optional
                A reference key to store the selection only during the active
                instance. The default is None.
            qsettings_ref : str, optional
                The reference key for storing the selection in the QSettings
                registry. The qsettings_ref will take precedence over the
                reference keyword.

        Returns
        -------
        Union[str, None]
            The full file path, if selected, or None.
        """
        self._calling_kwargs = kwargs
        self._set_name_filter()
        self.setWindowTitle(kwargs.get("caption", "Select filename"))
        self.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        self.setFileMode(QtWidgets.QFileDialog.AnyFile)
        self.setProxyModel(None)
        res = self.exec_()
        if res == 0:
            return None
        _selection = self.selectedFiles()[0]
        _ext = os.path.splitext(_selection)[1]
        if len(_ext) == 0:
            _selection = _selection + self._get_extension()
        else:
            self._check_extension(_ext)
        self._store_current_directory()
        return _selection

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
        if self._calling_kwargs["extensions"] is None:
            return ""
        if self.selectedNameFilter().startswith(
            "All files"
        ) or self.selectedNameFilter().startswith("All supported files"):
            if self._calling_kwargs.get("default_extension") is not None:
                return "." + self._calling_kwargs.get("default_extension")
            _defaults = ["yaml", "npy", "tif", "h5"]
            while len(_defaults) > 0:
                _ext = _defaults.pop(0)
                if _ext in self._calling_kwargs["extensions"]:
                    return f".{_ext}"
            return self._calling_kwargs["extensions"][0]
        _formats = self.selectedNameFilter().strip(")").split("*.")[1:]
        return "." + _formats[0]

    def _check_extension(self, extension: str):
        """
        Check the given extension and confirm that it is valid.

        Parameters
        ----------
        extension : str
            The extension.
        """
        if self._calling_kwargs["extensions"] is None:
            return
        if extension.strip(".") not in self._calling_kwargs["extensions"]:
            raise UserConfigError(
                f'The given extension "{extension}" is invalid because the file type '
                "is unknown."
            )

    def set_curr_dir(self, reference: Union[str, int], item: Union[pathlib.Path, str]):
        """
        Set the current directory to the directory of the given item.

        Parameters
        ----------
        reference: Union[str, int]
            The stored reference name.
        item : Union[pathlib.Path, str]
            The filename or directory name.
        """
        if isinstance(item, pathlib.Path):
            item = str(item)
        if os.path.isfile(item):
            item = os.path.dirname(item)
        elif not os.path.isdir(item):
            raise UserConfigError(
                f"The given entry {item} is neither a valid directory nor file. Please "
                "check the input and try again."
            )
        self._stored_dirs[reference] = item


PydidasFileDialog = SingletonFactory(PydidasFileDialogWidget)

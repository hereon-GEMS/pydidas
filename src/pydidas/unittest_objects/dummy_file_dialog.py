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
Module with a dummy PydidasFileDialog to use in unittests.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DummyFileDialog"]


import os
from pathlib import Path
from typing import Any, Iterable

from qtpy import QtCore, QtWidgets

from pydidas.contexts import Scan
from pydidas.core import (
    PydidasQsettingsMixin,
    UserConfigError,
)
from pydidas.core.utils import flatten


class DummyFileDialog(QtWidgets.QDialog, PydidasQsettingsMixin):
    """
    A dummy QFileDialog to emulate interaction in unittests.

    The usage is the same as for the generic QFileDialog.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the PydidasFileDialog.

        Parameters
        ----------
        *args : Any
            Positional arguments.
        **kwargs : Any
            Keyword arguments. Supported keywords are:

            parent : Union[None, QWidget], optional
                The dialog's parent widget. The default is None.
            caption : str | None, optional
                The dialog caption. If None, the caption will be selected based on the
                type of dialog. The default is None.
            dialog_type : str
                The type of the dialog. Must be open_file, save_file, or open_directory.
                The default is open_file.
            formats : str | None, optional
                The list of format filters for filenames, if used. The default is None.
            info_string : str | None, optional
                An additional information string which is displayed in the FileDialog
                widget. The default is None.
        """
        super().__init__()
        self._SCAN = Scan()
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
        self._returned_selection = None
        self._return_code = 1

    @property
    def returned_selection(self) -> list[str] | None:
        """Get the returned selection."""
        return self._returned_selection

    @returned_selection.setter
    def returned_selection(self, value: None | str | Path | Iterable[str | Path]):
        """Set the returned selection."""
        if isinstance(value, (str, Path)):
            self._returned_selection = [str(value)]
        elif isinstance(value, Iterable):
            self._returned_selection = [str(item) for item in value]
        elif value is None:
            self._returned_selection = None
        else:
            raise UserConfigError(
                "The returned_selection must be set to a str, Path, or iterable of "
                "str or Path entries."
            )

    @property
    def return_code(self) -> int:
        """Get the return code."""
        if self.returned_selection is None:
            return 0
        return self._return_code

    @return_code.setter
    def return_code(self, value: int):
        """Set the return code."""
        if not isinstance(value, int):
            raise UserConfigError("The return_code must be an integer.")
        self._return_code = value

    @QtCore.Slot()
    def goto_latest_location(self):
        """Open the latest location from any dialogue."""
        self.setDirectory(self.q_settings_get("dialogues/current"))

    @QtCore.Slot()
    def goto_scan_base_dir(self):
        """Open the ScanContext home directory, if set."""
        _scan_base = self._SCAN.get_param_value("scan_base_directory", dtype=str)
        self.setDirectory(_scan_base)

    def exec_(self) -> int:
        """
        Execute the dialog. For the dummy, just pass.

        Returns
        -------
        int
            The return code of the file dialog.
        """
        return self.return_code

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

    def get_existing_directory(self, **kwargs: Any) -> str | None:
        """
        Execute the dialog and get an existing directory.

        Parameters
        ----------
        **kwargs : Any
            Optional keyword arguments. Supported keywords are:

            caption : str, optional
                The window title caption. The default is 'Select directory'.
            reference : str | int, optional
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
        str | None
            The directory path, if selected or None.
        """
        self._calling_kwargs = kwargs
        res = self.exec_()
        if res == 0:
            return None
        _selection = self.returned_selection[0]
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
            reference : str | int, optional
                A reference key to store the selection only during the active instance.
                The default is None.
            select_multiple : bool, optional
                If True, multiple files can be selected. The default is False.
            qsettings_ref : str, optional
                The reference key for storing the selection in the QSettings registry.
                The qsettings_ref will take precedence over the reference keyword.

        Returns
        -------
        str | None
            The full file path, if selected, or None.
        """
        self._calling_kwargs = kwargs
        _select_multiple = kwargs.get("select_multiple", False)
        res = self.exec_()
        if res == 0:
            return None
        self._store_current_directory()
        if _select_multiple:
            return self.returned_selection
        return self.returned_selection[0]

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
        _selection = self.returned_selection[0]
        if not os.path.isdir(_selection):
            _selection = os.path.dirname(_selection)
        self.q_settings_set("dialogues/current", _selection)
        if self._calling_kwargs.get("qsettings_ref", None) is not None:
            _key = "dialogues/" + self._calling_kwargs.get("qsettings_ref")
            self.q_settings_set(_key, _selection)
            self._stored_selections[_key] = self.returned_selection
            return
        if "reference" in self._calling_kwargs:
            self._stored_dirs[self._calling_kwargs.get("reference")] = _selection
            self._stored_selections[self._calling_kwargs.get("reference")] = (
                self.returned_selection
            )

    def get_saving_filename(self, **kwargs: Any) -> str | None:
        """
        Execute the dialog and get the full path of a file for saving.

        The file may exist or a new filename can be entered.

        Parameters
        ----------
        **kwargs : Any
            Optional keyword arguments. Supported keywords are:

            caption : str, optional
                The window title caption. The default is 'Select filename'.
            reference : str | int, optional
                A reference key to store the selection only during the active
                instance. The default is None.
            qsettings_ref : str, optional
                The reference key for storing the selection in the QSettings
                registry. The qsettings_ref will take precedence over the
                reference keyword.

        Returns
        -------
        str | None
            The full file path, if selected, or None.
        """
        self._calling_kwargs = kwargs
        res = self.exec_()
        if res == 0:
            return None
        _selection = self.returned_selection[0]
        _ext = os.path.splitext(_selection)[1]
        if len(_ext) == 0:
            _selection = _selection + self._get_extension()
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
        _default = self._calling_kwargs["extensions"][0]
        return f".{_default}"

    def set_curr_dir(self, reference: str | int, item: Path | str):
        """
        Set the current directory to the directory of the given item.

        Parameters
        ----------
        reference: str | int
            The stored reference name.
        item : Path | str
            The filename or directory name.
        """
        if isinstance(item, Path):
            item = str(item)
        if os.path.isfile(item):
            item = os.path.dirname(item)
        elif not os.path.isdir(item):
            raise UserConfigError(
                f"The given entry {item} is neither a valid directory nor file. Please "
                "check the input and try again."
            )
        self._stored_dirs[reference] = item

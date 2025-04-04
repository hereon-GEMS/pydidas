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
Module with the ParamIoWidgetFile class used to edit Parameters with a file
path type.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ParamIoWidgetFile"]


import os
from pathlib import Path
from typing import Union

from numpy import nan
from qtpy import QtCore

from pydidas.data_io import IoManager
from pydidas.widgets.dialogues import critical_warning
from pydidas.widgets.file_dialog import PydidasFileDialog
from pydidas.widgets.parameter_config.param_io_widget_with_button import (
    ParamIoWidgetWithButton,
)


class ParamIoWidgetFile(ParamIoWidgetWithButton):
    """
    Widget to select a Path entry for a Parameter.

    This widget includes a small button to select a filepath from a dialogue.
    """

    io_edited = QtCore.Signal(str)

    def __init__(self, param, **kwargs):
        """
        Set up the widget.

        Init method to set up the widget and set the links to the parameter
        and Qt parent widget.

        Parameters
        ----------
        parent : QWidget
            A QWidget instance.
        param : Parameter
            A Parameter instance.
        **kwargs : dict
            Optional keyword arguments. Supported kwargs are "width" (in pixels) for
            the width of the I/O widget and "persistent_qsettings_ref" for the
            persistent reference label of the open directory.
        """
        ParamIoWidgetWithButton.__init__(self, param, **kwargs)
        self.setAcceptDrops(True)
        self._flag_pattern = "pattern" in param.refkey
        self.io_dialog = PydidasFileDialog()
        if "directory" in param.refkey:
            self.io_dialog_call = self.io_dialog.get_existing_directory
        else:
            if param.refkey.startswith("output"):
                self.io_dialog_call = self.io_dialog.get_saving_filename
            else:
                self.io_dialog_call = self.io_dialog.get_existing_filename
        self._io_dialog_config = {
            "reference": id(self),
            "formats": "All files (*.*);;" + IoManager.get_string_of_formats(),
            "qsettings_ref": kwargs.get("persistent_qsettings_ref"),
        }

    def button_function(self):
        """
        Open a dialogue to select a file.

        This method is called upon clicking the "open file" button
        and opens a QFileDialog widget to select a filename.
        """
        _result = self.io_dialog_call(**self._io_dialog_config)
        if _result is not None:
            if self._flag_pattern:
                self.io_dialog.set_curr_dir(id(self), _result)
                _result = os.path.basename(_result)
            self.setText(_result)
            self.emit_signal()

    def get_value(self) -> Path:
        """
        Get the current value from the QLineEdit to update the Parameter value.

        Returns
        -------
        Path
            The text converted to a Path to update the Parameter value.
        """
        text = self._io_lineedit.text().strip()
        _value = self.get_value_from_text(text)
        if _value in [None, True, False, nan]:
            _value = "."
            self._io_lineedit.setText(".")
        return Path(_value)

    def set_value(self, value: Union[str, Path]):
        """
        Set the input field's value.

        This method changes the QLineEdit selection to the specified value.
        """
        self._old_value = self.get_value()
        self._io_lineedit.setText(f"{value}".strip())
        if not self._flag_pattern and value != Path() and os.path.exists(value):
            self.io_dialog.set_curr_dir(id(self), value)

    def modify_file_selection(self, list_of_choices: list):
        """
        Modify the file selection choices in the popup window.

        Parameters
        ----------
        list_of_choices : list
            The list with string entries for file selection choices in the
            format 'NAME (*.EXT1 *.EXT2 ...)'
        """
        self._file_selection = ";;".join(list_of_choices)

    def dragEnterEvent(self, event: QtCore.QEvent):
        """Allow to drag files from, for example, the explorer."""
        if event.mimeData().hasFormat("text/uri-list"):
            event.acceptProposedAction()

    def dropEvent(self, event: QtCore.QEvent):
        """
        Allow to drop files from, for example, the explorer.
        """
        mimeData = event.mimeData()
        if mimeData.hasUrls():
            urls = mimeData.urls()
            if len(urls) > 1:
                critical_warning("Not a single file", "A single file is expected.")
                return
            _path = urls[0].toLocalFile()
        else:
            critical_warning("Not a file", "Can only accept single files.")
            return
        self.set_value(_path)
        self.emit_signal()

    def set_unique_ref_name(self, name: str):
        """
        Set a unique reference name to allow keeping track of the active working
        directory.

        Parameters
        ----------
        name : str
            The unique identifier to reference this Parameter in the QSettings.
        """
        self._io_dialog_config["qsettings_ref"] = name

    def update_io_directory(self, path: str):
        """
        Update the file dialog's IO directory for the given Parameter.

        Parameters
        ----------
        path : str
            The path to the new directory.
        """
        self.io_dialog.set_curr_dir(id(self), path)

    def emit_signal(self, force_update: bool = False):
        """
        Emit a signal that the value has been edited.

        This method emits a signal that the combobox selection has been
        changed and the Parameter value needs to be updated.

        Parameters
        ----------
        force_update : bool
            Force an update even if the value has not changed.
        """
        _curr_value = self._io_lineedit.text().strip()
        if _curr_value != self._io_lineedit.text():
            self._io_lineedit.setText(_curr_value)
        if _curr_value != self._old_value or force_update:
            self._old_value = _curr_value
            self.io_edited.emit(_curr_value)

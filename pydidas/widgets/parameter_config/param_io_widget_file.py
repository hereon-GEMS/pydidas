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
Module with the ParamIoWidgetFile class used to edit Parameters with a file
path type.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ParamIoWidgetFile"]


import os
from pathlib import Path
from typing import Union

from qtpy import QtCore

from ...data_io import IoMaster
from ..dialogues import critical_warning
from ..file_dialog import PydidasFileDialog
from .param_io_widget_with_button import ParamIoWidgetWithButton


class ParamIoWidgetFile(ParamIoWidgetWithButton):
    """
    Widgets for I/O during plugin parameter for filepaths.
    (Includes a small button to select a filepath from a dialogue.)
    """

    io_edited = QtCore.Signal(str)

    def __init__(self, param, **kwargs):
        """
        Setup the widget.

        Init method to setup the widget and set the links to the parameter
        and Qt parent widget.

        Parameters
        ----------
        parent : QWidget
            A QWidget instance.
        param : Parameter
            A Parameter instance.
        **kwargs : dict
            Optional keyword arguments. Supported kwargs are "width" (in pixels) for
            the with of the I/O widget and  "persistent_qsettings_ref" for the
            persistent reference label of the open directory.
        """
        ParamIoWidgetWithButton.__init__(self, param, **kwargs)
        self.setAcceptDrops(True)
        self._flag_pattern = "pattern" in param.refkey
        if "directory" in param.refkey:
            _dialog_type = "open_directory"
        else:
            if param.refkey.startswith("output"):
                _dialog_type = "save_file"
            else:
                _dialog_type = "open_file"
        self.io_dialog = PydidasFileDialog(
            parent=self,
            dialog_type=_dialog_type,
            formats="All files (*.*);;" + IoMaster.get_string_of_formats(),
            qsettings_ref=kwargs.get("persistent_qsettings_ref"),
        )

    def button_function(self):
        """
        Open a dialogue to select a file.

        This method is called upon clicking the "open file" button
        and opens a QFileDialog widget to select a filename.
        """
        _result = self.io_dialog.get_user_response()
        if _result is not None:
            if self._flag_pattern:
                self.io_dialog.set_curr_dir(_result)
                _result = os.path.basename(_result)
            self.setText(_result)
            self.emit_signal()

    def get_value(self) -> Path:
        """
        Get the current value from the combobox to update the Parameter value.

        Returns
        -------
        Path
            The text converted to a Path to update the Parameter value.
        """
        text = self.ledit.text()
        return Path(self.get_value_from_text(text))

    def set_value(self, value: Union[str, Path]):
        """
        Set the input field's value.

        This method changes the combobox selection to the specified value.
        """
        self._old_value = self.get_value()
        self.ledit.setText(f"{value}")
        if not self._flag_pattern and value != Path() and os.path.exists(value):
            self.io_dialog.set_curr_dir(value)

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
        self.io_dialog.qsettings_ref = name

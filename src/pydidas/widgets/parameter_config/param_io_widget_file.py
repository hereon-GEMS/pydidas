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
from typing import Any

from qtpy import QtCore, QtGui

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

    def __init__(self, param, **kwargs: Any):
        """
        Set up the widget.

        Init method to set up the widget and set the links to the parameter
        and Qt parent widget.

        Parameters
        ----------
        param : Parameter
            A Parameter instance.
        **kwargs : Any
            Optional keyword arguments. Supported kwargs are
            all kwargs of BaseParamIoWidgetMixIn.
        """
        ParamIoWidgetWithButton.__init__(self, param, **kwargs)
        self.setAcceptDrops(True)
        self._flag_pattern = "pattern" in param.refkey
        self.io_dialog = kwargs.get("io_dialog", PydidasFileDialog())
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

    @QtCore.Slot()
    def button_function(self) -> None:
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
            self.set_value(_result)

    def set_value(self, value: Path | str) -> None:
        """
        Set the input field's value.

        This method changes the QLineEdit selection to the specified value.
        """
        super().set_value(value)
        if not self._flag_pattern and value != Path() and os.path.exists(value):
            self.io_dialog.set_curr_dir(id(self), value)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        """Allow to drag files from, for example, the explorer."""
        if event.mimeData().hasFormat("text/uri-list"):
            event.acceptProposedAction()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        """
        Allow to drop files from, for example, the explorer.
        """
        _mime_data = event.mimeData()
        if _mime_data.hasUrls():
            urls = _mime_data.urls()
            if len(urls) > 1:
                critical_warning("Not a single file", "A single file is expected.")
                return
            _path = urls[0].toLocalFile()
        else:
            critical_warning("Not a file", "Can only accept single files.")
            return
        self.set_value(_path)

    def update_widget_value(self, value: Any) -> None:
        """
        Update the widget value.

        Parameters
        ----------
        value : Any
            The new value to set in the widget.
        """
        if value is None:
            self._io_lineedit.setText("")
        else:
            self._io_lineedit.setText(f"{value}")

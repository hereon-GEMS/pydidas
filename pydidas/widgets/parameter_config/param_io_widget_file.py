# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
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
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["ParamIoWidgetFile"]

import os
import pathlib

from qtpy import QtWidgets, QtCore

from ...core.constants import PARAM_INPUT_EDIT_WIDTH
from ...data_io import IoMaster
from ..dialogues import critical_warning
from .param_io_widget_with_button import ParamIoWidgetWithButton


class ParamIoWidgetFile(ParamIoWidgetWithButton):
    """
    Widgets for I/O during plugin parameter for filepaths.
    (Includes a small button to select a filepath from a dialogue.)
    """

    io_edited = QtCore.Signal(str)

    def __init__(self, parent, param, width=PARAM_INPUT_EDIT_WIDTH):
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
        width : int, optional
            The width of the IOwidget.
        """
        super().__init__(parent, param, width)
        self.setAcceptDrops(True)
        self._flag_is_output = param.refkey.startswith("output")
        self._flag_is_dir = "directory" in param.refkey
        self._flag_pattern = "pattern" in param.refkey
        self._file_selection = "All files (*.*);;" + IoMaster.get_string_of_formats()

    def button_function(self):
        """
        Open a dialogue to select a file.

        This method is called upon clicking the "open file" button
        and opens a QFileDialog widget to select a filename.
        """
        if self._flag_is_dir:
            _arg = QtWidgets.QFileDialog.ShowDirsOnly
            _func = QtWidgets.QFileDialog.getExistingDirectory
            _fname = _func(self, "Name of directory", None, _arg)
        else:
            _arg = self._file_selection
            if self._flag_is_output:
                _func = QtWidgets.QFileDialog.getSaveFileName
            else:
                _func = QtWidgets.QFileDialog.getOpenFileName
            _fname = _func(self, "Name of file", None, _arg)[0]
        if self._flag_pattern:
            _fname = os.path.basename(_fname)
        if _fname:
            self.setText(_fname)
            self.emit_signal()

    def get_value(self):
        """
        Get the current value from the combobox to update the Parameter value.

        Returns
        -------
        Path
            The text converted to a pathlib.Path to update the Parameter value.
        """
        text = self.ledit.text()
        return pathlib.Path(self.get_value_from_text(text))

    def modify_file_selection(self, list_of_choices):
        """
        Modify the file selection choices in the popup window.

        Parameters
        ----------
        list_of_choices : list
            The list with string entries for file selection choices in the
            format 'NAME (*.EXT1 *.EXT2 ...)'
        """
        self._file_selection = ";;".join(list_of_choices)

    def dragEnterEvent(self, event):
        """
        Allow to drag files from, for example, the explorer.
        """
        if event.mimeData().hasFormat("text/uri-list"):
            event.acceptProposedAction()

    def dropEvent(self, event):
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

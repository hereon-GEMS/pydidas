# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Module with the InputWidgetFile class used to edit Parameters."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['InputWidgetFile']

import pathlib

from PyQt5 import QtWidgets, QtCore

from .input_widget_with_button import InputWidgetWithButton


class InputWidgetFile(InputWidgetWithButton):
    """
    Widgets for I/O during plugin parameter for filepaths.
    (Includes a small button to select a filepath from a dialogue.)
     """
    #for some reason, inhering the signal from the base class does not work
    io_edited = QtCore.pyqtSignal(str)

    def __init__(self, parent, param, width=255):
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
        self._output_flag = param.refkey.startswith('output')
        self._file_selection = (
            'All files (*.*);;HDF5 files ({"*"+" *".join(HDF5_EXTENSIONS)});;'
            'TIFF files (*.tif, *.tiff);;NPY files (*.npy *.npz)'
            )

    def button_function(self):
        """
        Open a dialogue to select a file.

        This method is called upon clicking the "open file" button
        and opens a QFileDialog widget to select a filename.
        """
        if self._output_flag:
            _func = QtWidgets.QFileDialog.getSaveFileName
        else:
            _func = QtWidgets.QFileDialog.getOpenFileName
        fname = _func(self, 'Name of file', None, self._file_selection)[0]
        if fname:
            self.setText(fname)
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
        self._file_selection = ';;'.join(list_of_choices)

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
"""Module with the InputWidgetHdf5Key class used to edit Parameters."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['InputWidgetHdf5Key']

from PyQt5 import QtWidgets, QtCore
from .input_widget_with_button import InputWidgetWithButton
from pydidas.widgets.dialogues import Hdf5DatasetSelectionPopup
from pydidas.constants import HDF5_EXTENSIONS

class InputWidgetHdf5Key(InputWidgetWithButton):
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

        Returns
        -------
        None.
        """
        super().__init__(parent, param, width)
        self._button.setToolTip(
            'Select a dataset from all dataset keys in a file.')

    def button_function(self):
        """
        Open a dialogue to select a file.

        This method is called upon clicking the "open file" button
        and opens a QFileDialog widget to select a filename.

        Returns
        -------
        None.
        """
        _fnames = ' *'.join(HDF5_EXTENSIONS)
        fname = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Name of file', None,
            (f'HDF5 files (*{_fnames});; All files (*.*)')
        )[0]
        if fname:
            dset = Hdf5DatasetSelectionPopup(self, fname).get_dset()
            if dset is not None:
                self.setText(str(dset))
                self.emit_signal()

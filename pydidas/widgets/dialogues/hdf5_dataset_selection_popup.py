# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""Module with Hdf5DatasetSelection class which shows a pop-up to select
from the available datasets in a hdf5 file."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['Hdf5DatasetSelectionPopup']

from PyQt5 import QtWidgets, QtGui
from ...utils import get_hdf5_populated_dataset_keys
from ...core import HdfKey

class Hdf5DatasetSelectionPopup(QtWidgets.QInputDialog):
    """
    QInputDialog subclass for showing a pop-up dialogue to select a dataset
    from an hdf5 file..
    """
    def __init__(self, parent, fname):
        """
        Generate a dialogue.


        Parameters
        ----------
        parent : Union[None, QWidget]
            The parent widget
        fname : Union[str, pathlib.Path]
            The file path to the hdf5 file.

        Returns
        -------
        None
        """
        super().__init__(parent)
        dsets = get_hdf5_populated_dataset_keys(fname, min_dim=2)
        font = QtWidgets.QApplication.instance().font()
        metrics = QtGui.QFontMetrics(font)
        width = max([metrics.boundingRect(d).width() for d in dsets])

        self.resize(width + 60, min(300, max(200, 50 + len(dsets)*10)))
        self.setOption(QtWidgets.QInputDialog.UseListViewForComboBoxItems, True)
        self.setComboBoxItems(dsets)
        self.setWindowTitle('Select hdf5 dataset')
        self.setLabelText('Hdf5 datasets:')

    def get_dset(self):
        """
        Show the QInputDialog

        Returns
        -------
        Union[HdfKey, None]
            If the dialogue is accepted, returns the selected HdfKey.
            If it is aborted, it will return None.
        """
        if self.exec_() == QtWidgets.QDialog.Accepted:
            return HdfKey(self.textValue())
        return None

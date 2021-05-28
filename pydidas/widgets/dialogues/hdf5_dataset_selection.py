# MIT License
#
# Copyright (c) 2021 Malte Storm, Helmholtz-Zentrum Hereon.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Module with Hdf5DatasetSelection class which shows a pop-up to select
from the available datasets in a hdf5 file."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['Hdf5DatasetSelection']

from PyQt5 import QtWidgets, QtGui
from ...utils import get_hdf5_populated_dataset_keys
from ...core import HdfKey

class Hdf5DatasetSelection(QtWidgets.QInputDialog):
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
        dsets = get_hdf5_populated_dataset_keys(fname, minDataDim=2)
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

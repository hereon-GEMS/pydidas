# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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
Module with Hdf5DatasetSelectionPopup class which shows a pop-up to select
from the available datasets in a hdf5 file.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["Hdf5DatasetSelectionPopup"]


from collections.abc import Iterable
from pathlib import Path
from typing import Union

from qtpy import QtWidgets

from pydidas.core import Hdf5key
from pydidas.core.utils import get_hdf5_populated_dataset_keys
from pydidas.widgets.utilities import (
    get_max_pixel_width_of_entries,
    get_pyqt_icon_from_str,
)


class Hdf5DatasetSelectionPopup(QtWidgets.QInputDialog):
    """
    A dialogue for showing a pop-up dialogue to select a dataset from an hdf5 file.

    Parameters
    ----------
    parent : Union[None, QWidget]
        The parent widget
    fname : Union[str, pathlib.Path]
        The file path to the hdf5 file.
    """

    def __init__(
        self,
        parent: Union[None, QtWidgets.QWidget] = None,
        fname: Union[None, Path] = None,
    ):
        QtWidgets.QInputDialog.__init__(self, parent)
        if fname is not None:
            dsets = get_hdf5_populated_dataset_keys(fname, min_dim=2)
            self.__update_combo_box_items(dsets)
        self.setWindowTitle("Select hdf5 dataset")
        self.setWindowIcon(get_pyqt_icon_from_str("qt-std::SP_FileDialogListView"))
        self.setLabelText("Hdf5 datasets:")

    def set_filename(self, fname: Union[Path, str]):
        """
        Set the filename for the Hdf5 file.

        Parameters
        ----------
        fname : str
            The full path to the Hdf5 file.
        """
        dsets = get_hdf5_populated_dataset_keys(fname, min_dim=2)
        self.__update_combo_box_items(dsets)

    def __update_combo_box_items(self, items: Iterable[str, ...]):
        """
        Update the ComboBox entries with new items.

        Parameters
        ----------
        items : Iterable[str, ...]
            The items which are to be displayed. This must be an iterable
            of string items.
        """
        _font_height = QtWidgets.QApplication.instance().font_height
        self.resize(
            get_max_pixel_width_of_entries(items) + 60,
            min(
                15 * _font_height,
                max(10 * _font_height, 50 + len(items) * _font_height),
            ),
        )
        self.setOption(QtWidgets.QInputDialog.UseListViewForComboBoxItems, True)
        self.setComboBoxItems(items)

    def get_dset(self) -> Union[Hdf5key, None]:
        """
        Show the QInputDialog.

        Returns
        -------
        Union[Hdf5key, None]
            If the dialogue is accepted, returns the selected Hdf5key.
            If it is aborted, it will return None.
        """
        if self.exec_() == QtWidgets.QDialog.Accepted:
            return Hdf5key(self.textValue())

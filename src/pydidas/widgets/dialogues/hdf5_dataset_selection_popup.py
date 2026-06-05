# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["Hdf5DatasetSelectionPopup"]


from pathlib import Path
from typing import Sequence

from qtpy import QtWidgets

from pydidas.core import Hdf5key, NXdataKey, UserConfigError
from pydidas.core.utils.hdf5 import get_hdf5_populated_dataset_keys
from pydidas.widgets.utilities import (
    get_max_pixel_width_of_entries,
    get_pyqt_icon_from_str,
)
from pydidas_qtcore import PydidasQApplication


class Hdf5DatasetSelectionPopup(QtWidgets.QInputDialog):
    """
    A dialogue for showing a pop-up dialogue to select a dataset from a
    hdf5 file.

    Parameters
    ----------
    parent : QWidget or None, optional
        The parent widget. The default is None.
    fname : Path or str or None, optional
        The file path to the hdf5 file. The default is None.
    nxdata_signal_only : bool, optional
        Flag whether to show only the NxData entries. The default is False.
    min_dim : int, optional
        The minimum dimension of the datasets to be shown. The default is 1.
    """

    def __init__(
        self,
        parent: QtWidgets.QWidget | None = None,
        fname: None | Path | str = None,
        nxdata_signal_only: bool = False,
        min_dim: int = 1,
    ) -> None:
        QtWidgets.QInputDialog.__init__(self, parent)
        self.__nxdata_signal_only = nxdata_signal_only
        self.__min_dim = min_dim
        self.setWindowTitle("Select hdf5 dataset")
        self.setWindowIcon(get_pyqt_icon_from_str("qt-std::SP_FileDialogListView"))
        self.setLabelText("Hdf5 datasets:")
        if fname is not None:
            self.set_filename(fname)

    def set_filename(self, fname: Path | str) -> None:
        """
        Set the filename for the Hdf5 file.

        Parameters
        ----------
        fname : Path or str
            The full path to the Hdf5 file.
        """
        if not isinstance(fname, Path):
            fname = Path(fname)
        if not fname.is_file():
            raise UserConfigError(
                f"The selected file `{fname}` is not a valid file, for example "
                "the filename is misspelled and the file does not exist. Please "
                "select a valid hdf5 file."
            )
        dsets = get_hdf5_populated_dataset_keys(
            fname, min_dim=self.__min_dim, nxdata_signal_only=self.__nxdata_signal_only
        )
        self.__update_combo_box_items(dsets)

    def __update_combo_box_items(self, items: Sequence[str]) -> None:
        """
        Update the ComboBox entries with new items.

        Parameters
        ----------
        items : Sequence[str]
            The items which are to be displayed. This must be an iterable
            of string items.
        """
        _font_height = PydidasQApplication.instance().font_height
        self.setOption(QtWidgets.QInputDialog.UseListViewForComboBoxItems, True)
        self.setComboBoxItems(items)

        _width = get_max_pixel_width_of_entries(items) + 60
        _basic_height = 5 * _font_height
        _listview = self.findChild(QtWidgets.QListView)
        if not _listview or len(items) < 1:
            _list_height = _font_height + 5
        else:
            _row_height = _listview.sizeHintForRow(0)
            _list_height = _row_height * min(10, 1 + len(items))
        self.resize(_width, _list_height + _basic_height)

    def get_dset(self) -> Hdf5key | NXdataKey | None:
        """
        Show the QInputDialog and return the selected Hdf5key.

        Returns
        -------
        Hdf5key or NXdataKey or None
            If the dialogue is accepted, returns the selected Hdf5key.
            If it is aborted, it will return None.
        """
        if self.exec_() == QtWidgets.QDialog.Accepted:
            if self.__nxdata_signal_only:
                return NXdataKey(self.textValue())
            return Hdf5key(self.textValue())
        return None

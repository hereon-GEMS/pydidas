# This file is part of pydidas.
#
# Copyright 2025, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ItemInListSelectionWidget"]


from collections.abc import Iterable
from typing import Optional

from qtpy import QtWidgets

from pydidas.widgets.utilities import (
    get_max_pixel_width_of_entries,
    get_pyqt_icon_from_str,
)


class ItemInListSelectionWidget(QtWidgets.QInputDialog):
    """
    A dialogue for showing a pop-up dialogue to select an item from a list.

    Parameters
    ----------
    options : list[str]
        The list of options to select from.
    parent : QWidget, optional
        The parent widget. If None, the dialogue will be a top-level window.
    """

    def __init__(
        self,
        options: list[str],
        parent: Optional[QtWidgets.QWidget] = None,
        title="Select item",
        label="Items:",
    ):
        QtWidgets.QInputDialog.__init__(self, parent)
        self.__update_combo_box_items(options)
        self.setWindowTitle(title)
        self.setWindowIcon(get_pyqt_icon_from_str("qt-std::SP_FileDialogListView"))
        self.setLabelText(label)

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
            min(20 * _font_height, (len(items) + 5) * (_font_height + 5)),
        )
        print((20 * _font_height, (len(items) + 5) * (_font_height + 5)))
        self.setOption(QtWidgets.QInputDialog.UseListViewForComboBoxItems, True)
        self.setComboBoxItems(items)

    def get_item(self) -> Optional[str]:
        """
        Show the QInputDialog and get the selected item.

        Returns
        -------
        Union[Hdf5key, None]
            If the dialogue is accepted, returns the selected item.
            If it is aborted, it will return None.
        """
        if self.exec_() == QtWidgets.QDialog.Accepted:
            return self.textValue()

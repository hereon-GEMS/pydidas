# This file is part of pydidas.
#
# Copyright 2025 - 2026, Helmholtz-Zentrum Hereon
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
Module with SelectItemInListDialog class which shows a pop-up to select
an item from a list of options.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["SelectItemInListDialog"]


from collections.abc import Iterable

from qtpy import QtWidgets

from pydidas.widgets.utilities import (
    get_max_pixel_width_of_entries,
    get_pyqt_icon_from_str,
)


class SelectItemInListDialog(QtWidgets.QInputDialog):
    """
    A dialogue for showing a pop-up dialogue to select an item from a list.

    Parameters
    ----------
    options : list[str]
        The list of options to select from.
    parent : QtWidgets.QWidget or None, optional
        The parent widget. If None, the dialogue will be a top-level window.
    title : str, optional
        The dialogue's window title. The default is "Select item".
    label : str, optional
        The label text shown above the combo box. The default is "Items:".
    """

    def __init__(
        self,
        options: list[str],
        parent: QtWidgets.QWidget | None = None,
        title: str = "Select item",
        label: str = "Items:",
    ) -> None:
        QtWidgets.QInputDialog.__init__(self, parent)
        self.__update_combo_box_items(options)
        self.setWindowTitle(title)
        self.setWindowIcon(get_pyqt_icon_from_str("qt-std::SP_FileDialogListView"))
        self.setLabelText(label)

    def __update_combo_box_items(self, items: Iterable[str]) -> None:
        """
        Update the ComboBox entries with new items.

        Parameters
        ----------
        items : Iterable[str]
            The items which are to be displayed. This must be an iterable
            of string items.
        """
        _font_height = QtWidgets.QApplication.instance().font_height
        self.resize(
            get_max_pixel_width_of_entries(items) + 60,
            min(20 * _font_height, (len(items) + 5) * (_font_height + 5)),
        )
        self.setOption(QtWidgets.QInputDialog.UseListViewForComboBoxItems, True)
        self.setComboBoxItems(items)

    def get_item(self) -> str | None:
        """
        Show the QInputDialog and get the selected item.

        Returns
        -------
        str or None
            If the dialogue is accepted, returns the selected item.
            If it is aborted, it will return None.
        """
        if self.exec_() == QtWidgets.QDialog.Accepted:
            return self.textValue()

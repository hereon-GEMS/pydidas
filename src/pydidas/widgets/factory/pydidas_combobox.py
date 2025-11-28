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
The PydidasComboBox is a QComboBox with automatic font and width formatting.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasComboBox"]


from typing import Any

from qtpy import QtCore
from qtpy.QtWidgets import QComboBox

from pydidas.core.constants import GENERIC_IO_WIDGET_WIDTH
from pydidas.widgets.factory.pydidas_widget_mixin import PydidasWidgetMixin
from pydidas.widgets.utilities import get_max_pixel_width_of_entries


class PydidasComboBox(PydidasWidgetMixin, QComboBox):
    """
    Create a QComboBox with automatic font formatting.

    This Combobox overwrites the default sizeHint to take as much space
    (up to the generic IO widget width) to fill the layout.
    """

    init_kwargs = PydidasWidgetMixin.init_kwargs + ["items"]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the PydidasComboBox.

        Parameters
        ----------
        *args : Any
            Positional arguments for QComboBox.
        **kwargs : Any
            Keyword arguments for font formatting and widget initialization.
        """
        self.__sizeHint = QtCore.QSize(GENERIC_IO_WIDGET_WIDTH, 5)
        QComboBox.__init__(self, *args)
        _items = kwargs.pop("items", None)
        if isinstance(_items, list) and _items:
            self.insertItems(0, _items)
        if "font_metric_height_factor" not in kwargs:
            kwargs["font_metric_height_factor"] = 1
        PydidasWidgetMixin.__init__(self, **kwargs)

    def _update_view_width(self) -> None:
        """
        Update the view width of the combobox.

        This method assures that the combobox is resized to the maximum
        width of the entries and that all entries are always legible.
        """
        _items = [self.itemText(i) for i in range(self.count())]
        if _items:
            self.view().setMinimumWidth(get_max_pixel_width_of_entries(_items) + 50)

    def addItem(self, text: str, userData: Any = None) -> None:  # noqa ARG002
        super().addItem(text, userData)
        self._update_view_width()

    def addItems(self, texts: list[str]) -> None:
        super().addItems(texts)
        self._update_view_width()

    def insertItem(self, index: int, text: str, userData: Any = None) -> None:  # noqa ARG002
        super().insertItem(index, text, userData)
        self._update_view_width()

    def insertItems(self, index: int, texts: list[str]) -> None:
        super().insertItems(index, texts)
        self._update_view_width()

    def removeItem(self, index: int) -> None:
        super().removeItem(index)
        self._update_view_width()

    def clear(self) -> None:
        super().clear()
        self._update_view_width()

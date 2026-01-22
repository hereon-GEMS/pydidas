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
Module with the EmptyWidget, a QWidget with font-metric scaling and a QGridLayout.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["EmptyWidget"]


from typing import Any

from qtpy import QtWidgets
from qtpy.QtWidgets import QGridLayout, QWidget

from pydidas.widgets.factory.pydidas_widget_mixin import PydidasWidgetMixin


class EmptyWidget(PydidasWidgetMixin, QWidget):
    """
    Create an empty widget with a QGridLayout.

    The constructor also sets QProperties based on the supplied keywords, if
    a matching setter was found.
    """

    init_kwargs = PydidasWidgetMixin.init_kwargs + ["layout_column_stretches"]

    def __init__(self, parent: QtWidgets.QWidget | None = None, **kwargs: Any) -> None:
        """
        Initialize the EmptyWidget.

        Parameters
        ----------
        kwargs : Any
            Keyword arguments for widget initialization and layout properties.
        """
        QWidget.__init__(self, parent)
        self.setLayout(QGridLayout())
        PydidasWidgetMixin.__init__(self, **kwargs)
        if "layout_column_stretches" in kwargs:
            for _key, _val in kwargs.get("layout_column_stretches").items():
                self.layout().setColumnStretch(_key, _val)

    def layout(self) -> QGridLayout:
        """
        Return the layout

        This method only updates the return type because the EmptyWidget
        layout is always a QGridLayout.
        """
        return super().layout()  # type: ignore[return-value]

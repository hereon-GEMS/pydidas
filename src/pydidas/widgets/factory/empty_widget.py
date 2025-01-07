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
Module with the EmptyWidget, a QWidget with font-metric scaling and a QGridLayout.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["EmptyWidget"]


from qtpy.QtWidgets import QGridLayout, QWidget

from pydidas.core.constants import ALIGN_TOP_LEFT
from pydidas.core.utils import apply_qt_properties
from pydidas.widgets.factory.pydidas_widget_mixin import PydidasWidgetMixin


class EmptyWidget(PydidasWidgetMixin, QWidget):
    """
    Create an empty widget with a QGridLayout.

    The constructor also sets QProperties based on the supplied keywords, if
    a matching setter was found.
    """

    init_kwargs = PydidasWidgetMixin.init_kwargs[:] + [
        "init_layout",
        "layout_column_stretches",
    ]

    def __init__(self, **kwargs: dict):
        QWidget.__init__(self)
        PydidasWidgetMixin.__init__(self, **kwargs)
        if kwargs.get("init_layout", True):
            self.setLayout(QGridLayout())
            apply_qt_properties(
                self.layout(),
                contentsMargins=(0, 0, 0, 0),
                alignment=ALIGN_TOP_LEFT,
            )
        if "layout_column_stretches" in kwargs:
            for _key, _val in kwargs.get("layout_column_stretches").items():
                self.layout().setColumnStretch(_key, _val)

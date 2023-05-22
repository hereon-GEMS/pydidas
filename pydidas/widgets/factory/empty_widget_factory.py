# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
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
Module with a factory function to create an empty QWidget.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["create_empty_widget"]


from qtpy.QtWidgets import QGridLayout, QWidget

from ...core.constants import ALIGN_TOP_LEFT
from ...core.utils import apply_qt_properties


def create_empty_widget(**kwargs):
    """
    Create a button.

    Parameters
    ----------
    **kwargs : dict
        Any additional keyword arguments. See below for supported arguments.
    **QtAttribute : depends on the attribute
        Any Qt attributes which are supported by the QWidget. Use the Qt
        attribute name with a lowercase first character. Examples are
        ``fixedWidth``, ``visible``.

    Returns
    -------
    empty_widget : QtWidgets.QWidget
        The instantiated QWidget.
    """
    _widget = QWidget()
    init_layout = kwargs.get("init_layout", True)
    apply_qt_properties(_widget, **kwargs)
    if init_layout:
        _widget.setLayout(QGridLayout())
        apply_qt_properties(
            _widget.layout(),
            contentsMargins=(0, 0, 0, 0),
            alignment=ALIGN_TOP_LEFT,
        )
    return _widget

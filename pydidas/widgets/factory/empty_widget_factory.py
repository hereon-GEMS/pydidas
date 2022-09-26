# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
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
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["create_empty_widget"]

from qtpy.QtWidgets import QWidget, QGridLayout

from ...core.constants import QT_DEFAULT_ALIGNMENT
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
            alignment=QT_DEFAULT_ALIGNMENT,
        )
    return _widget

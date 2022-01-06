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
Module with a factory function to create a QComboBox.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['create_combo_box']

from PyQt5.QtWidgets import QComboBox

from ..utilities import apply_widget_properties


def create_combo_box(**kwargs):
    """
    Create a QcomboBox widget.

    This method creates a combo box and adds it to the parent widget.

    Parameters
    ----------
    **kwargs : dict
        Any additional keyword arguments. See below for supported
        arguments.
    **QtAttribute : depends on the attribute
        Any Qt attributes which are supported by the QComboBox. Use the Qt
        attribute name with a lowercase first character. Examples are
        ``fixedWidth``, ``visible``, ``enabled``.

    Returns
    -------
    box : QComboBox
        The line (in the form of a QFrame widget).
    """
    _box = QComboBox()
    apply_widget_properties(_box, **kwargs)
    return _box

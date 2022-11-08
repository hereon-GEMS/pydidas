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
Module with a factory function to create a QPushButton.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["create_button"]

from qtpy.QtWidgets import QPushButton

from ...core.utils import apply_qt_properties
from ..utilities import get_pyqt_icon_from_str


def create_button(text, **kwargs):
    """
    Create a button.

    Parameters
    ----------
    text : str
        The button text.
    **kwargs : dict
        Any additional keyword arguments. See below for supported arguments.
    **QtAttribute : depends on the attribute
        Any Qt attributes which are supported by the QPushButton. Use the Qt
        attribute name with a lowercase first character. Examples are
        ``icon``, ``fixedWidth``, ``visible``, ``enabled``.


    Returns
    -------
    button : QtWidgets.QPushButton
        The instantiated button widget.
    """
    _button = QPushButton(text)
    if isinstance(kwargs.get("icon", None), str):
        kwargs["icon"] = get_pyqt_icon_from_str(kwargs.get("icon"))
    apply_qt_properties(_button, **kwargs)
    return _button

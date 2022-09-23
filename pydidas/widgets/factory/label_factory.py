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
Module with a factory function to create formatted QLabels.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["create_label"]

from qtpy.QtWidgets import QLabel, QApplication
from qtpy.QtGui import QFont

from ..utilities import apply_widget_properties, apply_font_properties


def create_label(text, **kwargs):
    """
    This method will create a label with text.

    Parameters
    ----------
    text : str
        The label text to be printed.
    **kwargs : dict
        Any aditional keyword arguments. See below for supported
        arguments.
    **fontsize : int, optional
        The font size in pixels. The default is STANDARD_FONT_SIZE.
    **QtAttribute : depends on the attribute
        Any Qt attributes are supported by the QLabel. Use the Qt attribute
        name with a lowercase first character. Examples are
        ``fixedWidth``, ``visible``, ``enabled``.

    Returns
    -------
    label : QLabel
        The formatted QLabel
    """
    _label = QLabel(text)

    kwargs["wordWrap"] = kwargs.get("wordWrap", True)
    if not isinstance(kwargs.get("font", None), QFont):
        kwargs["font"] = QApplication.font()

    apply_font_properties(kwargs["font"], **kwargs)
    apply_widget_properties(_label, **kwargs)
    return _label

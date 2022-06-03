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
Module with a factory function to create a QLineEdit.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["create_lineedit"]

from qtpy.QtWidgets import QLineEdit, QApplication

from ...core.constants import STANDARD_FONT_SIZE
from ..utilities import apply_widget_properties, apply_font_properties


def create_lineedit(**kwargs):
    """
    Create a QLineEdit widget.

    Parameters
    ----------
    **kwargs : dict
        Any additional keyword arguments. See below for supported
        arguments.
    **QtAttribute : depends on the attribute
        Any Qt attributes which are supported by the QWidget. Use the Qt
        attribute name with a lowercase first character. Examples are
        ``fixedWidth``, ``fixedHeight``.

    Returns
    -------
    line : QFrame
        The line (in the form of a QFrame widget).
    """
    _lineedit = QLineEdit(kwargs.get("text", ""))

    kwargs["pointSize"] = kwargs.get("fontsize", STANDARD_FONT_SIZE)
    kwargs["wordWrap"] = kwargs.get("wordWrap", True)

    if QApplication.instance() is not None:
        kwargs["font"] = QApplication.font()
        apply_font_properties(kwargs["font"], **kwargs)

    apply_widget_properties(_lineedit, **kwargs)
    return _lineedit

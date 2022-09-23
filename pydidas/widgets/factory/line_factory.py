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
Module with a factory function to create formatted lines, implemented as a
flat QFrame.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["create_line"]

from qtpy.QtWidgets import QFrame

from ...core.utils import apply_qt_properties


def create_line(**kwargs):
    """
    Create a line widget.

    This method creates a line widget as separator and adds it to the
    parent widget.

    Parameters
    ----------
    **kwargs : dict
        Any additional keyword arguments. See below for supported
        arguments.
    **QtAttribute : depends on the attribute
        Any Qt attributes which are supported by the QFrame. Use the Qt
        attribute name with a lowercase first character. Examples are
        ``lineWidth``, ``fixedWidth``, ``fixedHeight``.


    Returns
    -------
    line : QFrame
        The line (in the form of a QFrame widget).
    """
    _line = QFrame()
    kwargs["frameShape"] = kwargs.get("frameShape", QFrame.HLine)
    kwargs["frameShadow"] = kwargs.get("frameShadow", QFrame.Sunken)
    kwargs["lineWidth"] = kwargs.get("lineWidth", 2)
    kwargs["fixedHeight"] = kwargs.get("fixedHeight", 3)
    apply_qt_properties(_line, **kwargs)
    return _line

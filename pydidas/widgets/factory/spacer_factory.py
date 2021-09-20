# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with a factory function to create formatted lines as a formatted
QFrame."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['create_spacer']

from PyQt5.QtWidgets import QSpacerItem, QSizePolicy

from ..utilities import apply_widget_properties


def create_spacer(**kwargs):
    """
    Create a spacer item.

    A QSpacerItem will be created. Its size policy is "Minimal" unless
    overridden.

    Parameters
    ----------
    height : int, optional
        The height of the spacer in pixel. The default is 20.
    width : int, optional
        The width of the spacer in pixel. The default is 20.
    policy : QtWidgets.QSizePolicy, optional
        The size policy for the spacer (applied both horizontally and
        vertically). The default is QtWidgets.QSizePolicy.Minimum.

    Returns
    -------
    spacer : QSpacerItem
        The new spacer.
    """
    _policy = kwargs.get('policy', QSizePolicy.Minimum)
    _spacer = QSpacerItem(kwargs.get('fixedHeight', 20),
                          kwargs.get('fixedWidth', 20), _policy, _policy)

    apply_widget_properties(_spacer, **kwargs)
    return _spacer

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
Module with the MainWindow class which is a subclassed QMainWindow which has
been modified for pydidas's requirements and which manages the option and
selection bars.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['configure_qtapp_namespace', 'get_pydidas_icon',
           'update_qtapp_font_size', 'apply_tooltop_event_filter']

import os

from qtpy import QtWidgets, QtGui

from ...core.constants import STANDARD_FONT_SIZE
from .qtooltip_event_handler import QTooltipEventFilter


def configure_qtapp_namespace():
    """
    Set the QApplication organization and application names.
    """
    app = QtWidgets.QApplication.instance()
    app.setOrganizationName("Hereon")
    app.setOrganizationDomain("Hereon/WPI")
    app.setApplicationName("pydidas")


def get_pydidas_icon():
    """
    Get the pydidas icon.

    Returns
    -------
    _icon : QtGui.QIcon
        The instantiated pydidas icon.
    """
    _path = __file__
    for _ in range(2):
        _path = os.path.dirname(_path)
    _logopath = os.path.join(_path, 'icons', 'pydidas_logo.svg')
    _icon= QtGui.QIcon(_logopath)
    return _icon


def find_toolbar_bases(items):
    """
    Find the bases of all toolbar items which are not included in the items
    itself.

    Base levels in items are separated by forward slashes.

    Parameters
    ----------
    items : Union[list, tuple]
        An iterable of string items.

    Example
    -------
    >>> items = ['a', 'a/b', 'a/c', 'b', 'd/e']
    >>> _find_toolbar_bases(items)
    ['', 'a', 'd']

    The '' entry is the root for all top-level items. Even though 'a' is an
    item itself, it is also a parent for 'a/b' and 'a/c' and it is therefore
    also included in the list, similar to 'd'.

    Returns
    -------
    itembases : list
        A list with string entries of all the items' parents.
    """
    _itembases = []
    for _item in items:
        _parent = os.path.dirname(_item)
        if _parent not in _itembases:
            _itembases.append(_parent)
        _item = _parent
    _itembases.sort()
    return _itembases


def update_qtapp_font_size():
    """
    Update the standard fonz size in the QApplication with the font size
    defined in pydidas.
    """
    _app = QtWidgets.QApplication.instance()
    _font = _app.font()
    _font.setPointSize(STANDARD_FONT_SIZE)
    _app.setFont(_font)


def apply_tooltop_event_filter():
    """
    Apply the pydidas.core.utils.QTooltipEventFilter to the QApplication
    to force the desired handling of tooltip.
    """
    _app = QtWidgets.QApplication.instance()
    _app.installEventFilter(QTooltipEventFilter(_app))

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
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['get_and_store_widget_states']


from qtpy import QtCore, QtWidgets


def get_visibilities_of_children(widget):
    """
    Get the visibilities of all children of the argument widget.

    Parameters
    ----------
    widget : WtWidgets.QWidget
        The widget whose

    Returns
    -------
    visibility_keys : list
        A list with a boolean flag entry for every child widget.

    """
    _args = (QtWidgets.QWidget, '',  QtCore.Qt.FindChildrenRecursively)
    visibility_keys = [_widget.isVisible()
                       for _widget in widget.findChildren(*_args)]
    return visibility_keys



def get_and_store_widget_states(central_widget):
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
    _widget_state = {}
    for _index, _widget in enumerate(central_widget.widgets):
        _vis = get_visibilities_of_children(_widget)
        _params = _widget.get_param_values_as_dict()
        _widget_state[_index] = {'params': _params, 'visibility': _vis}
    return _widget_state

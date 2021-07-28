# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""
Module with the CreateWidgetsMixIn class which can be inherited from to
add convenience widget creation methods.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['CreateWidgetsMixIn']

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QBoxLayout, QGridLayout, QStackedLayout

from .factory import (create_spin_box, create_progress_bar, create_check_box,
                      create_label, create_line, create_spacer, create_button)
from ..config import DEFAULT_ALIGNMENT
from .._exceptions import WidgetLayoutError
from ..utils import copy_docstring


class CreateWidgetsMixIn:
    """
    The CreateWidgetsMixIn class includes methods for easy adding of widgets
    to the layout. The create_something methods from the factories are called
    and in addition, the layout and positions can be set.

    Use the "gridPos" keyword to define the widget position in the parent's
    layout.
    """
    def __init__(self):
        self._widgets = {}

    @copy_docstring(create_spacer)
    def create_spacer(self, **kwargs):
        """
        Please refer to pydidas.widgets.factory.create_spacer
        """
        _parent = kwargs.get('parent_widget', self)
        _spacer = create_spacer(**kwargs)
        _layout_args = _get_widget_layout_args(_parent, **kwargs)
        _parent.layout().addItem(_spacer, *_layout_args)
        return _spacer

    @copy_docstring(create_label)
    def create_label(self, text, **kwargs):
        """
        Please refer to pydidas.widgets.factory.create_label
        """
        return self.__create_widget(create_label, text, **kwargs)

    @copy_docstring(create_line)
    def create_line(self, **kwargs):
        """
        Please refer to pydidas.widgets.factory.create_line
        """
        return self.__create_widget(create_line, **kwargs)

    @copy_docstring(create_button)
    def create_button(self, text, **kwargs):
        """
        Please refer to pydidas.widgets.factory.create_button
        """
        return self.__create_widget(create_button, text, **kwargs)

    @copy_docstring(create_spin_box)
    def create_spin_box(self, **kwargs):
        """
        Please refer to pydidas.widgets.factory.create_spin_box
        """
        return self.__create_widget(create_spin_box, **kwargs)

    @copy_docstring(create_progress_bar)
    def create_progress_bar(self, **kwargs):
        """
        Please refer to pydidas.widgets.factory.create_progress_bar
        """
        return self.__create_widget(create_progress_bar, **kwargs)

    @copy_docstring(create_check_box)
    def create_check_box(self, text, **kwargs):
        """
        Please refer to pydidas.widgets.factory.create_check_box
        """
        return self.__create_widget(create_check_box, text, **kwargs)

    def __create_widget(self, method, *args, **kwargs):
        """
        Create

        Parameters
        ----------
        method : method
            The method to be called.
        *args : args
            Any arguments to the method call
        **kwargs : dict
            keyword arguments.
        """
        _parent = kwargs.get('parent_widget', self)
        _widget = method(*args, **kwargs)
        _layout_args = _get_widget_layout_args(_parent, **kwargs)
        _parent.layout().addWidget(_widget, *_layout_args)
        return _widget


def _get_widget_layout_args(parent, **kwargs):
    """
    Get the arguments for adding a widget to the layout.

    Parameters
    ----------
    parent : QWidget
        The parent QWidget to be added to the layout.
    **kwargs : dict
        The keyword arguments dictionary from the calling method. This
        method only takes the "gridPos" and "alignment" arguments from the
        kwargs.

    Raises
    ------
    WidgetLayoutError
        If the parent widget has no supported layout. Supported are
        QBoxLayout, QStackedLayout or QGridLayout and subclasses.

    Returns
    -------
    list
        The list of layout arguments required for adding the widget to
        the layout of the parent widget.
    """
    if not isinstance(
            parent.layout(),(QBoxLayout, QStackedLayout, QGridLayout)):
        raise WidgetLayoutError(
            f'Layout of parent widget "{parent}" is not of type '
            'QBoxLayout, QStackedLayout or QGridLayout.')

    _alignment = kwargs.get('alignment', DEFAULT_ALIGNMENT)
    if isinstance(parent.layout(), QtWidgets.QBoxLayout):
        return [kwargs.get('stretch', 0), _alignment]
    if isinstance(parent.layout(), QtWidgets.QStackedLayout):
        return []

    _grid_pos = _get_grid_pos(parent, **kwargs)
    if _alignment is not None:
        return [*_grid_pos, _alignment]
    return [*_grid_pos]


def _get_grid_pos(parent, **kwargs):
    """
    Get the gridPos format from the kwargs or create it.

    Parameters
    ----------
    parent : QWidget
        The parent QWidget to be added to the layout.
    **kwargs : dict
        The keyword arguments dictionary from the calling method. This
        method only takes the "gridPos" and "alignment" arguments from the
        kwargs.

    Raises
    ------
    WidgetLayoutError
        If gridPos has been specified but is not of type tuple and not of
        length 4.

    Returns
    -------
    gridPos : tuple
        The 4-tuple of the gridPos.
    """
    _grid_pos = kwargs.get('gridPos', None)
    _default_row = (0 if parent.layout().count() == 0
                    else parent.layout().rowCount())

    if _grid_pos is None:
        _grid_pos = (kwargs.get('row', _default_row),
                     kwargs.get('column', 0),
                     kwargs.get('n_rows', 1),
                     kwargs.get('n_columns', 2))

    if not (isinstance(_grid_pos, tuple) and len(_grid_pos) == 4):
        raise WidgetLayoutError(
            'The passed value for "gridPos" is not of type tuple and/or not'
            ' of length 4.')

    if _grid_pos[0] == -1:
        _grid_pos = (_default_row, ) + _grid_pos[1:4]
    return _grid_pos

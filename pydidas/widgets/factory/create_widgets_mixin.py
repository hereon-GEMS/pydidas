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
Module with the CreateWidgetsMixIn class which can be inherited from to
add convenience widget creation methods.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['CreateWidgetsMixIn']

from qtpy import QtWidgets
from qtpy.QtWidgets import QBoxLayout, QGridLayout, QStackedLayout

from ...core import WidgetLayoutError
from ...core.utils import copy_docstring
from ..utilities import apply_widget_properties
from .button_factory import create_button
from .check_box_factory import create_check_box
from .combobox_factory import create_combo_box
from .label_factory import create_label
from .line_factory import create_line
from .progress_bar_factory import create_progress_bar
from .radio_button_group_factory import create_radio_button_group
from .spacer_factory import create_spacer
from .spin_box_factory import create_spin_box


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
        self.__index_unreferenced = 0

    @copy_docstring(create_spacer)
    def create_spacer(self, ref, **kwargs):
        """
        Please refer to pydidas.widgets.factory.create_spacer
        """
        _parent = kwargs.get('parent_widget', self)
        _spacer = create_spacer(**kwargs)
        _layout_args = _get_widget_layout_args(_parent, **kwargs)
        _parent.layout().addItem(_spacer, *_layout_args)
        if ref is None:
            ref = f'unreferenced_{self.__index_unreferenced:03d}'
            self.__index_unreferenced += 1
        self._widgets[ref] = _spacer

    @copy_docstring(create_label)
    def create_label(self, ref, text, **kwargs):
        """
        Please refer to pydidas.widgets.factory.create_label
        """
        self.__create_widget(create_label, ref, text, **kwargs)

    @copy_docstring(create_line)
    def create_line(self, ref, **kwargs):
        """
        Please refer to pydidas.widgets.factory.create_line
        """
        self.__create_widget(create_line, ref, **kwargs)

    @copy_docstring(create_button)
    def create_button(self, ref, text, **kwargs):
        """
        Please refer to pydidas.widgets.factory.create_button
        """
        self.__create_widget(create_button, ref, text, **kwargs)

    @copy_docstring(create_spin_box)
    def create_spin_box(self, ref, **kwargs):
        """
        Please refer to pydidas.widgets.factory.create_spin_box
        """
        self.__create_widget(create_spin_box, ref, **kwargs)

    @copy_docstring(create_progress_bar)
    def create_progress_bar(self, ref, **kwargs):
        """
        Please refer to pydidas.widgets.factory.create_progress_bar
        """
        self.__create_widget(create_progress_bar, ref, **kwargs)

    @copy_docstring(create_check_box)
    def create_check_box(self, ref, text, **kwargs):
        """
        Please refer to pydidas.widgets.factory.create_check_box
        """
        self.__create_widget(create_check_box, ref, text, **kwargs)

    @copy_docstring(create_combo_box)
    def create_combo_box(self, ref, **kwargs):
        """
        Please refer to pydidas.widgets.factory.create_check_box
        """
        self.__create_widget(create_combo_box, ref, **kwargs)

    @copy_docstring(create_radio_button_group)
    def create_radio_button_group(self, ref, entries, vertical=True, **kwargs):
        """
        Please refer to pydidas.widgets.factory.create_radio_button_group
        """
        self.__create_widget(create_radio_button_group, ref, entries,
                             vertical=vertical, **kwargs)

    def __create_widget(self, object_, ref, *args, **kwargs):
        """
        Create a widget from a object (function / class).

        Parameters
        ----------
        object : object
            The object to be called.
        ref : str
            The reference name in the _widgets dictionary.
        *args : args
            Any arguments to the object call.
        **kwargs : dict
            Keyword arguments for the widget creation.
        """
        _parent = kwargs.get('parent_widget', self)
        _widget = object_(*args, **kwargs)
        if isinstance(kwargs.get('layout_kwargs'), dict):
            kwargs.update(kwargs.get('layout_kwargs'))
            del kwargs['layout_kwargs']
        _layout_kwargs = dict(alignment=kwargs.get('alignment', None),
                              gridPos=kwargs.get('gridPos', None))
        _layout_args = _get_widget_layout_args(_parent, **_layout_kwargs)
        _parent.layout().addWidget(_widget, *_layout_args)
        if ref is None:
            ref = f'unreferenced_{self.__index_unreferenced:03d}'
            self.__index_unreferenced += 1
        self._widgets[ref] = _widget

    def create_any_widget(self, ref, widget_class, *args, **kwargs):
        """
        Create any widget with any settings and add it to the layout.

        Note
        ----
        Widgets must support generic args and kwargs arguments. This means
        that generic PyQt widgets cannot be created using this method. They
        can be added, however, using the ``add_any_widget`` method.

        Parameters
        ----------
        ref : str
            The reference name in the _widgets dictionary.
        widget_class : QtWidgets.QWidget
            The class of the widget.
        *args : args
            Any arguments for the widget creation.
        **kwargs : dict
            Keyword arguments for the widget creation.

        Raises
        ------
        TypeError
            If the reference "ref" is not of type string.
        """
        if not isinstance(ref, str):
            raise TypeError('Widget reference must be of type string.')
        self.__create_widget(widget_class, ref, *args, **kwargs)
        apply_widget_properties(self._widgets[ref], **kwargs)

    def add_any_widget(self, ref, widget, **kwargs):
        """
        Add any existing widget with any settings to the layout.

        Note
        ----
        This method can also be used to add a new widget to the layout
        be simply creating an instance of the widget in the call
        (see examples).

        Parameters
        ----------
        ref : str
            The reference name in the _widgets dictionary.
        widget : QtWidgets.QWidget
            The widget instance.
        **kwargs : dict
            Keyword arguments for the widget settings and layout.
        **layout_args : dict
            Any keyword arguments which should be passed to the layout
            arguments but not to the widget creation. This is important
            for an "alignment=None" flag which cannot be passed to the
            widget creation.

        Example
        -------
        To add a new widget, in this example a QLabel without any alignment
        and with a width of 600 pixel, create a new instance on the fly and
        add it to the object:

        >>> object.add_any_widget('new_label', QLabel(), width=600,
                                  layout_args={'alignment': None})

        Raises
        ------
        TypeError
            If the reference "ref" is not of type string.
        """
        if not isinstance(ref, str):
            raise TypeError('Widget reference must be of type string.')
        apply_widget_properties(widget, **kwargs)
        _parent = kwargs.get('parent_widget', self)
        if isinstance(kwargs.get('layout_kwargs'), dict):
            kwargs.update(kwargs.get('layout_kwargs'))
            del kwargs['layout_kwargs']
        _layout_args = _get_widget_layout_args(_parent, **kwargs)
        _parent.layout().addWidget(widget, *_layout_args)
        if ref is not None:
            self._widgets[ref] = widget


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
            parent.layout(), (QBoxLayout, QStackedLayout, QGridLayout)):
        raise WidgetLayoutError(
            f'Layout of parent widget "{parent}" is not of type '
            'QBoxLayout, QStackedLayout or QGridLayout.')

    # TODO: Verify alignment
    # _alignment = kwargs.get('alignment', DEFAULT_ALIGNMENT)
    _alignment = kwargs.get('alignment', None)
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
                     kwargs.get('n_columns', 1))
    if not (isinstance(_grid_pos, tuple) and len(_grid_pos) == 4):
        raise WidgetLayoutError(
            'The passed value for "gridPos" is not of type tuple and/or not'
            ' of length 4.')
    if _grid_pos[0] == -1:
        _grid_pos = (_default_row, ) + _grid_pos[1:4]
    return _grid_pos

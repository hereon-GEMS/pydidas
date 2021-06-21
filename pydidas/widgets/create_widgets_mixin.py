# MIT License
#
# Copyright (c) 2021 Malte Storm, Helmholtz-Zentrum Hereon.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Module with the CreateWidgetsMixIn class which can be inherited from to
add convenience widget creation methods.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['CreateWidgetsMixIn']

from PyQt5 import QtWidgets

from .factory import create_spin_box
from .utilities import apply_widget_properties, apply_font_properties
from ..config import STANDARD_FONT_SIZE, DEFAULT_ALIGNMENT
from .._exceptions import WidgetLayoutError


class CreateWidgetsMixIn:
    """
    The CreateWidgetsMixIn class includes methods for easy
    classes without having to inherit from ParamConfig to avoid multiple
    inheritance from QtWidgets.QFrame.
    """

    def create_label(self, text, **kwargs):
        """
        Add a label to the widget.

        This method will add a label with text to the widget. Useful for
        defining item groups etc.

        Parameters
        ----------
        text : str
            The label text to be printed.
        fontsize : int, optional
            The font size in pixels. The default is STANDARD_FONT_SIZE.
        **kwargs : dict
            Any aditional keyword arguments. See below for supported
            arguments.

        Supported keyword arguments
        ---------------------------
        gridPos : Union[list, tuple, None], optional
            The position in the QGridLayout
        parent_widget : Union[QWidget, None], optional
            The parent widget to which the label is added. If None, this
            defaults to the calling widget, ie. "self".
        *Qt settings : any
            Any Qt settings

        Returns
        -------
        label : QLabel
            The formatted QLabel
        """
        kwargs['pointSize'] = kwargs.get('fontsize', STANDARD_FONT_SIZE)
        kwargs['font'] = QtWidgets.QApplication.font()
        apply_font_properties(kwargs['font'], **kwargs)

        _parent = kwargs.get('parent_widget', self)
        _label = QtWidgets.QLabel(text)
        # TODO : verify the heights of text widgets
        # _h = _label.fontMetrics().boundingRect(_label.text()).height()
        # print(_h, text)
        # kwargs['fixedHeight'] = (kwargs['pointSize'] * (1 + text.count('\n'))
        #                          + 10)
        kwargs['wordWrap'] = kwargs.get('wordWrap', True)

        apply_widget_properties(_label, **kwargs)

        _layout_args = _get_widget_layout_args(_parent, **kwargs)
        _parent.layout().addWidget(_label, *_layout_args)
        return _label

    def create_line(self, **kwargs):
        """
        Create a line widget.

        This method creates a line widget as separator and adds it to the
        parent widget.

        Parameters
        ----------
        **kwargs : dict
            Any aditional keyword arguments. See below for supported
            arguments.

        Supported keyword arguments
        ---------------------------
        gridPos : Union[list, tuple, None], optional
            The position in the QGridLayout
        parent_widget : Union[QWidget, None], optional
            The parent widget to which the label is added. If None, this
            defaults to the calling widget, ie. "self".
        *Qt settings : any

        Returns
        -------
        line : QFrame
            The line (in the form of a QFrame widget).
        """
        _parent = kwargs.get('parent_widget', self)
        _line = QtWidgets.QFrame()
        kwargs['frameShape'] = kwargs.get('frameShape',
                                          QtWidgets.QFrame.HLine)
        kwargs['frameShadow'] = kwargs.get('frameShadow',
                                           QtWidgets.QFrame.Sunken)
        kwargs['lineWidth'] = kwargs.get('lineWidth', 2)
        kwargs['fixedHeight'] = kwargs.get('fixedHeight', 3)
        apply_widget_properties(_line, **kwargs)
        _parent.layout().addWidget(
            _line, *_get_widget_layout_args(_parent, **kwargs)
            )
        return _line

    def create_spacer(self, **kwargs):
        """
        Add a spacer to the layout.

        A QSpacerItem will be created and added to the layout. Its size policy
        is "Minimal" unless overridden.

        Parameters
        ----------
        height : int, optional
            The height of the spacer in pixel. The default is 20.
        width : int, optional
            The width of the spacer in pixel. The default is 20.
        gridPos : Union[tuple, list, None], optional
            A list or tuple of length 4 can be supplied as the gridPos.
            The default            is None.
        policy : QtWidgets.QSizePolicy, optional
            The size policy for the spacer (applied both horizontally and
            vertically). The default is QtWidgets.QSizePolicy.Minimum.

        Returns
        -------
        spacer : QSpacerItem
            The new spacer.
        """
        _policy = kwargs.get('policy', QtWidgets.QSizePolicy.Minimum)
        _parent = kwargs.get('parent_widget', self)
        _spacer = QtWidgets.QSpacerItem(
            kwargs.get('fixedHeight', 20), kwargs.get('fixedWidth', 20),
            _policy, _policy
            )
        _layout_args = _get_widget_layout_args(_parent, **kwargs)
        _parent.layout().addItem(_spacer, *_layout_args)
        return _spacer

    def create_button(self, text, **kwargs):
        """
        Create a button and add it to the layout.

        Parameters
        ----------
        text : str
            The button text.
        **kwargs : dict
            Any supported keyword arguments.

        Supported keyword arguments
        ---------------------------
        gridPos : Union[tuple, None], optional
            The grid position of the widget in the layout. If None, the widget
            is added to the layout and the layout selects the widget's
            position. The default is None.
        *Qt settings : any
            Any supported Qt settings for button (for example, icon, visible,
            enabled, fixedWidth)

        Returns
        -------
        button : QtWidgets.QPushButton
            The instantiated button widget.
        """
        _parent = kwargs.get('parent_widget', self)
        _button = QtWidgets.QPushButton(text)
        apply_widget_properties(_button, **kwargs)
        _layout_args = _get_widget_layout_args(_parent, **kwargs)
        _parent.layout().addWidget(_button, *_layout_args)
        return _button

    def create_spin_box(self, **kwargs):
        """
        Create a button and add it to the layout.

        Parameters
        ----------
        **kwargs : dict
            Any supported keyword arguments.

        Supported keyword arguments
        ---------------------------
        valueRange: tuple, optional
            The range for the QSpinBox, given as a 2-tuple of (min, max). The
            default is (0, 1).
        *Qt settings : any
            Any supported Qt settings for a QSpinBox (for example value,
            fixedWidth, visible, enabled)

        Returns
        -------
        box : QtWidgets.QSpinBox
            The instantiated spin box widget.
        """
        _parent = kwargs.get('parent_widget', self)
        _box = create_spin_box(**kwargs)
        _layout_args = _get_widget_layout_args(_parent, **kwargs)
        _parent.layout().addWidget(_box, *_layout_args)
        return _box

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
        If the parent widget has no layout.

    Returns
    -------
    list
        The list of layout arguments required for adding the widget to
        the layout of the parent widget.
    """
    if parent.layout() is None:
        raise WidgetLayoutError('No layout set on parent widget'
                                f'"{parent}".')
    _alignment = kwargs.get('alignment', DEFAULT_ALIGNMENT)
    _grid_pos = kwargs.get('gridPos', None)
    if not isinstance(parent.layout(), QtWidgets.QGridLayout):
        return [0, _alignment]
    if _grid_pos is None:
        _row = (kwargs.get('row', parent.layout().rowCount() + 1)
                if isinstance(parent.layout(), QtWidgets.QGridLayout)
                else kwargs.get('row', -1))
        _grid_pos = (_row, kwargs.get('column', 0),
                     kwargs.get('n_rows', 1), kwargs.get('n_columns', 2))
    return [*_grid_pos, _alignment]
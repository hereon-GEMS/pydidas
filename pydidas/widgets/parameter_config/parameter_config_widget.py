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

"""Module with the PluginParameterConfigWidget class used to edit plugin parameters."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ParameterConfigWidget', 'ParameterConfigWidgetsMixIn']

import sys
import pathlib

from functools import partial

from PyQt5 import QtWidgets, QtCore
from .input_widget_combo import InputWidgetCombo
from .input_widget_file import InputWidgetFile
from .input_widget_line import InputWidgetLine
from .input_widget_hdfkey import InputWidgetHdfKey

from ..utilities import excepthook, apply_widget_properties
from ...config import STANDARD_FONT_SIZE
from ...core import HdfKey, ParameterCollection
from ..._exceptions import WidgetLayoutError


def param_widget_factory(param, widget_width):
    if param.choices:
        _widget = InputWidgetCombo(None, param, widget_width)
    else:
        if param.type == pathlib.Path:
            _widget =  InputWidgetFile(None, param, widget_width)
        elif param.type == HdfKey:
            _widget =  InputWidgetHdfKey(None, param, widget_width)
        else:
            _widget =  InputWidgetLine(None, param, widget_width)
    _widget.set_value(param.value)
    return _widget


def text_widget_factory(param, widget_width):#, alignment):
    _txt = QtWidgets.QLabel(f'{param.name}:')
    _txt.setFixedWidth(widget_width)
    _txt.setFixedHeight(20)
    _txt.setToolTip(param.tooltip)
    _txt.setMargin(0)
    # if alignment is not None:
    #     _txt.setAlignment(alignment)
    return _txt


class ParameterConfigWidgetsMixIn:
    """
    The ParameterConfigWidgetsMixIn class includes methods which can be added
    to other classes without having to inherit from ParameterConfigWidget to
    avoid multiple inheritance from QtWidgets.QFrame.
    """
    def __init__(self, *args, **kwargs):
        self.param_widgets = {}
        self.param_textwidgets = {}
        self.params = ParameterCollection()

    def create_param_widget(self, param, **kwargs):
        """
        Add a name label and input widget for a specific parameter to the
        widget.

        Parameters
        ----------
        param : Parameter
            A Parameter class instance.
        row : int, optional
            The row in case a grid layout is used. The default is -1 (the
            next row)
        column : int, optional
            The starting column in case of a grid layout. The default is 0.
        width_text : int, optional
            The width of the text field for the parameter name. The default
            is 120.
        width : int, optional
            The width of the input widget. The default is 255 pixel.
        n_columns : int, optional
            The number of grid columns for the i/o widget. The default is 1.
        n_columns_text : int, optional
            The number of grid columns for the text widget. The default is 1.
        linebreak : bool, optional
            Keyword to toggle a line break between the text label and the
            input widget. The default is False.
        halign_io : QtCore.Qt.Alignment, optional
            The horizontal alignment for the input widget. The default is
            QtCore.Qt.AlignRight.
        halign_text : QtCore.Qt.Alignment, optional
            The horizontal alignment for the text (label) widget. The default
            is QtCore.Qt.AlignRight.
        valign_io : QtCore.Qt.Alignment, optional
            The vertical alignment for the input widget. The default is
            QtCore.Qt.AlignTop.
        valign_text : QtCore.Qt.Alignment, optional
            The vertical alignment for the text (label) widget. The default
            is QtCore.Qt.AlignTop.
        parent_widget : Union[QWidget, None], optional
            The widget to which the label is added. If None, this defaults
            to the calling widget, ie. "self". The default is None.
        """
        _parent = kwargs.get('parent_widget', self)
        _config = self.__get_config_for_create_parameter(**kwargs)
        _text_widget = text_widget_factory(param, _config['width_text'])#,
                                           # _config['valign_text'])
        _input_widget = param_widget_factory(param, _config['width'])
        _input_widget.io_edited.connect(
            partial(self.__set_param_value, param, _input_widget))

        # store references to the widgets:
        self.param_widgets[param.refkey] = _input_widget
        self.param_textwidgets[param.refkey] = _text_widget

        # add widgets to layout:
        if _parent.layout() is None:
            raise WidgetLayoutError('No layout set.')
        _text_widget_args, _input_widget_args = \
            self.__get_layout_args_for_create_param_widget(_config)
        _parent.layout().addWidget(_text_widget, *_text_widget_args)
        _parent.layout().addWidget(_input_widget, *_input_widget_args)

    def __get_config_for_create_parameter(self, **kwargs):
        """
        Get the config with kwargs formatting options.

        Parameters
        ----------
        **kwargs : dict
            All possible formatting options.

        Returns
        -------
        config : dict
            The full formatting options, updated with the default values.
        """
        _row = (kwargs.get('row', self.layout().rowCount() + 1) if
                isinstance(self.layout(), QtWidgets.QGridLayout) else -1)
        config = {'row': _row,
                  'column': kwargs.get('column', 0),
                  'width_text': kwargs.get('width_text', 120),
                  'width': kwargs.get('width', 255),
                  'n_columns_text': kwargs.get('n_columns_text', 1),
                  'n_columns': kwargs.get('n_columns', 1),
                  'linebreak': kwargs.get('linebreak', False),
                  'halign_io': kwargs.get('halign_io',
                                          QtCore.Qt.AlignRight),
                  'halign_text': kwargs.get('halign_text',
                                            QtCore.Qt.AlignRight),
                  'valign_io': kwargs.get('valign_io',
                                          QtCore.Qt.AlignVCenter),
                  'valign_text': kwargs.get('valign_text',
                                            QtCore.Qt.AlignVCenter)}
        return config

    def __get_layout_args_for_create_param_widget(self, config):
        """
        Get the layout insertion arguments based on config.

        Parameters
        ----------
        config : dict
            The dictionary with the layout formatting arguments.

        Returns
        -------
        _txt_args : tuple
            The tuple with the layout formatting args for the text widget.
        _io_args : tuple
            The tuple with the layout formatting args for the input widget.
        """
        if isinstance(self.layout(), QtWidgets.QGridLayout):
            _txt_args = (config['row'], config['column'], 1,
                         config['n_columns_text'],
                         config['valign_text'] | config['halign_text'])
            _io_args = (config['row'] + config['linebreak'],
                        config['column'] + 1 - config['linebreak'], 1,
                        config['n_columns'],
                        config['valign_io'] | config['halign_io'])
        else:
            _txt_args = (0, QtCore.Qt.AlignRight)
            _io_args = (0, QtCore.Qt.AlignRight)
        return _txt_args, _io_args

    def update_param_value(self, key, value):
        """
        Update a parameter value both in the Parameter and the widget.

        This method will update the parameter referenced by <key> and
        update both the Parameter.value as well as the displayed widget
        entry.

        Parameters
        ----------
        key : str
            The reference key for the Parameter.
        value : object
            The new parameter value. This must be of the same type as the
            Parameter datatype.

        Raises
        ------
        KeyError
            If no parameter or widget has been registered with this key.
        """
        if key not in self.params or key not in self.param_widgets:
            raise KeyError(f'No parameter with key "{key}" found.')
        self.set_param_value(key, value)
        self.param_widgets[key].set_value(value)

    def toggle_widget_visibility(self, key, visible):
        """
        Toggle the visibility of widgets referenced with key.

        This method allows to show/hide the label and input widget for a
        parameter referenced with <key>.

        Parameters
        ----------
        key : str
            The reference key for the Parameter..
        visible : bool
            The boolean setting for the visibility.

        Raises
        ------
        KeyError
            If no widget has been registered with this key.
        """
        if key not in self.param_textwidgets or key not in self.param_widgets:
            raise KeyError(f'No parameter with key "{key}" found.')
        self.param_widgets[key].setVisible(visible)
        self.param_textwidgets[key].setVisible(visible)


    def get_param_value(self, key):
        """
        Get the value of the Parameter referencey by key.

        Parameters
        ----------
        key : str
            The parameter reference key.

        Raises
        ------
        KeyError
            If no parameter has been registered with key.

        Returns
        -------
        object
            The Parameter value (in the datatype determined by Parameter).
        """
        if key not in self.params:
            raise KeyError(f'No parameter with key "{key}" found.')
        return self.params[key].value

    @staticmethod
    def __set_param_value(param, widget):
        """
        Update the Parameter value with the entry from the widget.

        This method tries to update the Parameter value with the entry from
        the widget. If unsuccessful, an exception box will be opened and
        the widget input will be reset to the stored Parameter value.

        Parameters
        ----------
        param : Parameter
            A Parameter class instance from the plugin.
        widget : QWidget
            The input widget used for editing the parameter value.
        """
        try:
            param.value = widget.get_value()
        except Exception:
            widget.set_value(param.value)
            excepthook(*sys.exc_info())


class ParameterConfigWidget(QtWidgets.QFrame, ParameterConfigWidgetsMixIn):
    """
    The ParameterConfigWidget widget can be used to create a composite widget
    for updating parameter values.

    Depending on the parameter types, automatic typechecks are implemented.
    """
    def __init__(self, parent=None, **kwargs):
        """
        Setup method.

        Create an instance on the ParameterConfigWidget class.

        Parameters
        ----------
        parent : QtWidget, optional
            The parent widget. The default is None.
        initLayout : bool, optional
            Flag to toggle layout creation (with a VBoxLayout). The default
            is True.
        **kwargs : dict
            Additional keyword arguments
        """
        QtWidgets.QFrame.__init__(self, parent)
        ParameterConfigWidgetsMixIn.__init__(self)
        initLayout = kwargs.get('initLayout', True)
        kwargs['lineWidth'] = kwargs.get('lineWidth', 2)
        kwargs['frameStyle'] = kwargs.get('frameStyle',
                                          QtWidgets.QFrame.Raised)
        kwargs['autoFillBackground'] = kwargs.get('autoFillBackground', True)
        apply_widget_properties(self, **kwargs)
        if initLayout:
            _layout = QtWidgets.QGridLayout()
            _layout.setContentsMargins(5, 5, 0, 0)
            _layout.setAlignment(QtCore.Qt.AlignLeft
                                      | QtCore.Qt.AlignTop)
            self.setLayout(_layout)

    def next_row(self):
        """
        Get the next empty row in the layout.

        Returns
        -------
        int
            The next empty row.
        """
        return self.layout().rowCount() + 1

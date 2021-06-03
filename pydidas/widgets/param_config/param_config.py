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

"""Module with the PluginParamConfig class used to edit plugin parameters."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ParamConfig', 'ParamConfigMixIn']

import sys
import pathlib

from functools import partial

from PyQt5 import QtWidgets, QtCore
from .io_widget_combo import IOwidget_combo
from .io_widget_file import IOwidget_file
from .io_widget_line import IOwidget_line
from .io_widget_hdfkey import IOwidget_hdfkey

from ..utilities import excepthook
from ...config import STANDARD_FONT_SIZE
from ...core import HdfKey
from ..._exceptions import WidgetLayoutError


class ParamConfigMixIn:
    """
    The ParamConfigMixIn class includes methods which can be added to other
    classes without having to inherit from ParamConfig to avoid multiple
    inheritance from QtWidgets.QFrame.
    """
    def __init__(self, *args, **kwargs):
        self.param_widgets = {}
        self.params = {}
        self.param_textwidgets = {}

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

        Returns
        -------
        None.
        """
        if key not in self.params or key not in self.param_widgets:
            raise KeyError(f'No parameter with key "{key}" found.')
        self.params[key].value = value
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

        Returns
        -------
        None.
        """
        if key not in self.param_textwidgets or key not in self.param_widgets:
            raise KeyError(f'No parameter with key "{key}" found.')
        self.param_widgets[key].setVisible(visible)
        self.param_textwidgets[key].setVisible(visible)

    def add_label_widget(self, text, fontsize=STANDARD_FONT_SIZE, width=None,
                         gridPos=None):
        """
        Add a label to the widget.

        This method will add a label with "text" to the widget. Useful for
        defining item groups etc.

        Parameters
        ----------
        text : str
            The label text to be printed.
        fontsize : int, optional
            The font size in pixels. The default is STANDARD_FONT_SIZE.
        width : int, optional
            The width of the QLabel. If None, no width will be speciied.
            The default is None.
        gridPos : Union[list, tuple, None], optional
            The

        Returns
        -------
        None.
        """
        w = QtWidgets.QLabel(text)
        if fontsize != STANDARD_FONT_SIZE:
            _font = QtWidgets.QApplication.font()
            _font.setPointSize(fontsize)
            w.setFont(_font)
        if width:
            w.setFixedWidth(width)
        w.setFixedHeight(fontsize * (1 + text.count('\n')) + 10)
        if self.layout() is None:
            raise WidgetLayoutError('No layout set.')
        if isinstance(self.layout(), QtWidgets.QGridLayout):
            self.layout().addWidget(w, *gridPos,
                                    QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        else:
            self.layout().addWidget(w, 0,
                                    QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

    def add_param_widget(self, param, **kwargs):
        """
        Add a name label and input widget for a specific parameter to the
        widget.

        Parameters
        ----------
        param : Parameter
            A Parameter class instance.
        row : int, optional
            The row in case a grid layout is used.
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

        Returns
        -------
        None.
        """
        _row = (kwargs.get('row', self.layout().rowCount() + 1) if
                isinstance(self.layout(), QtWidgets.QGridLayout) else -1)
        self._cfg = {'row': _row,
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
                                             QtCore.Qt.AlignTop),
                     'valign_text': kwargs.get('valign_text',
                                               QtCore.Qt.AlignTop)
            }

        _txt = QtWidgets.QLabel(f'{param.name}:')
        _txt.setFixedWidth(self._cfg['width_text'])
        _txt.setFixedHeight(25)
        _txt.setToolTip(param.tooltip)

        # create an io widget depending on the Parameter.
        if param.choices:
            _io = IOwidget_combo(None, param, self._cfg['width'])
        else:
            if param.type == pathlib.Path:
                _io = IOwidget_file(None, param, self._cfg['width'])
            elif param.type == HdfKey:
                _io = IOwidget_hdfkey(None, param, self._cfg['width'])
            else:
                _io = IOwidget_line(None, param, self._cfg['width'])

        _io.io_edited.connect(partial(self.set_param_value, param, _io))
        _io.set_value(param.value)

        # store references to the widgets:
        self.param_widgets[param.refkey] = _io
        self.param_textwidgets[param.refkey] = _txt

        # add widgets to layout:
        if self.layout() is None:
            raise WidgetLayoutError('No layout set.')
        if isinstance(self.layout(), QtWidgets.QGridLayout):
            _vs = self.layout().verticalSpacing()
            self.layout().setVerticalSpacing(0)
            self.layout().addWidget(
                _txt, self._cfg['row'], self._cfg['column'], 1,
                self._cfg['n_columns_text'],
                self._cfg['valign_text'] | self._cfg['halign_text'])
            self.layout().addWidget(
                _io, self._cfg['row'] + self._cfg['linebreak'],
                self._cfg['column'] + 1 - self._cfg['linebreak'], 1,
                self._cfg['n_columns'],
                self._cfg['valign_io'] | self._cfg['halign_io'])
            self.layout().setVerticalSpacing(_vs)
        else:
            _l = QtWidgets.QHBoxLayout()
            _l.addWidget(_txt, 0, QtCore.Qt.AlignRight)
            _l.addWidget(_io, 0, QtCore.Qt.AlignRight)
            self.layout().addLayout(_l)

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
    def set_param_value(param, widget):
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

        Returns
        -------
        None.
        """
        try:
            param.value = widget.get_value()
        except Exception:
            widget.set_value(param.value)
            excepthook(*sys.exc_info())


class ParamConfig(QtWidgets.QFrame, ParamConfigMixIn):
    """
    The ParamConfig widget can be used to create a composite widget for
    updating parameter values.

    Depending on the parameter types, automatic typechecks are implemented.
    """
    def __init__(self, parent=None, **kwargs):
        """
        Setup method.

        Create an instance on the ParamConfig class.

        Parameters
        ----------
        parent : QtWidget, optional
            The parent widget. The default is None.
        initLayout : bool, optional
            Flag to toggle layout creation (with a VBoxLayout). The default
            is True.
        **kwargs : dict
            Additional keyword arguments

        Returns
        -------
        None.
        """
        initLayout = kwargs.get('initLayout', True)
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setLineWidth(2)
        self.setFrameStyle(QtWidgets.QFrame.Raised)
        if initLayout:
            _layout = QtWidgets.QVBoxLayout()
            _layout.setContentsMargins(5, 5, 0, 0)
            _layout.setAlignment(QtCore.Qt.AlignLeft
                                      | QtCore.Qt.AlignTop)
            self.setLayout(_layout)
        self.layout_meta = dict(set=initLayout, grid=False, row=0)

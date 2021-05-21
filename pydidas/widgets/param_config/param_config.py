#!/usr/bin/env python

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

from ..utilities import excepthook
from ...config import STANDARD_FONT_SIZE
from ..._exceptions import WidgetLayoutError


class ParamConfigMixIn:
    """
    The ParamConfigMixIn class includes methods which can be added to other
    classes without having to inherit from ParamConfig to avoid multiple
    inheritance from QtWidgets.QFrame.
    """
    def __init__(self, *args, **kwargs):
        self.param_widgets = {}
        self.param_txtwidgets = {}

    def add_label(self, text, fontsize=STANDARD_FONT_SIZE, width=None,
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
        if self.layout_meta['set']:
            if self.layout_meta['grid']:
                self.layout().addWidget(w, *gridPos, QtCore.Qt.AlignLeft)
            else:
                self.layout().addWidget(w, 0, QtCore.Qt.AlignLeft)
        else:
            raise WidgetLayoutError('No layout set.')

    def add_param(self, param, **kwargs):
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
        align_io : QtCore.Qt.Alignment, optional
            The alignment for the input widget. The default is
            QtCore.Qt.AlignRight.
        align_text : QtCore.Qt.Alignment, optional
            The alignment for the text (label) widget. The default is
            QtCore.Qt.AlignRight.

        Returns
        -------
        None.
        """
        self._cfg = {'row': kwargs.get('row', self.layout().rowCount() + 1),
                     'column': kwargs.get('column', 0),
                     'width_text': kwargs.get('textwidth', 120),
                     'width': kwargs.get('width', 255),
                     'n_columns_text': kwargs.get('n_columns_text', 1),
                     'n_columns': kwargs.get('n_columns', 1),
                     'linebreak': kwargs.get('linebreak', False),
                     'align_io': kwargs.get('align', QtCore.Qt.AlignRight),
                     'align_text': kwargs.get('align', QtCore.Qt.AlignRight)
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
            else:
                _io = IOwidget_line(None, param, self._cfg['width'])

        _io.io_edited.connect(partial(self.set_plugin_param, param, _io))
        _io.set_value(param.value)

        # store references to the widgets:
        self.param_widgets[param.refkey] = _io
        self.param_txtwidgets[param.refkey] = _txt

        # add widgets to layout:
        if self.layout() is None:
            raise WidgetLayoutError('No layout set.')
        if isinstance(self.layout(), QtWidgets.QGridLayout):
            self.layout().addWidget(
                _txt, self._cfg['row'], self._cfg['column'], 1,
                self._cfg['n_columns_text'], )
            self.layout().addWidget(
                _io, self._cfg['row'] + self._cfg['linebreak'],
                self._cfg['column'] + 1 - self._cfg['linebreak'], 1,
                self._cfg['n_columns'], self._cfg['align_io'])
        else:
            _l = QtWidgets.QHBoxLayout()
            _l.addWidget(_txt, 0, QtCore.Qt.AlignRight)
            _l.addWidget(_io, 0, QtCore.Qt.AlignRight)
            self.layout().addLayout(_l)


    @staticmethod
    def set_plugin_param(param, widget):
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

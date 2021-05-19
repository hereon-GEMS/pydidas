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
__all__ = ['ParamConfig']

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


class ParamConfig(QtWidgets.QFrame):
    """
    The PluginParamConfig widget creates the composite widget for updating
    parameters and changing default values.

    Depending on the parameter types, automatic typechecks are implemented.
    """
    def __init__(self, parent=None, **kwargs):
        """
        Setup method.

        Create an instance on the PluginParamConfig class.

        Parameters
        ----------
        parent : QtWidget, optional
            The parent widget. The default is None.
        initLayout : bool, optional
            Flag to toggle layout creation (with a VBoxLayout). The default
            is True.

        Returns
        -------
        None.
        """
        # parent = kwargs.get('parent', None)
        initLayout = kwargs.get('initLayout', True)
        print('Param config initLayout: ', initLayout)
        print(kwargs)
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setLineWidth(2)
        self.setFrameStyle(QtWidgets.QFrame.Raised)
        self.param_links = {}
        if initLayout:
            _layout = QtWidgets.QVBoxLayout()
            _layout.setContentsMargins(5, 5, 0, 0)
            _layout.setAlignment(QtCore.Qt.AlignLeft
                                      | QtCore.Qt.AlignTop)
            self.setLayout(_layout)
        self.layout_meta = dict(set=initLayout, grid=False, row=0)

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
        w.setFixedHeight(fontsize * (1 + text.count('\n')) + 8)
        if self.layout_meta['set']:
            if self.layout_meta['grid']:
                self.layout().addWidget(w, *gridPos, QtCore.Qt.AlignLeft)
            else:
                self.layout().addWidget(w, 0, QtCore.Qt.AlignLeft)
        else:
            raise WidgetLayoutError('No layout set.')

    def add_param(self, param, row=None):
        """
        Add a name label and input widget for a specific parameter to the
        widget.

        Parameters
        ----------
        param : Parameter
            A Parameter class instance from the plugin.
        row : int, optional
            The row in case a grid layout is used.

        Returns
        -------
        None.
        """
        _txt = QtWidgets.QLabel(f'{param.name}:')
        _txt.setFixedWidth(120)
        _txt.setFixedHeight(25)
        _txt.setToolTip(param.tooltip)

        if param.choices:
            _io = IOwidget_combo(None, param)
        else:
            if param.type == pathlib.Path:
                _io = IOwidget_file(None, param)
            else:
                _io= IOwidget_line(None, param)
        _io.io_edited.connect(partial(self.set_plugin_param, param, _io))
        _io.set_value(param.value)
        self.param_links[param.name] = _io
        if self.layout_meta['set']:
            if self.layout_meta['grid']:
                self.layout().addWidget(_txt, row, 0, 1, 1,
                                        QtCore.Qt.AlignRight)
                self.layout().addWidget(_io, row, 1, 1, 1,
                                        QtCore.Qt.AlignRight)
            else:
                _l = QtWidgets.QHBoxLayout()
                _l.addWidget(_txt, 0, QtCore.Qt.AlignRight)
                _l.addWidget(_io, 0, QtCore.Qt.AlignRight)
                self.layout().addLayout(_l)
        else:
            raise WidgetLayoutError('No layout set.')

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

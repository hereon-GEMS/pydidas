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
__all__ = ['PluginParamConfig']

import sys
import pathlib

from functools import partial

from PyQt5 import QtWidgets, QtGui, QtCore
from .io_widget_combo import IOwidget_combo
from .io_widget_file import IOwidget_file
from .io_widget_line import IOwidget_line

from ..utilities import deleteItemsOfLayout, excepthook
from ...gui import WorkflowEditTreeManager
from ...config import STANDARD_FONT_SIZE

WORKFLOW_EDIT_MANAGER = WorkflowEditTreeManager()

class PluginParamConfig(QtWidgets.QFrame):
    """
    The PluginParamConfig widget creates the composite widget for updating
    parameters and changing default values.

    Depending on the parameter types, automatic typechecks are implemented.
    """
    def __init__(self, parent=None):
        """
        Setup method.

        Create an instance on the PluginParamConfig class.

        Parameters
        ----------
        parent : QtWidget, optional
            The parent widget. The default is None.

        Returns
        -------
        None.
        """
        super().__init__(parent)
        self.parent = parent
        self.painter =  QtGui.QPainter()
        self.setAutoFillBackground(True)
        self.setLineWidth(2)
        self.setFrameStyle(QtWidgets.QFrame.Raised)
        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(5, 5, 0, 0)
        self._layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.plugin = None
        self.param_links = {}
        self.setLayout(self._layout)

    def configure_plugin(self, node_id):
        """
        Update the panel to show the parameters of a different plugin.

        This method clears the widget and populates it again with the
        parameters of the new plugin, defined by the plugin node_id

        Parameters
        ----------
        node_id : int
            The node_id in the workflow edit tree.

        Returns
        -------
        None.
        """
        self.plugin = WORKFLOW_EDIT_MANAGER.plugins[node_id]
        self.param_links = {}
        #delete current widgets
        for i in reversed(range(self._layout.count())):
            item = self._layout.itemAt(i)
            if isinstance(item, QtWidgets.QLayout):
                deleteItemsOfLayout(item)
                self._layout.removeItem(item)
                item.deleteLater()
            elif isinstance(item.widget(), QtWidgets.QWidget):
                widgetToRemove = item.widget()
                self._layout.removeWidget(widgetToRemove)
                widgetToRemove.setParent(None)
                widgetToRemove.deleteLater()

        #setup new widgets:
        self.add_label(f'Plugin: {self.plugin.plugin_name}', fontsize=12,
                       width=385)
        self.add_label(f'Node id: {node_id}', fontsize=12)
        self.add_label('\nParameters:', fontsize=12)
        if self.plugin.has_unique_param_config_widget():
            self._layout.add(self.plugin.param_config_widget())
        self.restore_default_button()
        for param in self.plugin.params:
            self.add_param(param)

    def restore_default_button(self):
        """
        Restore default values for all parameters.

        This method is called on clicks on the "Restore defaults" button and
        will reset all parameter to their default values.

        Returns
        -------
        None.
        """
        but = QtWidgets.QPushButton(self.style().standardIcon(59),
                                    'Restore default parameters')
        but.clicked.connect(partial(self.plugin.restore_defaults, force=True))
        but.clicked.connect(self.update_edits)
        but.setFixedHeight(25)
        self._layout.addWidget(but, 0, QtCore.Qt.AlignRight)

    def update_edits(self):
        """
        Update the input fields with the stored parameter values.

        This method will go through all plugin parameters and populates
        the input fields with the stores parameter values.

        Returns
        -------
        None.
        """
        for param in self.plugin.params:
            self.param_links[param.name].setText(param.value)

    def add_label(self, text, fontsize=STANDARD_FONT_SIZE, width=None):
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
        self._layout.addWidget(w, 0, QtCore.Qt.AlignLeft)

    def add_param(self, param):
        """
        Add a name label and input widget for a specific parameter to the
        widget.

        Parameters
        ----------
        param : Parameter
            A Parameter class instance from the plugin.

        Returns
        -------
        None.
        """
        _l = QtWidgets.QHBoxLayout()
        _txt = QtWidgets.QLabel(f'{param.name}:')
        _txt.setFixedWidth(120)
        _txt.setFixedHeight(25)
        _txt.setToolTip(param.tooltip)
        _l.addWidget(_txt, 0, QtCore.Qt.AlignRight)

        if param.choices:
            _io = IOwidget_combo(None, param)
        else:
            if param.type == pathlib.Path:
                _io = IOwidget_file(None, param)
            else:
                _io= IOwidget_line(None, param)
        _io.io_edited.connect(partial(self.set_plugin_param, param, _io))
        _io.set_value(param.value)
        _l.addWidget(_io, 0, QtCore.Qt.AlignRight)
        self.param_links[param.name] = _io
        self._layout.addLayout(_l)


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
        except:
            widget.set_value(param.value)
            excepthook(*sys.exc_info())

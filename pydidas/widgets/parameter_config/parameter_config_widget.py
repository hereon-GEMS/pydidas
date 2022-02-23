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
Module with the ParameterConfigWidget class which is a generic QWidget with a
GridLayout to add the label, I/O and unit widgets for a Parameter.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ParameterConfigWidget']

import sys
from functools import partial

from qtpy import QtWidgets, QtCore

from ...core.constants import (
    PARAM_INPUT_WIDGET_HEIGHT, PARAM_INPUT_WIDGET_WIDTH,
    PARAM_INPUT_EDIT_WIDTH, PARAM_INPUT_TEXT_WIDTH, PARAM_INPUT_UNIT_WIDTH)
from ...core.utils import convert_special_chars_to_unicode
from ..utilities import apply_widget_properties, excepthook
from ..factory import create_param_widget, create_label


class ParameterConfigWidget(QtWidgets.QWidget):
    """
    The ParameterConfigWidget is a combined widget to display and modify a
    Parameter with name, value and unit.

    This widget is a wrapper and includes labels for name and unit and the
    respective Parameter edit widget which is selected based on the Parameter
    type and choices.

    This is the public widget should be added to the GUI to display and modify
    Parameters.

    Parameters
    ----------
    param : pydidas.core.Parameter
        The associated Parameter.
    parent : QtWidget, optional
        The parent widget. The default is None.
    **kwargs : dict
        Additional keyword arguments
    """
    io_edited = QtCore.Signal(str)

    def __init__(self, param, parent=None, **kwargs):
        QtWidgets.QWidget.__init__(self, parent)
        self.__set_size_from_kwargs(kwargs)
        self.__store_config_from_kwargs(kwargs)

        self.param = param
        _layout = QtWidgets.QGridLayout()
        _layout.setContentsMargins(0, 0, 0, 0)
        _layout.setSpacing(5)
        _layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        _layout.setColumnStretch(1, 1)
        self.name_widget = self.__get_name_widget()
        if self.config['width_unit'] > 0:
            self.unit_widget = self.__get_unit_widget()
        self.io_widget = create_param_widget(param, self.config['width_io'])

        _text_widget_args, _input_widget_args, _unit_widget_args = \
            self.__get_layout_args_for_widgets()
        _layout.addWidget(self.name_widget, *_text_widget_args)
        _layout.addWidget(self.io_widget, *_input_widget_args)
        if self.config['width_unit'] > 0:
            _layout.addWidget(self.unit_widget, *_unit_widget_args)

        self.io_widget.io_edited.connect(self.__emit_io_changed)
        self.io_widget.io_edited.connect(
            partial(self.__set_param_value, param, self.io_widget))
        self.setLayout(_layout)
        apply_widget_properties(self, **kwargs)

    def __set_size_from_kwargs(self, kwargs):
        """
        Set the size of the widget based on the input keyword arguments.

        Parameters
        ----------
        kwargs : dict
            The keyword arguments.
        """
        _linebreak = kwargs.get('linebreak', False)
        _width = kwargs.get('width_total', PARAM_INPUT_WIDGET_WIDTH)
        _height = (PARAM_INPUT_WIDGET_HEIGHT
                   + _linebreak * (PARAM_INPUT_WIDGET_HEIGHT + 4))
        self.setFixedWidth(_width)
        self.setFixedHeight(_height)

    def __store_config_from_kwargs(self, kwargs):
        """
        Get the config from the kwargs formatting options.

        Parameters
        ----------
        parent : QtWidgets.QWidget
            The parent widget.
        **kwargs : dict
            All possible formatting options.

        Returns
        -------
        config : dict
            The full formatting options, updated with the default values.
        """
        _width = kwargs.get('width_total', PARAM_INPUT_WIDGET_WIDTH)
        _width_unit = kwargs.get('width_unit', PARAM_INPUT_UNIT_WIDTH)
        config = {'linebreak': kwargs.get('linebreak', False),
                  'valign_io': kwargs.get('valign_io',
                                          QtCore.Qt.AlignVCenter),
                  'valign_text': kwargs.get('valign_text',
                                            QtCore.Qt.AlignVCenter)}
        if config['linebreak']:
            config['width_text'] = kwargs.get('width_text', _width - 10)
            config['width_io'] = kwargs.get('width_io',
                                            _width - _width_unit - 20)
            config['halign_text'] = kwargs.get('halign_text',
                                               QtCore.Qt.AlignLeft)
            config['halign_io'] = kwargs.get('halign_io',
                                              QtCore.Qt.AlignRight)
        else:
            config['width_text'] = kwargs.get('width_text',
                                              PARAM_INPUT_TEXT_WIDTH)
            config['width_io'] = kwargs.get('width_io',
                                            PARAM_INPUT_EDIT_WIDTH)
            config['halign_text'] = kwargs.get('halign_text',
                                               QtCore.Qt.AlignLeft)
            config['halign_io'] = kwargs.get('halign_io',
                                             QtCore.Qt.AlignRight)
        config['width_unit'] = _width_unit
        config['width_total'] = _width
        config['halign_unit'] = kwargs.get('halign_unit', QtCore.Qt.AlignLeft)
        config['valign_unit'] = kwargs.get('valign_unit',
                                           QtCore.Qt.AlignVCenter)
        self.config = config

    def __get_name_widget(self):
        """
        Get a widget with the Parameter's name.

        Parameters
        ----------
        config : dict
            The configuration dictionary.

        Returns
        -------
        QtWidgets.QLabel
            The label with the Parameter's name.
        """
        _text = convert_special_chars_to_unicode(self.param.name) + ':'
        return create_label(_text, fixedWidth=self.config['width_text'],
                            fixedHeight=20, toolTip=self.param.tooltip,
                            margin=0)

    def __get_unit_widget(self):
        """
        Get a widget with the Parameter's unit text.

        Parameters
        ----------
        config : dict
            The configuration dictionary.

        Returns
        -------
        QtWidgets.QLabel
            The label with the Parameter's unit text.
        """
        _text = convert_special_chars_to_unicode(self.param.unit)
        return create_label(_text, fixedWidth=self.config['width_unit'],
                            fixedHeight=20, toolTip=self.param.tooltip,
                            margin=0)

    def __get_layout_args_for_widgets(self):
        """
        Get the layout insertion arguments based on config.

        Parameters
        ----------
        config : dict
            The dictionary with the layout formatting arguments.

        Returns
        -------
        txt_args : tuple
            The tuple with the layout formatting args for the name widget.
        io_args : tuple
            The tuple with the layout formatting args for the io widget.
        unit_args : tuple
            The tuple with the layout formatting args for the unit widget.
        """
        _iline = int(self.config['linebreak'])
        _iunit = int(self.config['width_unit'] > 0)
        _txtargs = (0, 0, 1, 1 + 2 * _iline,
                    self.config['valign_text'] | self.config['halign_text'])
        _ioargs = (_iline, 1, 1, 2 - _iunit,
                   self.config['valign_io'] | self.config['halign_io'])
        _unitargs = (_iline, 2, 1, 1,
                     self.config['valign_text'] | self.config['halign_text'])
        return _txtargs, _ioargs, _unitargs

    @QtCore.Slot(str)
    def __emit_io_changed(self, value):
        """
        Forward the io_changed signal from the IO widget.

        Parameters
        ----------
        value : str
            The value emitted by the IO widget.
        """
        self.io_edited.emit(value)

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
        except ValueError:
            widget.set_value(param.value)
            excepthook(*sys.exc_info())

    def sizeHint(self):
        """
        Set the Qt sizeHint to be the widget's size.

        Returns
        -------
        QtCore.QSize
            The size of the widget.
        """
        return QtCore.QSize(self.width(), self.height())

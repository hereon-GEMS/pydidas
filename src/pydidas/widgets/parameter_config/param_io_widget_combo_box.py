# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the ParamIoWidgetComboBox class used to edit Parameters. This
class is used for all Parameters with predefined choices.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ParamIoWidgetComboBox"]


from collections.abc import Iterable

from qtpy import QtCore

from pydidas.core import Parameter
from pydidas.core.utils import (
    convert_special_chars_to_unicode,
    convert_unicode_to_ascii,
)
from pydidas.widgets.factory import PydidasComboBox
from pydidas.widgets.parameter_config.base_param_io_widget_mixin import (
    BaseParamIoWidgetMixIn,
)
from pydidas.widgets.utilities import get_max_pixel_width_of_entries


class ParamIoWidgetComboBox(BaseParamIoWidgetMixIn, PydidasComboBox):
    """Widgets for I/O during plugin parameter editing with predefined choices."""

    def __init__(self, param: Parameter, **kwargs: dict):
        """
        Initialize the widget.

        Init method to setup the widget and set the links to the parameter
        and Qt parent widget.

        Parameters
        ----------
        param : Parameter
            A Parameter instance.
        width : int, optional
            The width of the IOwidget.
        """
        PydidasComboBox.__init__(self)
        BaseParamIoWidgetMixIn.__init__(self, param, **kwargs)
        for choice in param.choices:
            self.addItem(f"{convert_special_chars_to_unicode(str(choice))}")

        self.__items = [self.itemText(i) for i in range(self.count())]
        self.currentIndexChanged.connect(self.emit_signal)
        self.set_value(param.value)
        # self.view().setMinimumWidth(get_max_pixel_width_of_entries(self.__items) + 50)

    def __convert_bool(self, value: object) -> object:
        """
        Convert boolean integers to string.

        This conversion is necessary because boolean "0" and "1" cannot be
        interpreted as "True" and "False" straight away.

        Parameters
        ----------
        value : object
            The input value from the field. This could be any object.

        Returns
        -------
        value : any
            The input value, with 0/1 converted it True or False are
            widget choices.
        """
        if value == 0 and "False" in self.__items:
            value = "False"
        elif value == 1 and "True" in self.__items:
            value = "True"
        return value

    def emit_signal(self):
        """
        Emit a signal that the value has been edited.

        This method emits a signal that the combobox selection has been
        changed and the Parameter value needs to be updated.
        """
        _cur_value = convert_unicode_to_ascii(self.currentText())
        if _cur_value != self._old_value:
            self._old_value = _cur_value
            self.io_edited.emit(_cur_value)

    def get_value(self) -> object:
        """
        Get the current value from the combobox to update the Parameter value.

        Returns
        -------
        object
            The text converted to the required datatype (int, float, path)
            to update the Parameter value.
        """
        text = convert_unicode_to_ascii(self.currentText())
        return self.get_value_from_text(text)

    def set_value(self, value: object):
        """
        Set the input field's value.

        This method changes the combobox selection to the specified value.

        Parameters
        ----------
        value : object
            The value to be set.
        """
        value = self.__convert_bool(value)
        self._old_value = value
        _txt_repr = convert_special_chars_to_unicode(str(value))
        self.setCurrentText(_txt_repr)

    def update_choices(self, new_choices: Iterable[object, ...]):
        """
        Update the choices of the BaseParamIoWidget in place.

        This method also selects the first new choice as new item.
        Note: This method does not update the associated Parameter and does
        not synchronize with the Parameter.

        Parameters
        ----------
        new_choices : collections.abc.Iterable
            Any iterable with new choices.
        """
        with QtCore.QSignalBlocker(self):
            self.clear()
            for choice in new_choices:
                _itemstr = convert_special_chars_to_unicode(str(choice))
                self.addItem(_itemstr)
            self.__items = [self.itemText(i) for i in range(self.count())]
            self.set_value(new_choices[0])
            self.emit_signal()
        self.view().setMinimumWidth(get_max_pixel_width_of_entries(self.__items) + 50)

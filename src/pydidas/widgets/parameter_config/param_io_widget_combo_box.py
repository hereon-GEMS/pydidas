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


from collections.abc import Sequence
from typing import Any

from qtpy import QtCore

from pydidas.core import Parameter
from pydidas.core.utils import (
    convert_special_chars_to_unicode,
    convert_unicode_to_ascii,
)
from pydidas.widgets.factory import PydidasComboBox
from pydidas.widgets.parameter_config.base_param_io_widget import (
    BaseParamIoWidgetMixIn,
)
from pydidas.widgets.utilities import get_max_pixel_width_of_entries


class ParamIoWidgetComboBox(BaseParamIoWidgetMixIn, PydidasComboBox):
    """Widget used for editing Parameter values with predefined choices."""

    def __init__(self, param: Parameter, **kwargs: Any):
        """
        Initialize the widget.

        Init method to set up the widget and set the links to the parameter
        and Qt parent widget.

        Parameters
        ----------
        param : Parameter
            A Parameter instance.
        **kwargs : Any
            Supported keyword arguments are all supported arguments of the
            PydidasComboBox.
        """
        PydidasComboBox.__init__(self, **kwargs)
        BaseParamIoWidgetMixIn.__init__(self, param)
        self.__items = []
        for choice in param.choices:
            _display_txt = convert_special_chars_to_unicode(str(choice))
            self.__items.append(_display_txt)
            self.addItem(_display_txt)
        self.update_widget_value(param.value)
        self.currentIndexChanged.connect(self.emit_signal)

    @property
    def current_text(self) -> str:
        """
        Get the text of the current combobox selection.

        Returns
        -------
        str
            The text of the current combobox selection.
        """
        return convert_unicode_to_ascii(self.currentText())

    @property
    def current_choices(self) -> list[str]:
        """
        Get the current list of choices in the combobox.

        Returns
        -------
        list[str]
            The current list of choices in the combobox.
        """
        return [convert_unicode_to_ascii(_item) for _item in self.__items]

    def update_widget_value(self, value: Any) -> None:
        """
        Update the widget value.

        Parameters
        ----------
        value : Any
            The new value to set in the widget.
        """
        value = self.__convert_bool(value)
        _txt_repr = convert_special_chars_to_unicode(str(value))
        self.setCurrentText(_txt_repr)

    def __convert_bool(self, value: Any) -> Any:
        """
        Convert boolean integers to string representations of True or False.

        Parameters
        ----------
        value : Any
            The input value from the field.

        Returns
        -------
        value : Any
            The input value, with 0/1 converted it True or False are
            widget choices.
        """
        if value == 0 and "False" in self.__items:
            value = "False"
        elif value == 1 and "True" in self.__items:
            value = "True"
        return value

    def update_choices(
        self,
        new_choices: Sequence[Any],
        selection: str | None = None,
        emit_signal: bool = True,
    ) -> None:
        """
        Update the choices of the BaseParamIoWidget in place.

        This method also selects the first new choice as new item.
        Note: This method does not update the associated Parameter and does
        not synchronize with the Parameter.

        Parameters
        ----------
        new_choices : collections.abc.Sequence
            Any sequence with new choices.
        selection : str, optional
            The selection to be set after the update. If None, the first
            choice will be selected. Default is None.
        emit_signal : bool, optional
            If True, a signal will be emitted after updating the choices.
            The default is True.
        """
        self._old_value = self.current_text
        with QtCore.QSignalBlocker(self):
            self.clear()
            for choice in new_choices:
                _itemstr = convert_special_chars_to_unicode(str(choice))
                self.addItem(_itemstr)
            self.__items = [self.itemText(i) for i in range(self.count())]
            if selection is not None and selection in new_choices:
                self.update_widget_value(selection)
            else:
                self.update_widget_value(new_choices[0])
        if emit_signal:
            self.emit_signal()
        self.view().setMinimumWidth(get_max_pixel_width_of_entries(self.__items) + 50)

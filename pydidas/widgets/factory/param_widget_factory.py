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
Module with a factory function to create Parameter input/output widgets
consisting of a label for the name, an I/O field and a label for the unit.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['create_param_widget']

import pathlib

from ...core.constants import PARAM_INPUT_EDIT_WIDTH
from ...core import Hdf5key


def create_param_widget(param, widget_width=PARAM_INPUT_EDIT_WIDTH):
    """
    Create a widget based on the type of Parameter input.

    This factory function will select a widget based on the following
    settings:

        1. If the Parameter has defined choices, a
           :py:class:`ParamIoWidgetComboBox` is returned.
        2. If the Parameter type is Path, a :py:class:`ParamIoWidgetFile`
           is returned.
        3. If the Parameter type is Hdf5key, a :py:class:`ParamIoWidgetHdf5key`
           is returned.
        4. Otherwise, a :py:class:`ParamIoWidgetLineEdit` is returned.

    Parameters
    ----------
    param : pydidas.core.Parameter
        The Parameter requiring an I/O widget.
    widget_width : int, optional
        The width of the corresponding widget. The default is 255.

    Returns
    -------
    pydidas.widgets.parameter_config.BaseParamIoWidget
        The I/O widget.
    """
    # need to place the import here to prevent circular import. The circular
    # import cannot be prevented while maintaining the desired module
    # structure.
    from ..parameter_config.param_io_widget_file import ParamIoWidgetFile
    from ..parameter_config.param_io_widget_hdf5key import ParamIoWidgetHdf5Key
    from ..parameter_config.param_io_widget_combo_box import (
        ParamIoWidgetComboBox)
    from ..parameter_config.param_io_widget_lineedit import (
        ParamIoWidgetLineEdit)

    if param.choices:
        _widget = ParamIoWidgetComboBox(None, param, widget_width)
    else:
        if param.type == pathlib.Path:
            _widget = ParamIoWidgetFile(None, param, widget_width)
        elif param.type == Hdf5key:
            _widget = ParamIoWidgetHdf5Key(None, param, widget_width)
        else:
            _widget = ParamIoWidgetLineEdit(None, param, widget_width)
    _widget.set_value(param.value)
    return _widget

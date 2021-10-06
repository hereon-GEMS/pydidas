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

"""Module with a factory function to create formatted QSpinBoxes."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['create_param_widget']

import pathlib

from ...core import Hdf5key
from ..parameter_io_widgets import (InputWidgetCombo, InputWidgetFile,
                                    InputWidgetLine, InputWidgetHdf5Key)


def create_param_widget(param, widget_width=255):
    """
    Create a widget based on the type of Parameter input.

    Parameters
    ----------
    param : pydidas.core.Parameter
        The Parameter requiring an I/O widget.
    widget_width : int, optional
        The width of the corresponding widget. The default is 255.

    Returns
    -------
    pydidas.widgets.parameter_config.InputWidget
        The I/O widget.
    """
    if param.choices:
        _widget = InputWidgetCombo(None, param, widget_width)
    else:
        if param.type == pathlib.Path:
            _widget =  InputWidgetFile(None, param, widget_width)
        elif param.type == Hdf5key:
            _widget =  InputWidgetHdf5Key(None, param, widget_width)
        else:
            _widget =  InputWidgetLine(None, param, widget_width)
    _widget.set_value(param.value)
    return _widget

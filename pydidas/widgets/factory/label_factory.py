# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""Module with a factory function to create formatted QLabels."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['create_label']

from PyQt5.QtWidgets import QLabel, QApplication

from ..utilities import apply_widget_properties, apply_font_properties
from ...config import STANDARD_FONT_SIZE


def create_label(text, **kwargs):
    """
    This method will create a label with text.

    Parameters
    ----------
    text : str
        The label text to be printed.
    fontsize : int, optional
        The font size in pixels. The default is STANDARD_FONT_SIZE.
    **kwargs : dict
        Any aditional keyword arguments. See below for supported
        arguments.

    Supported keyword arguments
    ---------------------------
    *Qt settings : any
        Any Qt settings

    Returns
    -------
    label : QLabel
        The formatted QLabel
    """
    _label = QLabel(text)

    kwargs['pointSize'] = kwargs.get('fontsize', STANDARD_FONT_SIZE)
    kwargs['wordWrap'] = kwargs.get('wordWrap', True)
    kwargs['font'] = QApplication.font()

    apply_font_properties(kwargs['font'], **kwargs)
    apply_widget_properties(_label, **kwargs)
    return _label

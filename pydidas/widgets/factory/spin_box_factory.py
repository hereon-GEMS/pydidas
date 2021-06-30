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

"""Module with a factory function to create formatted QSpinBoxes."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['create_spin_box']

from PyQt5.QtWidgets import QSpinBox

from ..utilities import apply_widget_properties

def create_spin_box(**kwargs):
    """
    Create a QSpinBox widget and set properties.

    Parameters
    ----------
    **kwargs : dict
        Any supported keyword arguments.

    Supported keyword arguments
    ---------------------------
    valueRange: tuple, optional
        The range for the QSpinBox, given as a 2-tuple of (min, max). The
        default is (0, 1).
    *Qt settings : any
        Any supported Qt settings for a QSpinBox (for example value,
        fixedWidth, visible, enabled)

    Returns
    -------
    box : QtWidgets.QSpinBox
        The instantiated spin box widget.
    """
    kwargs['range'] = kwargs.get('valueRange', (0, 1))
    kwargs['fixedWidth'] = kwargs.get('fixedWidth', 50)
    _box = QSpinBox()
    apply_widget_properties(_box, **kwargs)
    return _box

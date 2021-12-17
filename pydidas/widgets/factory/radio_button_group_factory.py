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
Module with a factory function to create radio button groups with a choice
of their alignment and joint toggles.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['create_radio_button_group']

from ..utilities import apply_widget_properties


def create_radio_button_group(entries, vertical=True, title=None, **kwargs):
    """
    Create a RadioButtonGroup widget and set properties.

    Parameters
    ----------
    entries : list
        The list of labels for the RadioButtons.
    vertical : bool
        Keyword to arrange the RadioButtons vertically. If False, a horizontal
        alignment is used. The default is True.
    title : Union[str, None]
        The title/label of the RadioButtonGroup. If None, no title is used.
        The default is None.
    **kwargs : dict
        Any supported keyword arguments.

    Supported keyword arguments
    ---------------------------
    *Qt settings : any
        Any supported Qt settings for a QSpinBox (for example value,
        fixedWidth, visible, enabled)

    Returns
    -------
    box : RadioButtonGroup
        The instantiated spin box widget.
    """
    # need to place the import here to prevent circular import. The circular
    # import cannot be prevented while maintaining the desired module
    # structure.
    from ..selection import RadioButtonGroup

    _box = RadioButtonGroup(None, entries, vertical=vertical, title=title)
    apply_widget_properties(_box, **kwargs)
    return _box

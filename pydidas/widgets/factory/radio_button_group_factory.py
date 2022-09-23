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
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["create_radio_button_group"]

from ...core.utils import apply_qt_properties


def create_radio_button_group(entries, title=None, **kwargs):
    """
    Create a RadioButtonGroup widget and set properties.

    Parameters
    ----------
    entries : list
        The list of labels for the RadioButtons.
    title : Union[str, None]
        The title/label of the RadioButtonGroup. If None, no title is used.
        The default is None.
    rows : int, optional
        The number of button rows (i.e. vertical alignment) of the
        QRadioButtons. -1 will toggle automatic determination of the number
        of rows. The default is 1.
    columns: int, optional
        The number of button columns (i.e. horizontal alignment) of the
        QRadioButtons. -1 will toggle automatic determination of the number
        of columns. The default is -1.
    **kwargs : dict
        Any additional keyword arguments. See below for supported arguments.
    **QtAttribute : depends on the attribute
        Any Qt attributes which are supported by the RadioButtonGroup. Use the
        Qt attribute name with a lowercase first character. Examples are
        ``icon``, ``fixedWidth``, ``visible``, ``enabled``.

    Returns
    -------
    box : RadioButtonGroup
        The instantiated spin box widget.
    """
    # need to place the import here to prevent circular import. The circular
    # import cannot be prevented while maintaining the desired module
    # structure.
    from ..selection import RadioButtonGroup

    _box = RadioButtonGroup(None, entries, title=title, **kwargs)
    apply_qt_properties(_box, **kwargs)
    return _box

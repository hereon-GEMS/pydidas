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
Module with utility functions for Qt objects.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["update_size_policy", "apply_qt_properties", "apply_font_properties"]


def _get_args_as_list(args):
    """
    Format the input arguments to an interable list to be passed as *args.

    Parameters
    ----------
    args : object
        Any input

    Returns
    -------
    args : Union[tuple, list, set]
        The input arguments formatted to a iterable list.
    """
    if not isinstance(args, (tuple, list, set)):
        args = [args]
    return args


def update_size_policy(obj, **kwargs):
    """
    Update the sizePolicy of an object with various keywords.

    This function takes a dictionary (ie. keyword arguments) and iterates
    through all keys. Keys will be interpreted in Qt style: A "property: 12"
    entry in the dictionary will verify that the widget has a "setProperty"
    method and will then call "obj.setProperty(12)". The verificiation that
    the methods exist allows this function to take the full kwargs of any
    object without the need to filter out non-related keys.

    Parameters
    ----------
    obj : QtWidgets.QWidget
        Any QWidget (because other QObjects do not have a sicePolicy).
    **kwargs : dict
        A dictionary with properties to set.
    """
    _policy = obj.sizePolicy()
    apply_qt_properties(_policy, **kwargs)
    obj.setSizePolicy(_policy)


def apply_qt_properties(obj, **kwargs):
    """
    Set Qt widget properties from a supplied dict.

    This function takes a dictionary (ie. keyword arguments) and iterates
    through all keys. Keys will be interpreted in Qt style: A "property: 12"
    entry in the dictionary will verify that the widget has a "setProperty"
    method and will then call "obj.setProperty(12)". The verificiation that
    the methods exist allows this function to take the full kwargs of any
    object without the need to filter out non-related keys.

    Parameters
    ----------
    obj : QtCore.QObject
        Any QObject.
    **kwargs : dict
        A dictionary with properties to be set.
    """
    for _key in kwargs:
        _name = f"set{_key[0].upper()}{_key[1:]}"
        if hasattr(obj, _name):
            _func = getattr(obj, _name)
            _func(*_get_args_as_list(kwargs.get(_key)))


def apply_font_properties(fontobj, **kwargs):
    """
    Set font properties from a supplied dict.

    This function takes a dictionary (ie. keyword arguments) and iterates
    through all keys. Keys will be interpreted in Qt style: A "property: 12"
    entry in the dictionary will verify that the font object has a
    "setProperty" method and will then call "fontobj.setProperty(12)". The
    verificiation that methods exist allows this function to take the full
    kwargs of any object without the need to filter out non-related keys.

    Parameters
    ----------
    fontobj : QObject
        Any QFont
    **kwargs : dict
        A dictionary with properties to be set.
    """
    if "fontsize" in kwargs and "pointSize" not in kwargs:
        kwargs["pointSize"] = kwargs.get("fontsize")
    for _key in kwargs:
        _name = f"set{_key[0].upper()}{_key[1:]}"
        if hasattr(fontobj, _name):
            _func = getattr(fontobj, _name)
            _func(*_get_args_as_list(kwargs.get(_key)))

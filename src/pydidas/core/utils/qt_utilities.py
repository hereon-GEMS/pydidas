# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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
Module with utility functions for Qt objects.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "update_child_qobject",
    "update_size_policy",
    "apply_qt_properties",
    "update_palette",
    "update_qobject_font",
    "apply_font_properties",
    "check_pydidas_qapp_instance",
    "IS_QT6",
]


from collections.abc import Iterable
from typing import Any, NoReturn

from qtpy import QT_VERSION, QtGui, QtWidgets
from qtpy.QtCore import QObject
from qtpy.QtGui import QFont
from qtpy.QtWidgets import QWidget

from pydidas_qtcore import PydidasQApplication


IS_QT6 = QT_VERSION[0] == "6"


def _get_args_as_list(args: Iterable):
    """
    Format the input arguments to an iterable list to be passed as *args.

    This is used to convert strings (which are Iterable) to a list entry to
    prevent iterating over each string character.

    Parameters
    ----------
    args : Iterable
        Any input

    Returns
    -------
    args : Union[tuple, list, set]
        The input arguments formatted to an iterable list.
    """
    if not isinstance(args, (tuple, list, set)):
        args = [args]
    return args


def update_child_qobject(obj: QObject, attr: str, **kwargs: Any):
    """
    Update the objects given attribute in place.

    This function allows updating a QObjects attribute, which is a QObject itself,
    in place and updating the original object after the update.

    This function takes a dictionary (i.e., keyword arguments) and iterates
    through all keys. Keys will be interpreted in Qt style: A "property: 12"
    entry in the dictionary will verify that the widget has a "setProperty"
    method and will then call "obj.setProperty(12)". The verification that
    the methods exist allows this function to take the full kwargs of any
    object without the need to filter out non-related keys.

    Note that the object is modified in place and no explicit return is given.

    Parameters
    ----------
    obj : QObject
        The parent QObject.
    attr : str
        The name of the child QObject.
    **kwargs : Any
        A dictionary with properties to set.
    """
    _child_obj = getattr(obj, attr)()
    apply_qt_properties(_child_obj, **kwargs)
    _child_setter = getattr(obj, "set" + attr[0].upper() + attr[1:])
    _child_setter(_child_obj)


def update_size_policy(obj: QWidget, **kwargs: Any):
    """
    Update the sizePolicy of an object with various keywords.

    Parameters
    ----------
    obj : QtWidgets.QWidget
        Any QWidget (because other QObjects do not have a sicePolicy).
    **kwargs : Any
        A dictionary with properties to set.
    """
    update_child_qobject(obj, "sizePolicy", **kwargs)


def apply_qt_properties(obj: QObject, **kwargs: Any):
    """
    Set Qt widget properties from a supplied dict.

    This function takes a dictionary (i.e., keyword arguments) and iterates
    through all keys. Keys will be interpreted in Qt style: A "property: 12"
    entry in the dictionary will verify that the widget has a "setProperty"
    method and will then call "obj.setProperty(12)". The verification that
    the methods exist allows this function to take the full kwargs of any
    object without the need to filter out non-related keys.

    Note that the object is modified in place and no explicit return is given.

    Parameters
    ----------
    obj : QtCore.QObject
        Any QObject or subclass
    **kwargs : Any
        A dictionary with properties to be set.
    """
    for _key in kwargs:
        _name = f"set{_key[0].upper()}{_key[1:]}"
        if hasattr(obj, _name):
            _func = getattr(obj, _name)
            _func(*_get_args_as_list(kwargs.get(_key)))


def update_palette(obj: QWidget, **kwargs: Any):
    """
    Update the palette associated with a QWidget.

    Note that the object is modified in place and no explicit return is given.

    Parameters
    ----------
    obj : QtCore.QObject
        The QObject to be updated.
    **kwargs : Any
        A dictionary with palette values. Keys must correspond to palette roles.
    """
    _palette = obj.palette()
    for _key, _value in kwargs.items():
        if QT_VERSION.startswith("5"):
            _role = _key[0].upper() + _key[1:]
            if _role in QtGui.QPalette.__dict__:
                _role_key = getattr(QtGui.QPalette, _role)
                _palette.setColor(_role_key, QtGui.QColor(_value))
        elif QT_VERSION.startswith("6"):
            _role = _key[0].upper() + _key[1:]
            if _role in QtGui.QPalette.ColorRole.__dict__:
                _role_key = getattr(QtGui.QPalette.ColorRole, _role)
                _palette.setColor(_role_key, QtGui.QColor(_value))
    obj.setPalette(_palette)


def update_qobject_font(obj: QObject, **kwargs: Any):
    """
    Update the font associated with a QObject.

    Note that the object is modified in place and no explicit return is given.

    Parameters
    ----------
    obj : QtCore.QObject
        The QObject to be updated.
    **kwargs : Any
        A dictionary with font properties.
    """
    _font = obj.font()
    apply_font_properties(_font, **kwargs)
    obj.setFont(_font)


def apply_font_properties(font_obj: QFont, **kwargs: Any):
    """
    Set font properties from a supplied dict.

    This function takes a dictionary (i.e., keyword arguments) and iterates
    through all keys. Keys will be interpreted in Qt style: A "property: 12"
    entry in the dictionary will verify that the font object has a
    "setProperty" method and will then call "font_obj.setProperty(12)". The
    verification that methods exist allows this function to take the full
    kwargs of any object without the need to filter out non-related keys.

    Note that the object is modified in place and no explicit return is given.

    Parameters
    ----------
    font_obj : QFont
        The QFont instance.
    **kwargs : Any
        A dictionary with properties to be set.
    """
    if "fontsize" in kwargs and "pointSize" not in kwargs:
        kwargs["pointSize"] = kwargs.get("fontsize")
    for _key in kwargs:
        _name = f"set{_key[0].upper()}{_key[1:]}"
        if hasattr(font_obj, _name):
            _func = getattr(font_obj, _name)
            _func(*_get_args_as_list(kwargs.get(_key)))


def check_pydidas_qapp_instance() -> None | NoReturn:
    """
    Check if the QtWidgets.QApplication instance is a PydidasQApplication.

    If it is not, the function will raise a RuntimeError. This is used to
    ensure that Pydidas is running in a PydidasQApplication instance.
    """
    _app = QtWidgets.QApplication.instance()
    if not isinstance(_app, PydidasQApplication):
        raise RuntimeError(
            "The current QApplication instance is not a PydidasQApplication. "
            "Pydidas widgets require a PydidasQApplication instance to work properly "
            "and are not compatible with the generic QApplication."
        )

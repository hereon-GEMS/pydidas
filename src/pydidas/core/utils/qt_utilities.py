# This file is part of pydidas.
#
# Copyright 2024 - 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2024 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "update_child_qobject",
    "update_size_policy",
    "apply_qt_properties",
    "update_palette",
    "update_qwidget_font",
    "check_pydidas_qapp_instance",
    "IS_QT6",
    "qstate_is_checked",
]


from typing import Any, NoReturn

from qtpy import QT_VERSION, QtCore, QtGui, QtWidgets
from qtpy.QtCore import QObject
from qtpy.QtWidgets import QWidget

from pydidas_qtcore import PydidasQApplication


# noinspection PyTypeHints
IS_QT6: bool = QT_VERSION[0] == "6"


def _get_args_as_list(args: Any) -> list:
    """
    Format the input arguments to an iterable list to be passed as *args.

    This is used to convert strings (which are Iterable) to a list entry to
    prevent iterating over each string character.

    Parameters
    ----------
    args : Any
        Any input

    Returns
    -------
    list
        The input arguments formatted to an iterable list.
    """
    if isinstance(args, (tuple, list, set)):
        return list(args)
    return [args]


def _property_setter_name(name: str) -> str:
    """
    Generate the setter method name for a given property.

    Parameters
    ----------
    name : str
        The name of the property.

    Returns
    -------
    str
        The setter method name for the property.
    """
    return ("set" + name[0].upper() + name[1:]) if name else name


def update_child_qobject(obj: QObject, attr: str, **kwargs: Any) -> None:
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
    _child_setter = getattr(obj, _property_setter_name(attr))
    _child_setter(_child_obj)


def update_size_policy(obj: QWidget, **kwargs: Any) -> None:
    """
    Update the sizePolicy of an object with various keywords.

    Parameters
    ----------
    obj : QtWidgets.QWidget
        Any QWidget (because other QObjects do not have a sizePolicy).
    **kwargs : Any
        A dictionary with properties to set.
    """
    update_child_qobject(obj, "sizePolicy", **kwargs)


def apply_qt_properties(obj: QObject, **kwargs: Any) -> None:
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
        _setter_name = _property_setter_name(_key)
        if hasattr(obj, _setter_name):
            _setter = getattr(obj, _setter_name)
            _setter(*_get_args_as_list(kwargs.get(_key)))


def update_palette(obj: QWidget, **kwargs: Any) -> None:
    """
    Update the palette associated with a QWidget.

    Note that the object is modified in place and no explicit return is given.

    Parameters
    ----------
    obj : QtWidgets.QWidget
        The QWidget to be updated.
    **kwargs : Any
        A dictionary with palette values. Keys must correspond to palette roles.
    """
    _palette = obj.palette()
    _QPALETTE_ROLES = QtGui.QPalette.ColorRole if IS_QT6 else QtGui.QPalette
    for _key, _value in kwargs.items():
        _role = _property_setter_name(_key)
        if _role in _QPALETTE_ROLES.__dict__:
            _role_key = getattr(_QPALETTE_ROLES, _role)
            _palette.setColor(_role_key, QtGui.QColor(_value))
    obj.setPalette(_palette)


def update_qwidget_font(obj: QWidget, **kwargs: Any) -> None:
    """
    Update the font associated with a QWidget.

    Keys will be interpreted in Qt style: A "property: 12" entry in the
    kwargs dictionary will assume a corresponding setter "setProperty"
    method and will then call "font_obj.setProperty(12)". The
    verification that methods exist allows this function to take the full
    kwargs of any object without the need to filter out non-related keys.

    Note that the object is modified in place and no explicit return is given.

    Parameters
    ----------
    obj : QtWidgets.QWidget
        The QWidget to be updated.
    **kwargs : Any
        A dictionary with font properties.
    """
    _font = obj.font()
    if "fontsize" in kwargs and "pointSize" not in kwargs:
        kwargs["pointSize"] = kwargs.get("fontsize")
    for _key in kwargs:
        _setter_name = _property_setter_name(_key)
        if hasattr(_font, _setter_name):
            _setter = getattr(_font, _setter_name)
            _setter(*_get_args_as_list(kwargs.get(_key)))
    obj.setFont(_font)


def check_pydidas_qapp_instance() -> None | NoReturn:
    """
    Check if the QtWidgets.QApplication instance is a PydidasQApplication.

    If it is not, the function will raise a RuntimeError. This is used to
    ensure that Pydidas is running in a PydidasQApplication instance.
    """
    _app = QtWidgets.QApplication.instance()
    if not isinstance(_app, PydidasQApplication):
        raise RuntimeError(
            "The current QApplication instance is not a "
            "PydidasQApplication. Pydidas widgets require a "
            "PydidasQApplication instance to work properly and are not "
            "compatible with the generic QApplication."
        )


def qstate_is_checked(state: QtCore.Qt.CheckState) -> bool:
    """
    Check if the given state is checked.

    Parameters
    ----------
    state : QtCore.Qt.CheckState
        The state to check.

    Returns
    -------
    bool
        True if the state is checked, False otherwise.
    """
    # In Qt6, Qt.CheckState is an enum.Enum, and `.value` is used to get
    # the integer value. In Qt5, no `.value` is available and the
    # Qt.CheckState holds the integer value directly.
    return state == getattr(QtCore.Qt.Checked, "value", QtCore.Qt.Checked)

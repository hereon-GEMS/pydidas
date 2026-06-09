# This file is part of pydidas.
#
# Copyright 2025 - 2026, Helmholtz-Zentrum Hereon
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
Module with the QtSingleton class for implementing thread-safe singletons.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["QtSingleton"]


import copy as copy_module
from typing import Any, Callable, ClassVar

from qtpy.QtCore import QObject  # type: ignore[import-not-found]

from pydidas.core.object_with_parameter_collection import ObjectWithParameterCollection
from pydidas.core.parameter_collection import ParameterCollection


def _get_base_class(obj: Any) -> type[ObjectWithParameterCollection]:
    """
    Get the base class for a singleton object.

    Parameters
    ----------
    obj : Any
        The singleton object instance.

    Returns
    -------
    type[ObjectWithParameterCollection]
        The base class for the singleton.
    """
    # Imported here to avoid circular reference before class definition
    return QtSingleton._base_classes[obj.__class__]  # type: ignore[attr-defined]


def _make_copy(self: Any, copy_function: Callable) -> object:
    """
    Make a copy of the base class with the specified copy function.

    This is used when the base class doesn't have a custom __copy__ or
    __deepcopy__ method. It creates a new base class instance and copies
    the params and config attributes.

    Parameters
    ----------
    self : Any
        The singleton object instance.
    copy_function : Callable
        The copy function to use (copy.copy or copy.deepcopy).

    Returns
    -------
    object
        The copied object.
    """
    _base_class = _get_base_class(self)
    _copy_instance = _base_class()
    _param_copy: ParameterCollection = copy_function(  # type: ignore[type]
        getattr(self, "params", ParameterCollection())
    )
    if hasattr(_copy_instance, "add_params"):
        _copy_instance.add_params(_param_copy)
    _config_copy: dict[str, Any] = copy_function(getattr(self, "_config", {}))
    if _config_copy:
        _copy_instance._config = _config_copy
    return _copy_instance


def __copy__(self: Any) -> object:
    """Create a copy as the base class, not the singleton."""
    _base_class = _get_base_class(self)
    if hasattr(_base_class, "__copy__"):
        # Use temp instance to ensure custom __copy__ doesn't trigger singleton
        _temp = _base_class.__new__(_base_class)
        _temp.__dict__.update(self.__dict__)
        return _base_class.__copy__(_temp)
    return _make_copy(self, copy_module.copy)


def __deepcopy__(self: Any, _memo: dict = {}) -> object:
    """Create a deep copy as the base class, not the singleton."""
    _base_class = _get_base_class(self)
    if hasattr(_base_class, "__deepcopy__"):
        # Use temp instance to ensure custom __deepcopy__ doesn't trigger singleton
        _temp = _base_class.__new__(_base_class)
        _temp.__dict__.update(self.__dict__)
        return _base_class.__deepcopy__(_temp, _memo)
    return _make_copy(self, copy_module.deepcopy)


def reset_instance(kls: type) -> None:
    """
    Reset the singleton instance.

    This allows a fresh instance to be created on the next instantiation.
    Useful for testing or reinitializing singleton state.

    Parameters
    ----------
    kls : type
        The singleton class to reset.
    """
    QtSingleton.reset_instance(kls)


class QtSingleton(type(QObject)):
    """
    Metaclass to implement singleton pattern for QObjects.

    This class provides singleton functionality using the `__new__()` method,
    avoiding metaclass conflicts with `QtCore.QObject`.

    Class Attributes
    ----------------
    _instances : ClassVar[dict[type, Any]]
        Dictionary mapping each subclass to its singleton instance.
    """

    _instances: ClassVar[dict[type, type[QObject] | None]] = {}
    _base_classes: ClassVar[dict[type, type[QObject]]] = {}

    def __new__(cls, name: str, bases: tuple[type], dct: dict) -> "QtSingleton":
        """
        Create a new singleton context class with copy redirection.

        Parameters
        ----------
        name : str
            The name of the new class being created.
        bases : tuple[type]
            The base classes for the new class.
        dct : dict
            The class dictionary containing class attributes and methods.

        Returns
        -------
        QtSingleton
            The newly created singleton metaclass instance.
        """
        # Get the first base class which is not a QtSingleton:
        _base_class: type[ObjectWithParameterCollection] = ObjectWithParameterCollection
        if bases:
            _non_context_bases = list(
                _b for _b in bases[0].__mro__ if type(_b) is not cls
            )
            if _non_context_bases:
                _base_class = _non_context_bases[0]  # type: ignore[assignment]

        # Add required methods to class dictionary
        dct["__copy__"] = __copy__
        dct["__deepcopy__"] = __deepcopy__
        dct["_make_copy"] = _make_copy
        if hasattr(_base_class, "copy"):
            dct["copy"] = __copy__
        if hasattr(_base_class, "deepcopy"):
            dct["deepcopy"] = __deepcopy__
        dct["reset_instance"] = classmethod(reset_instance)

        _singleton_class = super().__new__(cls, name, bases, dct)
        cls._base_classes[_singleton_class] = _base_class
        return _singleton_class

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:  # type: ignore[reportSelfClsParameterName]
        """
        Intercept instance creation to implement singleton + init skip.

        Parameters
        ----------
        *args: Any
            Positional arguments (unused, for compatibility).
        **kwargs: Any
            Keyword arguments (unused, for compatibility).
        """
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

    @classmethod
    def get_base_class(cls, kls: type) -> type[object]:
        """
        Get the base class of the singleton class.

        Parameters
        ----------
        kls : type
            The singleton class to get the base class from.

        Returns
        -------
        type[object]
            The base class of the singleton class.
        """
        _base_class: type[object] | None = cls._base_classes.get(kls, None)
        if _base_class is None:
            raise KeyError(
                f"The class type {kls} is not stored in the singleton instance."
            )
        return _base_class

    @classmethod
    def reset_instance(cls, kls: type[QObject]) -> None:
        """
        Reset the singleton instance.

        Parameters
        ----------
        kls : type[QObject]
            The singleton class to reset.
        """
        if kls in QtSingleton._instances:  # type: ignore[attr-defined]
            del QtSingleton._instances[kls]  # type: ignore[attr-defined]

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
Module with singleton metaclass factory for implementing thread-safe singletons.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["QtSingleton", "Singleton", "create_singleton_metaclass"]


import copy as copy_module
from typing import Any, Callable, ClassVar

from qtpy.QtCore import QObject  # type: ignore[import-not-found]

from pydidas.core.object_with_parameter_collection import ObjectWithParameterCollection
from pydidas.core.parameter_collection import ParameterCollection


def _fallback_copy(obj: Any, base_class: type, copy_func: Callable) -> Any:
    """
    Create a copy of obj with fallback copy method.

    Parameters
    ----------
    obj : Any
        The object to be copied.
    base_class : type
        The base class to use for copying.
    copy_func : Callable
        The copy function to use (copy or deepcopy).

    Returns
    -------
    Any
        A copy of the object.
    """
    # Fall back to default copy
    _copy_instance = base_class()
    if hasattr(_copy_instance, "add_params"):
        _param_copy: ParameterCollection = copy_func(  # type: ignore[type]
            getattr(obj, "params", ParameterCollection())
        )
        _copy_instance.add_params(_param_copy)
    _config_copy: dict[str, Any] = copy_func(getattr(obj, "_config", {}))
    if _config_copy:
        _copy_instance._config = _config_copy
    return _copy_instance


def create_singleton_metaclass(  # noqa: C901
    base_metaclass: type = type, name: str | None = None
) -> type:
    """
    Create a singleton metaclass that inherits from the specified base metaclass.

    This factory function generates singleton metaclasses that work with any
    base metaclass, including `type` for regular objects and `type(QObject)`
    for Qt objects.

    Parameters
    ----------
    base_metaclass : type, optional
        The base metaclass to inherit from. Default is `type` for regular
        Python objects. Can also be `type(QObject)` for Qt compatibility.
    name : str or None, optional
        Name of the created metaclass. If None, the default name will be
        used. Default is None.

    Returns
    -------
    type
        A new singleton metaclass.
    """

    class _SingletonMeta(base_metaclass):  # type: ignore[misc,valid-type]
        """Singleton metaclass implementation."""

        _instances: ClassVar[dict[type, Any]] = {}
        _base_classes: ClassVar[dict[type, type]] = {}

        @staticmethod
        def _instance_copy(obj: Any) -> object:
            """Create a copy as base class, not singleton."""
            _bc = obj.__class__.get_base_class(obj.__class__)
            if hasattr(_bc, "__copy__"):
                _temp = _bc.__new__(_bc)  # type: ignore[misc]
                _temp.__dict__.update(obj.__dict__)  # type: ignore[union-attr]
                return _bc.__copy__(_temp)
            return _fallback_copy(obj, _bc, copy_module.copy)

        @staticmethod
        def _instance_deepcopy(obj: Any, _memo: dict | None = None) -> object:
            """Create a deep copy as base class, not singleton."""
            if _memo is None:
                _memo = {}
            _bc = obj.__class__.get_base_class(obj.__class__)
            if hasattr(_bc, "__deepcopy__"):
                _temp = _bc.__new__(_bc)  # type: ignore[misc]
                _temp.__dict__.update(obj.__dict__)  # type: ignore[union-attr]
                return _bc.__deepcopy__(_temp, _memo)
            return _fallback_copy(obj, _bc, copy_module.deepcopy)

        def __new__(cls, name_: str, bases: tuple[type], dct: dict) -> "_SingletonMeta":
            """
            Create a new singleton class with copy redirection.

            Parameters
            ----------
            name_ : str
                The name of the new class being created.
            bases : tuple[type]
                The base classes for the new class.
            dct : dict
                The class dictionary containing class attributes and methods.

            Returns
            -------
            _SingletonMeta
                The newly created singleton metaclass instance.
            """
            # Get the first base class which is not a singleton. If no base
            # class was found, this reverts to ObjectWithParameterCollection:
            _base_class: type = ObjectWithParameterCollection
            if bases:
                _non_singleton_bases = list(
                    _b for _b in bases[0].__mro__ if type(_b) is not cls
                )
                if _non_singleton_bases:
                    _base_class = _non_singleton_bases[0]

            # Add methods from metaclass to instance methods
            dct["__copy__"] = cls._instance_copy
            dct["__deepcopy__"] = cls._instance_deepcopy
            if hasattr(_base_class, "copy"):
                dct["copy"] = cls._instance_copy
            if hasattr(_base_class, "deepcopy"):
                dct["deepcopy"] = cls._instance_deepcopy
            dct["reset_instance"] = classmethod(
                lambda kls: cls._reset_instance(kls)  # type: ignore[arg-type]
            )

            _singleton_class = super().__new__(cls, name_, bases, dct)
            cls._base_classes[_singleton_class] = _base_class
            return _singleton_class

        def __call__(cls, *args: Any, **kwargs: Any) -> Any:  # type: ignore[override]
            """
            Intercept instance creation to implement singleton.

            Parameters
            ----------
            *args: Any
                Positional arguments.
            **kwargs: Any
                Keyword arguments.

            Returns
            -------
            Any
                The singleton instance for this class.
            """
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
            return cls._instances[cls]

        @classmethod
        def _reset_instance(cls, kls: type) -> None:
            """
            Reset singleton instance.

            Parameters
            ----------
            kls : type
                The singleton class to reset.
            """
            if kls in cls._instances:
                del cls._instances[kls]

        @classmethod
        def get_base_class(cls, kls: type) -> type:
            """
            Get the non-singleton base class for a given singleton class.

            Parameters
            ----------
            kls : type
                The singleton class to get the base class for.

            Returns
            -------
            type
                The non-singleton base class.
            """
            _base_class = cls._base_classes.get(kls)
            if _base_class is None:
                raise KeyError(
                    f"The class type {kls} is not stored in the singleton instance."
                )
            return _base_class

    _name = name or _SingletonMeta.__name__
    _SingletonMeta.__name__ = _name
    _SingletonMeta.__qualname__ = _name
    return _SingletonMeta


# Create concrete metaclass instances
QtSingleton = create_singleton_metaclass(type(QObject), "QtSingleton")
Singleton = create_singleton_metaclass(type, "Singleton")

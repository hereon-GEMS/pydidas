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


import copy
from typing import Any, ClassVar

from qtpy.QtCore import QObject  # type: ignore[import-not-found]

from pydidas.core.object_with_parameter_collection import ObjectWithParameterCollection
from pydidas.core.parameter_collection import ParameterCollection


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
        # Store original __copy__ and __deepcopy__ if they exist
        original_copy = dct.get("__copy__")
        original_deepcopy = dct.get("__deepcopy__")

        # Get the first base class which is not instantiated through the
        # QtSingleton:
        _base_class = ObjectWithParameterCollection
        if bases:
            _non_context_bases = list(
                _b for _b in bases[0].__mro__ if type(_b) is not cls
            )
            if _non_context_bases:
                _base_class = _non_context_bases[0]

        if not issubclass(_base_class, ObjectWithParameterCollection):
            raise TypeError(
                "The QtSingleton class must inherit from "
                "ObjectWithParameterCollection or derived classes."
            )

        def __copy__(self):
            """Create a copy as the base class, not the singleton."""
            _copy_instance = _base_class()
            _copy_instance.params = copy.copy(  # type: ignore[type]
                getattr(self, "params", ParameterCollection())
            )
            _copy_instance._config = copy.copy(self._config)
            return _copy_instance

        def __deepcopy__(self, _memo):
            """Create a deep copy as the base class, not the singleton."""
            _copy_instance = _base_class()
            _copy_instance.params = self.params.copy()
            _copy_instance._config = copy.deepcopy(self._config)
            return _copy_instance

        dct["__copy__"] = original_copy or __copy__
        dct["__deepcopy__"] = original_deepcopy or __deepcopy__

        return super().__new__(cls, name, bases, dct)

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

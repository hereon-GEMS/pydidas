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
Module with the SingletonQObject
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["SingletonObject"]


import warnings
from typing import Any, NoReturn


class SingletonObject:
    """
    Class which includes the necessary code to create classes only as Singletons.

    Implementations must inherit from SingletonObject first to assert the correct
    method resolution order for calling methods.
    """

    _instance = None
    _initialized = False

    @classmethod
    def reset_instance(cls) -> None:
        """
        Reset the instance of the singleton object.

        This method is intended for testing purposes only and should not be used
        in production code.
        """
        cls._instance = None
        cls._initialized = False

    def __new__(cls, *args: Any, **kwargs: Any) -> "SingletonObject":
        """Create a new instance of the class if it does not exist yet."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, *args: Any, **kwargs: Any):
        if self._initialized:
            if args != () or kwargs != {}:
                warnings.warn(
                    "The instance of this class has already been created, "
                    "and the arguments and keyword arguments have been ignored.",
                    UserWarning,
                )
            return
        self.__class__._initialized = True

        _skip_base_init = kwargs.pop("skip_base_init", False)
        # Only call super().__init__ if there are multiple bases:
        if len(self.__class__.__bases__) > 1 and not _skip_base_init:
            for base in self.__class__.__bases__:
                if base is not SingletonObject and hasattr(base, "__init__"):
                    base.__init__(self, *args, **kwargs)
        self.initialize(*args, **kwargs)

    def initialize(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the singleton object.

        This method should be overridden by subclasses which have additional
        mixin-classes to perform any necessary initialization. Using the initialize
        method instead of __init__ is required to avoid multiple initializations
        through the SingletonObject.

        Parameters
        ----------
        args : Any
            Positional arguments for the initialization.
        kwargs : Any
            Keyword arguments for the initialization.
        """
        pass

    def __copy__(self) -> NoReturn:
        """
        Prevent copying of the singleton instance.

        Raises
        -------
        TypeError
            Always.
        """
        raise TypeError("SingletonObject instances cannot be copied.")

    def copy(self) -> NoReturn:
        """Wrapper for the __copy__ method."""
        return self.__copy__()


# class SingletonObjectNew(type):
#     """
#     Metaclass to implement singleton pattern for any object.
#
#     This class provides singleton functionality using the `__new__()` method.
#
#     Class Attributes
#     ----------------
#     _instances : ClassVar[dict[type, Any]]
#         Dictionary mapping each subclass to its singleton instance.
#     """
#
#     _instances: ClassVar[dict[type, type | None]] = {}
#
#     def __new__(cls, name: str, bases: tuple[type], dct: dict) -> "SingletonObject":
#         """
#         Create a new singleton context class with copy redirection.
#
#         Parameters
#         ----------
#         name : str
#             The name of the new class being created.
#         bases : tuple[type]
#             The base classes for the new class.
#         dct : dict
#             The class dictionary containing class attributes and methods.
#
#         Returns
#         -------
#         QtSingleton
#             The newly created singleton metaclass instance.
#         """
#         # Store original __copy__ and __deepcopy__ if they exist
#         original_copy = dct.get("__copy__")
#         original_deepcopy = dct.get("__deepcopy__")
#
#         # Get the first base class which is not instantiated through the
#         # SingletonObject:
#         _base_class = object
#         if bases:
#             _non_context_bases = list(
#                 _b for _b in bases[0].__mro__ if type(_b) is not cls
#             )
#             if _non_context_bases:
#                 _base_class = _non_context_bases[0]
#
#         def __copy__(self):
#             """Create a copy as the base class, not the singleton."""
#             _copy_instance = _base_class()
#             _copy_instance.params = copy.copy(  # type: ignore[type]
#                 getattr(self, "params", ParameterCollection())
#             )
#             _copy_instance._config = copy.copy(self._config)
#             return _copy_instance
#
#         def __deepcopy__(self, _memo):
#             """Create a deep copy as the base class, not the singleton."""
#             _copy_instance = _base_class()
#             _copy_instance.params = self.params.copy()
#             _copy_instance._config = copy.deepcopy(self._config)
#             return _copy_instance
#
#         dct["__copy__"] = original_copy or __copy__
#         dct["__deepcopy__"] = original_deepcopy or __deepcopy__
#
#         return super().__new__(cls, name, bases, dct)
#
#     def __call__(cls, *args: Any, **kwargs: Any) -> Any:  # type: ignore[reportSelfClsParameterName]
#         """
#         Intercept instance creation to implement singleton + init skip.
#
#         Parameters
#         ----------
#         *args: Any
#             Positional arguments (unused, for compatibility).
#         **kwargs: Any
#             Keyword arguments (unused, for compatibility).
#         """
#         if cls not in cls._instances:
#             cls._instances[cls] = super().__call__(*args, **kwargs)
#         return cls._instances[cls]

# This file is part of pydidas.
#
# Copyright 2025, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
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

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
        super().__init__(*args, **kwargs)

    def __copy__(self) -> NoReturn:
        """
        Prevent copying of the singleton instance.

        Raises
        -------
        TypeError
            Always.
        """
        raise TypeError("SingletonQObject instances cannot be copied.")

    def copy(self) -> NoReturn:
        """Wrapper for the __copy__ method."""
        return self.__copy__()

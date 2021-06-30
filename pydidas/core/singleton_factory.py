# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""Module with the SingletonFactory class which is used to create Singleton
instances of clases.."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL 3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['SingletonFactory']


class SingletonFactory:
    """
    Factory to create a Singleton.
    """
    def __init__(self, cls):
        """
        Setup method.
        """
        self.__instance = None
        self.__class = cls

    def __call__(self):
        """
        Get the instance of the Singleton.

        Returns
        -------
        object
            The instance of the Singleton class.
        """
        if not self.__instance:
            self.__instance = self.__class()
        return self.__instance

    def __reset_singleton(self):
        """
        Reset the Singleton instance and create a new one.
        """
        self.__instance = self.__class()

    def instance(self):
        """
        Get the instance. A wrapper for __call__
        """
        return self.__call__()

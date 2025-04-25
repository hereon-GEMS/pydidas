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
__all__ = ["SingletonQObject"]


from qtpy import QtCore


class SingletonQObject(QtCore.QObject):
    """
    Class which includes the necessary code to create classes only as Singletons.

    Implementations cannot inherit from other classes and must use the
    `initialize` method to set up the class instead of the `__init__` method.
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        """Create a new instance of the class if it does not exist yet."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, parent: QtCore.QObject | None = None):
        if self._initialized:
            return
        SingletonQObject.__init__(self, parent)
        self.initialize()
        self._initialized = True

    def initialize(self):
        """
        Initialize the class instance.

        This method should be implemented in the custom classes, if required.
        """
        pass

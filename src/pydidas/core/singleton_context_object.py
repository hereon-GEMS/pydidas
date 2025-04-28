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
Module with the SingletonContextObject
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["SingletonContextObject"]


from pydidas.core import ObjectWithParameterCollection


class SingletonContextObject(ObjectWithParameterCollection):
    """
    Class which includes the necessary code to create classes only as Singletons.

    Implementations cannot inherit from other classes and must use the
    `initialize` method to set up the class instead of the `__init__` method.

    This method will try to fetch and restore the parameter values  from the
    QSettings, if values have been set.
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        """Create a new instance of the class if it does not exist yet."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        ObjectWithParameterCollection.__init__(self)
        self.set_default_params()
        for _key, _param in self.params.items():
            _stored_val = self.q_settings_get(_key, default=None)
            if _stored_val is not None:
                self.set_param_value(_key, _stored_val)
        self.initialize()
        self._initialized = True

    def initialize(self):
        """
        Initialize the class instance.

        This method should be implemented in the custom classes, if required.
        """
        pass

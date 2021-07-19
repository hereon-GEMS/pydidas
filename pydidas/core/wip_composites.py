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

"""The composites module includes the Composite class for handling composite image data."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['Composites']

import multiprocessing
import numpy as np


class _CompositesFactory:
    """
    Singleton factory to make sure that only one CompositesCollection exists
    at runtime.
    """
    def __init__(self):
        self._instance = None

    def __call__(self, plugin_path=None):
        if not self._instance:
            self._instance = _Composites()
        return self._instance

Composites = _CompositesFactory()


class _Composites:
    """
    WIP ...

    Handle composite data which spans individual images
    """

    def __init__(self):
        self.__composites = {}
        self.__scan = None
        self.__lock = multiprocessing.Lock()

    def set_scan(self, scan):
        if True:
            ...
            #TODO: include class type check
        self.__scan = scan

    def new_composite(self, name, dtype=np.float32):
        if name in self.__composites:
            raise KeyError(f'The composite name {name} already exists.')
        self.__composites[name] = np.zeros((self.__scan.dim), dtype=dtype)

    def set_value(self, name, image_no, value):
        if name not in self.__composites:
            raise KeyError(f'The composite name {name} does not exists.')
        coords = self.__scan.get_image_pos(image_no)
        self.__lock.acquire()
        self.__composites[name][coords] = value
        self.__lock.release()

# MIT License
#
# Copyright (c) 2021 Malte Storm, Helmholtz-Zentrum Hereon
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""The composites module includes the Composite class for handling composite image data."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['Composites']

# from collections import OrderedDict
import numbers
import multiprocessing
import numpy as np

class _CompositesFactory:
    """
    Singleton factory to make sure that only one PluginCollection exists
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
    """Handle composite data which spans individual images
    """

    def __init__(self):
        self.__composites = {}
        self.__scan = None
        self.__lock = multiprocessing.Lock()

    def set_scan(self, scan):
        if True:
            ...
            #To do: include class type check
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

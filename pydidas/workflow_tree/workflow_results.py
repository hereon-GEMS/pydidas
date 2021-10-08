# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""The composites module includes the Composite class for handling composite image data."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['WorkflowResults']

import multiprocessing
import numpy as np

from ..core.singleton_factory import SingletonFactory
from ..core.scan_settings import ScanSettings
from .workflow_tree import WorkflowTree

SCAN = ScanSettings()

TREE = WorkflowTree()

class _WorkflowResults:
    """
    WorkflowResults is a class for handling composite data which spans
    individual images
    """

    def __init__(self):
        self.__composites = {}

    def update_shape_from_scan(self):
        """
        Update the shape of the results from the ScanSettings.
        """



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


WorkflowResults = SingletonFactory(_WorkflowResults)

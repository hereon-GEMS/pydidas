# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import unittest
import tempfile
import shutil
import os

import numpy as np

from pydidas.data_io import export_data, import_data


class TestImportExport(unittest.TestCase):
    def setUp(self):
        self._shape = np.array((10, 5, 20, 8, 3))
        self._data = np.random.random(self._shape)
        self._2dshape = np.array((37, 15))
        self._2dimage = np.random.random(self._2dshape)
        self._dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self._dir)

    def test_export_data(self):
        _fname = os.path.join(self._dir, "test.npy")
        export_data(_fname, self._data)
        _data = np.load(_fname)
        self.assertTrue(np.allclose(_data, self._data))

    def test_import_data(self):
        _fname = os.path.join(self._dir, "test.npy")
        np.save(_fname, self._data)
        _data = import_data(_fname)
        self.assertTrue(np.allclose(_data, self._data))


if __name__ == "__main__":
    unittest.main()

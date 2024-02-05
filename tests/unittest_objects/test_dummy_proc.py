# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import pickle
import unittest

import numpy as np

from pydidas.core import Dataset
from pydidas.unittest_objects.dummy_proc import DummyProc


class TestDummyProc(unittest.TestCase):
    def setUp(self): ...

    def tearDown(self): ...

    def test_init(self):
        plugin = DummyProc()
        self.assertIsInstance(plugin, DummyProc)
        self.assertFalse(plugin._preexecuted)
        self.assertFalse(plugin._executed)

    def test_pre_execute(self):
        plugin = DummyProc()
        plugin.pre_execute()
        self.assertTrue(plugin._preexecuted)

    def test_execute(self):
        _shape = (12, 12)
        _offset = np.random.random()
        plugin = DummyProc()
        _data = np.random.random(_shape)
        _newdata, _kws = plugin.execute(_data, offset=_offset)
        self.assertIsInstance(_newdata, Dataset)
        self.assertTrue(np.allclose(_data + _offset, _newdata))

    def test_pickle_unpickle(self):
        plugin = DummyProc()
        new_plugin = pickle.loads(pickle.dumps(plugin))
        self.assertIsInstance(new_plugin, DummyProc)


if __name__ == "__main__":
    unittest.main()

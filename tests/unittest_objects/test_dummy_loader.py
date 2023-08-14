# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import pickle
import unittest

from pydidas.core import Dataset
from pydidas.core.utils import get_random_string
from pydidas.unittest_objects import DummyLoader


class TestDummyLoader(unittest.TestCase):
    def setUp(self):
        ...

    def tearDown(self):
        ...

    def test_init(self):
        plugin = DummyLoader()
        self.assertIsInstance(plugin, DummyLoader)
        self.assertFalse(plugin._preexecuted)

    def test_get_first_file_size(self):
        plugin = DummyLoader()
        self.assertEqual(plugin.get_first_file_size(), 1)

    def test_get_filename(self):
        plugin = DummyLoader()
        _s = get_random_string(8)
        self.assertEqual(plugin.get_filename(_s), _s)

    def test_input_available__true(self):
        plugin = DummyLoader()
        plugin._config["input_available"] = 7
        self.assertTrue(plugin.input_available(6))

    def test_input_available__false(self):
        plugin = DummyLoader()
        plugin._config["input_available"] = 7
        self.assertFalse(plugin.input_available(8))

    def test_pre_execute(self):
        plugin = DummyLoader()
        plugin.pre_execute()
        self.assertTrue(plugin._preexecuted)

    def test_execute(self):
        _shape = (134, 54)
        _index = 37
        plugin = DummyLoader()
        plugin.set_param_value("image_height", _shape[0])
        plugin.set_param_value("image_width", _shape[1])
        _newdata, _kws = plugin.execute(_index)
        self.assertIsInstance(_newdata, Dataset)
        self.assertEqual(_newdata.shape, _shape)
        self.assertEqual(_kws["index"], _index)

    def test_pickle_unpickle(self):
        plugin = DummyLoader()
        new_plugin = pickle.loads(pickle.dumps(plugin))
        self.assertIsInstance(new_plugin, DummyLoader)


if __name__ == "__main__":
    unittest.main()

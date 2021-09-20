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

"""Unit tests for pydidas modules."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import unittest
import numpy as np

from pydidas.unittest_objects.mp_test_app import MpTestApp
from pydidas.apps import BaseApp


class TestMpTestApp(unittest.TestCase):

    def setUp(self):
        self._indices = (3, 57)

    def tearDown(self):
        ...

    def test_create(self):
        app = MpTestApp()
        self.assertIsInstance(app, BaseApp)

    def test_mp_pre_run(self):
        app = MpTestApp()
        app.multiprocessing_pre_run()
        self.assertTrue(app._config['mp_pre_run_called'])

    def test_mp_get_tasks(self):
        app = MpTestApp()
        app._config['min_index'] = self._indices[0]
        app._config['max_index'] = self._indices[1]
        app.multiprocessing_pre_run()
        _tasks = app.multiprocessing_get_tasks()
        self.assertEqual(_tasks, range(*self._indices))

    def test_mp_func(self):
        app = MpTestApp()
        app._config['min_index'] = self._indices[0]
        app._config['max_index'] = self._indices[1]
        app.multiprocessing_pre_run()
        _image = app.multiprocessing_func(self._indices[0])
        self.assertIsInstance(_image, np.ndarray)

    def test_mp_post_run(self):
        app = MpTestApp()
        app.multiprocessing_post_run()
        self.assertTrue(app._config['mp_post_run_called'])

    def test_mp_store_results(self):
        app = MpTestApp()
        app._config['min_index'] = self._indices[0]
        app._config['max_index'] = self._indices[1]
        app.multiprocessing_pre_run()
        _image = app.multiprocessing_func(self._indices[0])
        app.multiprocessing_store_results(self._indices[0], _image)
        self.assertTrue((app._composite.image[:20, :20] > 0).all())

    def test_mp_wait(self):
        app = MpTestApp()
        self.assertEqual(app.multiprocessing_carryon(), False)
        self.assertEqual(app.multiprocessing_carryon(), True)


if __name__ == "__main__":
    unittest.main()

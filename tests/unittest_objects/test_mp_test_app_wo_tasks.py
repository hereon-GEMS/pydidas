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


import unittest

import numpy as np

from pydidas.core import BaseApp
from pydidas.unittest_objects.mp_test_app_wo_tasks import MpTestAppWoTasks


class TestMpTestAppWoTasks(unittest.TestCase):
    def setUp(self):
        self._indices = (3, 57)

    def tearDown(self): ...

    def test_create(self):
        app = MpTestAppWoTasks()
        self.assertIsInstance(app, BaseApp)

    def test_mp_pre_run(self):
        app = MpTestAppWoTasks()
        app.multiprocessing_pre_run()
        self.assertTrue(app._config["run_prepared"])

    def test_mp_get_tasks(self):
        app = MpTestAppWoTasks()
        app.multiprocessing_pre_run()
        _tasks = app.multiprocessing_get_tasks()
        self.assertEqual(_tasks, [])

    def test_mp_func(self):
        app = MpTestAppWoTasks()
        app._config["min_index"] = self._indices[0]
        app._config["max_index"] = self._indices[1]
        app.multiprocessing_pre_run()
        _index, _image = app.multiprocessing_func(self._indices[0])
        self.assertIsInstance(_index, int)
        self.assertIsInstance(_image, np.ndarray)

    def test_mp_post_run(self):
        app = MpTestAppWoTasks()
        app.multiprocessing_post_run()
        self.assertTrue(app._config["mp_post_run_called"])

    def test_mp_store_results(self):
        app = MpTestAppWoTasks()
        app._config["min_index"] = self._indices[0]
        app._config["max_index"] = self._indices[1]
        app.multiprocessing_pre_run()
        _index, _image = app.multiprocessing_func(self._indices[0])
        app.multiprocessing_store_results(self._indices[0], _image)
        self.assertTrue((app._composite.image[:20, :20] > 0).all())

    def test_mp_wait(self):
        app = MpTestAppWoTasks()
        self.assertEqual(app.multiprocessing_carryon(), False)
        self.assertEqual(app.multiprocessing_carryon(), True)


if __name__ == "__main__":
    unittest.main()

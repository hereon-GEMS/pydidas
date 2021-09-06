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
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import copy
import os
import unittest
from unittest import mock
import tempfile
import shutil
from pathlib import Path
import sys

import numpy as np
import h5py

from pydidas.apps import BaseApp
from pydidas.core import (ParameterCollection,
                          get_generic_parameter, CompositeImage)


class TestApp(BaseApp):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stored = []

    def multiprocessing_pre_run(self):
        pass

    def multiprocessing_post_run(self):
        pass

    def multiprocessing_get_tasks(self):
        return [1, 2, 3]

    def multiprocessing_pre_cycle(self, *args):
        """
        Perform operations in the pre-cycle of every task.
        """
        return

    def multiprocessing_func(self, *args):
        return args

    def multiprocessing_store_results(self, task, result):
        self.stored.append(result[0])


class TestBaseApp(unittest.TestCase):

    def setUp(self):
        ...

    def tearDown(self):
        ...

    def test_creation(self):
        app = BaseApp()
        self.assertIsInstance(app, BaseApp)

    def test_creation_with_args(self):
        _nx = get_generic_parameter('composite_nx')
        _nx.value = 10
        _ny = get_generic_parameter('composite_ny')
        _ny.value = 5
        _dir = get_generic_parameter('composite_dir')
        _dir.value = 'y'
        _args = ParameterCollection(_nx, _ny, _dir)
        app = BaseApp(_args)
        self.assertEqual(app.get_param_value('composite_nx'), _nx.value)
        self.assertEqual(app.get_param_value('composite_ny'), _ny.value)
        self.assertEqual(app.get_param_value('composite_dir'), _dir.value)

    def test_multiprocessing_pre_run(self):
        app = BaseApp()
        with self.assertRaises(NotImplementedError):
            app.multiprocessing_pre_run()

    def test_multiprocessing_post_run(self):
        app = BaseApp()
        with self.assertRaises(NotImplementedError):
            app.multiprocessing_post_run()

    def test_multiprocessing_get_tasks(self):
        app = BaseApp()
        with self.assertRaises(NotImplementedError):
            app.multiprocessing_get_tasks()

    def test_multiprocessing_pre_cycle(self):
        app = BaseApp()
        self.assertIsNone(app.multiprocessing_pre_cycle())

    def test_multiprocessing_func(self):
        app = BaseApp()
        with self.assertRaises(NotImplementedError):
            app.multiprocessing_func(None)

    def test_multiprocessing_carryon(self):
        app = BaseApp()
        self.assertTrue(app.multiprocessing_carryon())

    def test_get_config(self):
        app = BaseApp()
        self.assertEqual(app.get_config(), {})

    def test_copy(self):
        app = BaseApp()
        _copy = app.copy()
        self.assertNotEqual(app, _copy)
        self.assertIsInstance(_copy, BaseApp)

    def test_run(self):
        app = TestApp()
        app.run()
        self.assertEqual(app.stored, app.multiprocessing_get_tasks())

    def test_parse_func(self):
        app = BaseApp()
        self.assertIsNone(app.parse_func)

    def test_set_parse_func(self):
        def dummy(obj):
            return {0: hash(self)}
        BaseApp.parse_func = dummy
        app = BaseApp()
        self.assertEqual(dummy(None), app.parse_func())


if __name__ == "__main__":
    unittest.main()

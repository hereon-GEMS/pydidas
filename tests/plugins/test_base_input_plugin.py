# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import os
import pickle
import shutil
import tempfile
import unittest

import h5py
import numpy as np

from pydidas.contexts import ScanContext
from pydidas.core import Dataset, Parameter
from pydidas.core.constants import INPUT_PLUGIN
from pydidas.core.utils import get_random_string
from pydidas.data_io import export_data, import_data
from pydidas.plugins import InputPlugin
from pydidas.unittest_objects import create_plugin_class


_DUMMY_SHAPE = (130, 140)

SCAN = ScanContext()


class TestInputPlugin(InputPlugin):
    def __init__(self, filename=""):
        InputPlugin.__init__(self)
        self.filename_string = filename

    def get_frame(self, index, **kwargs):
        _frame = index * SCAN.get_param_value(
            "scan_index_stepping"
        ) + SCAN.get_param_value("scan_start_index")
        kwargs["indices"] = (_frame,)
        return import_data(self.filename_string, **kwargs), kwargs

    def update_filename_string(self):
        pass

    def get_filename(self, index):
        return self.filename_string


def dummy_update_filename_string(plugin):
    plugin.filename_string = str(plugin._image_metadata.filename)


class TestBaseInputPlugin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._testpath = tempfile.mkdtemp()
        cls._datashape = _DUMMY_SHAPE
        cls._fname = os.path.join(cls._testpath, "test.h5")
        with h5py.File(cls._fname, "w") as f:
            f["entry/data/data"] = np.repeat(
                np.arange(30, dtype=np.uint16), np.prod(_DUMMY_SHAPE)
            ).reshape((30,) + _DUMMY_SHAPE)

    @classmethod
    def tearDownClass(cls):
        SCAN.restore_all_defaults(True)
        shutil.rmtree(cls._testpath)

    def setUp(self):
        SCAN.restore_all_defaults(True)

    def tearDown(self): ...

    def test_is_basic_plugin__baseclass(self):
        for _plugin in [InputPlugin, InputPlugin()]:
            self.assertTrue(_plugin.is_basic_plugin())

    def test_is_basic_plugin__subclass(self):
        class TestPlugin(InputPlugin):
            pass

        for _plugin in [TestPlugin, TestPlugin()]:
            self.assertFalse(_plugin.is_basic_plugin())

    def test_create_base_plugin(self):
        plugin = create_plugin_class(INPUT_PLUGIN)
        self.assertIsInstance(plugin(), InputPlugin)

    def test_class_attributes(self):
        plugin = create_plugin_class(INPUT_PLUGIN)
        for att in (
            "plugin_type",
            "plugin_name",
            "default_params",
            "generic_params",
            "input_data_dim",
            "output_data_dim",
        ):
            self.assertTrue(hasattr(plugin, att))

    def test_class_generic_params(self):
        plugin = create_plugin_class(INPUT_PLUGIN)
        for att in (
            "use_roi",
            "roi_xlow",
            "roi_xhigh",
            "roi_ylow",
            "roi_yhigh",
            "binning",
        ):
            _param = plugin.generic_params.get_param(att)
            self.assertIsInstance(_param, Parameter)

    def test_get_filename(self):
        plugin = create_plugin_class(INPUT_PLUGIN)()
        _fname = plugin.get_filename(1)
        self.assertEqual(_fname, "")

    def test_input_available__file_exists_and_readable(self):
        _data = np.zeros((10, 10))
        for _ext in ["tif", "npy", "h5"]:
            with self.subTest(extension=_ext):
                _fname = os.path.join(self._testpath, f"test_dummy.{_ext}")
                export_data(_fname, _data, overwrite=True)
                plugin = TestInputPlugin(filename=_fname)
                plugin.pre_execute()
                self.assertTrue(plugin.input_available(5))

    def test_input_available__file_exists_w_no_data(self):
        for _ext in ["tif", "npy", "h5"]:
            with self.subTest(extension=_ext):
                _fname = os.path.join(self._testpath, f"test_dummy.{_ext}")
                with open(_fname, "wb") as f:
                    f.write(b"")
                plugin = TestInputPlugin(filename=_fname)
                plugin.pre_execute()
                self.assertFalse(plugin.input_available(5))

    def test_pickle(self):
        plugin = InputPlugin()
        _new_params = {get_random_string(6): get_random_string(12) for _ in range(7)}
        for _key, _val in _new_params.items():
            plugin.add_param(Parameter(_key, str, _val))
        plugin2 = pickle.loads(pickle.dumps(plugin))
        for _key in plugin.params:
            self.assertEqual(
                plugin.get_param_value(_key), plugin2.get_param_value(_key)
            )

    def test_execute__simple(self):
        plugin = TestInputPlugin(filename=self._fname)
        plugin.pre_execute()
        _data, _ = plugin.execute(0)
        self.assertIsInstance(_data, Dataset)
        self.assertTrue(np.allclose(_data, 0))

    def test_execute__w_multiplicity_and_average(self):
        SCAN.set_param_value("scan_multiplicity", 4)
        SCAN.set_param_value("scan_multi_image_handling", "Average")
        plugin = TestInputPlugin(filename=self._fname)
        plugin.pre_execute()
        _data, _ = plugin.execute(0)
        self.assertTrue(np.allclose(_data, 1.5))

    def test_execute__w_multiplicity_and_sum(self):
        SCAN.set_param_value("scan_multiplicity", 4)
        SCAN.set_param_value("scan_multi_image_handling", "Sum")
        plugin = TestInputPlugin(filename=self._fname)
        plugin.pre_execute()
        _data, _ = plugin.execute(0)
        self.assertTrue(np.allclose(_data, 6))

    def test_execute__w_multiplicity_and_max(self):
        SCAN.set_param_value("scan_multiplicity", 4)
        SCAN.set_param_value("scan_multi_image_handling", "Maximum")
        plugin = TestInputPlugin(filename=self._fname)
        plugin.pre_execute()
        _data, _ = plugin.execute(0)
        self.assertTrue(np.allclose(_data, 3))

    def test_execute__w_start_index(self):
        SCAN.set_param_value("scan_start_index", 4)
        plugin = TestInputPlugin(filename=self._fname)
        plugin.pre_execute()
        _data, _ = plugin.execute(0)
        self.assertTrue(np.allclose(_data, 4))

    def test_execute__w_start_index_w_delta(self):
        SCAN.set_param_value("scan_start_index", 4)
        SCAN.set_param_value("scan_index_stepping", 3)
        plugin = TestInputPlugin(filename=self._fname)
        plugin.pre_execute()
        _data, _ = plugin.execute(0)
        _data2, _ = plugin.execute(1)
        self.assertTrue(np.allclose(_data, 4))
        self.assertTrue(np.allclose(_data2, 7))

    def test_execute__full_complexity(self):
        SCAN.set_param_value("scan_start_index", 4)
        SCAN.set_param_value("scan_index_stepping", 3)
        SCAN.set_param_value("scan_multiplicity", 4)
        SCAN.set_param_value("scan_multi_image_handling", "Sum")
        plugin = TestInputPlugin(filename=self._fname)
        plugin.pre_execute()
        _result_0 = 4 + 7 + 10 + 13
        _result_1 = 16 + 19 + 22 + 25
        _data, _ = plugin.execute(0)
        _data_1, _ = plugin.execute(1)
        self.assertTrue(np.allclose(_data, _result_0))
        self.assertTrue(np.allclose(_data_1, _result_1))

    def test_execute__with_roi(self):
        plugin = TestInputPlugin(filename=self._fname)
        plugin.set_param_value("use_roi", True)
        plugin.set_param_value("roi_yhigh", 5)
        plugin.pre_execute()
        _data, kwargs = plugin.execute(0)

    def test_copy(self):
        plugin = TestInputPlugin(filename=self._fname)
        copy = plugin.copy()
        self.assertEqual(plugin._SCAN, SCAN)
        self.assertEqual(copy._SCAN, SCAN)


if __name__ == "__main__":
    unittest.main()

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
import shutil
import tempfile
import unittest
from numbers import Integral, Real

import numpy as np

from pydidas.contexts.scan import Scan, ScanContext
from pydidas.contexts.scan.scan_io_base import ScanIoBase
from pydidas.core import UserConfigError
from pydidas.core.utils import get_random_string


SCAN = ScanContext()
SCAN_IO = ScanIoBase


class TestScanIoBase(unittest.TestCase):
    def setUp(self):
        _test_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self._path = os.path.join(_test_dir, "_data", "load_test_scan_context_")
        self._tmppath = tempfile.mkdtemp()
        SCAN_IO.imported_params = {}

    def tearDown(self):
        del self._path
        shutil.rmtree(self._tmppath)

    def test_verify_all_entries_present__correct(self):
        for param in SCAN.params:
            SCAN_IO.imported_params[param] = True
        SCAN_IO._verify_all_entries_present()

    def test_verify_all_entries_present__missing_keys(self):
        with self.assertRaises(UserConfigError):
            SCAN_IO._verify_all_entries_present()

    def test_write_to_scan_settings__generic_ScanContext(self):
        _scan = Scan()
        for _param in _scan.params.values():
            if _param.dtype == str and _param.choices is None:
                _param.value = get_random_string(6)
            elif _param.dtype == Real:
                _param.value = np.random.random()
            elif _param.dtype == Integral and _param.refkey != "scan_dim":
                _param.value = int(100 * np.random.random())
        SCAN_IO.imported_params = _scan.get_param_values_as_dict()
        SCAN_IO._write_to_scan_settings()
        for _key, _value in _scan.get_param_values_as_dict().items():
            self.assertEqual(SCAN.get_param_value(_key), _value)

    def test_write_to_scan_settings__given_scan(self):
        _scan = Scan()
        for _param in _scan.params.values():
            if _param.dtype == str and _param.choices is None:
                _param.value = get_random_string(6)
            elif _param.dtype == Real:
                _param.value = np.random.random()
            elif _param.dtype == Integral and _param.refkey != "scan_dim":
                _param.value = int(100 * np.random.random())
        _new_scan = Scan()
        SCAN_IO.imported_params = _scan.get_param_values_as_dict()
        SCAN_IO._write_to_scan_settings(scan=_new_scan)
        SCAN.restore_all_defaults(True)
        for _key, _value in _scan.get_param_values_as_dict().items():
            self.assertEqual(_new_scan.get_param_value(_key), _value)
        self.assertEqual(SCAN.get_param_value("scan_dim1_label"), "")

    def test_convert_legacy_param_names__w_scan_start_index(self):
        SCAN_IO.imported_params = {"scan_start_index": 42}
        SCAN_IO._convert_legacy_param_names()
        self.assertEqual(SCAN_IO.imported_params["pattern_number_offset"], 42)
        self.assertEqual(SCAN_IO.imported_params["pattern_number_delta"], 1)
        self.assertNotIn("scan_start_index", SCAN_IO.imported_params)

    def test_convert_legacy_param_names__w_scan_start_index__duplicate(self):
        SCAN_IO.imported_params = {"scan_start_index": 42, "pattern_number_offset": 0}
        with self.assertRaises(UserConfigError):
            SCAN_IO._convert_legacy_param_names()

    def test_convert_legacy_params__w_scan_index_stepping(self):
        SCAN_IO.imported_params = {"scan_index_stepping": 2}
        SCAN_IO._convert_legacy_param_names()
        self.assertEqual(SCAN_IO.imported_params["frame_indices_per_scan_point"], 2)
        self.assertNotIn("scan_index_stepping", SCAN_IO.imported_params)

    def test_convert_legacy_params__w_scan_index_stepping__duplicate(self):
        SCAN_IO.imported_params = {
            "scan_index_stepping": 2,
            "frame_indices_per_scan_point": 0,
        }
        with self.assertRaises(UserConfigError):
            SCAN_IO._convert_legacy_param_names()

    def test_convert_legacy_params__w_scan_multiplicity(self):
        SCAN_IO.imported_params = {"scan_multiplicity": 7}
        SCAN_IO._convert_legacy_param_names()
        self.assertEqual(SCAN_IO.imported_params["scan_frames_per_scan_point"], 7)
        self.assertNotIn("scan_multiplicity", SCAN_IO.imported_params)

    def test_convert_legacy_params__w_scan_multiplicity__duplicate(self):
        SCAN_IO.imported_params = {
            "scan_multiplicity": 7,
            "scan_frames_per_scan_point": 2,
        }
        with self.assertRaises(UserConfigError):
            SCAN_IO._convert_legacy_param_names()

    def test_convert_legacy_params__w_scan_multi_image_handling(self):
        SCAN_IO.imported_params = {"scan_multi_image_handling": "Average"}
        SCAN_IO._convert_legacy_param_names()
        self.assertEqual(
            SCAN_IO.imported_params["scan_multi_frame_handling"], "Average"
        )
        self.assertNotIn("scan_multi_image_handling", SCAN_IO.imported_params)

    def test_convert_legacy_params__w_scan_multi_image_handling__duplicate(self):
        SCAN_IO.imported_params = {
            "scan_multi_image_handling": "Average",
            "scan_multi_frame_handling": "Sum",
        }
        with self.assertRaises(UserConfigError):
            SCAN_IO._convert_legacy_param_names()

    def test_check_file_list(self):
        _res = SCAN_IO.check_file_list(["scan_0001.h5", "scan_0002.h5"])
        self.assertEqual(_res, ["::no_error::"])


if __name__ == "__main__":
    unittest.main()

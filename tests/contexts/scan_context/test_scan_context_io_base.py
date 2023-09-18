# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
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


import os
import shutil
import tempfile
import unittest
from numbers import Integral, Real

import numpy as np

from pydidas.contexts.scan_context import Scan, ScanContext
from pydidas.contexts.scan_context.scan_context_io_base import ScanContextIoBase
from pydidas.core import UserConfigError
from pydidas.core.utils import get_random_string


SCAN = ScanContext()
SCAN_IO = ScanContextIoBase


class TestScanContextIoBase(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()

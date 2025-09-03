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


import shutil
import tempfile
import unittest
from pathlib import Path

import numpy as np
import yaml

from pydidas.contexts import ScanContext
from pydidas.contexts.scan import Scan
from pydidas.contexts.scan.scan_io_yaml import ScanIoYaml
from pydidas.core import UserConfigError


SCAN = ScanContext()
SCAN_IO_YAML = ScanIoYaml


class TestScanSetupIoYaml(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._test_path = Path(__file__).parents[2] / "_data"
        cls._fpath = cls._test_path / "load_test_scan_context.yml"
        cls._tmp_path = Path(tempfile.mkdtemp())

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._tmp_path)

    def test_import_from_file__correct(self):
        SCAN_IO_YAML.import_from_file(self._fpath)
        with open(self._fpath, "r") as stream:
            _data = yaml.safe_load(stream)
        for key in SCAN.params.keys():
            self.assertEqual(SCAN.get_param(key).value_for_export, _data[key])

    def test_import_from_file__w_legacy_keys(self):
        SCAN_IO_YAML.import_from_file(
            self._test_path / "load_test_scan_context_legacy.yml"
        )
        with open(self._fpath, "r") as stream:
            _data = yaml.safe_load(stream)
        for key in SCAN.params.keys():
            self.assertEqual(SCAN.get_param(key).value_for_export, _data[key])

    def test_import_from_file__given_Scan(self):
        _scan = Scan()
        SCAN_IO_YAML.import_from_file(self._fpath, scan=_scan)
        with open(self._fpath, "r") as stream:
            _data = yaml.safe_load(stream)
        for key in SCAN.params.keys():
            self.assertEqual(_scan.get_param(key).value_for_export, _data[key])

    def test_import_from_file__missing_keys(self):
        _fname = self._tmp_path / "yaml_missing_key.yml"
        with open(_fname, "w") as stream:
            stream.write("no_entry: True")
        with self.assertRaises(UserConfigError):
            SCAN_IO_YAML.import_from_file(_fname)

    def test_import_from_file__wrong_format(self):
        _fname = self._tmp_path / "yaml_wrong_format.yml"
        with open(_fname, "w") as stream:
            stream.write("no_entry =True")
        with self.assertRaises(UserConfigError):
            SCAN_IO_YAML.import_from_file(_fname)

    def test_import_from_file__legacy_format(self):
        _scan = Scan()
        SCAN_IO_YAML.import_from_file(
            self._test_path / "load_test_scan_context_legacy.yml", scan=_scan
        )
        _scan2 = Scan()
        SCAN_IO_YAML.import_from_file(
            self._test_path / "load_test_scan_context.yml", scan=_scan2
        )
        for key in SCAN.params:
            if key != "xray_energy":
                self.assertEqual(
                    _scan.get_param_value(key), _scan2.get_param_value(key)
                )

    def test_import_from_file__yaml_error(self):
        _fname = self._tmp_path / "yaml_error.yml"
        np.save(_fname, np.array([1, 2, 3]))  # Save a numpy array instead of YAML
        # remove the .npy suffix to simulate a YAML file
        shutil.move(_fname.parent / (_fname.name + ".npy"), _fname)
        with self.assertRaises(yaml.YAMLError):
            SCAN_IO_YAML.import_from_file(_fname)

    def test_export_to_file(self):
        _fname = self._tmp_path / "yaml_export.yml"
        SCAN_IO_YAML.export_to_file(_fname)
        with open(_fname, "r") as stream:
            _data = yaml.safe_load(stream)
        for key in SCAN.params:
            if key != "xray_energy":
                self.assertEqual(SCAN.get_param(key).value_for_export, _data[key])


if __name__ == "__main__":
    unittest.main()

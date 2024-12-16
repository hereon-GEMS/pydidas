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


import os
import shutil
import tempfile
import unittest

import yaml

from pydidas.contexts import ScanContext
from pydidas.contexts.scan import Scan
from pydidas.contexts.scan.scan_io_yaml import ScanIoYaml
from pydidas.core import UserConfigError


SCAN = ScanContext()
SCAN_IO_YAML = ScanIoYaml


class TestScanSetupIoYaml(unittest.TestCase):
    def setUp(self):
        _test_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self._path = os.path.join(_test_dir, "_data", "load_test_scan_context_yaml.yml")
        self._tmppath = tempfile.mkdtemp()

    def tearDown(self):
        del self._path
        shutil.rmtree(self._tmppath)

    def test_import_from_file__correct(self):
        SCAN_IO_YAML.import_from_file(self._path)
        with open(self._path, "r") as stream:
            _data = yaml.safe_load(stream)
        for key in SCAN.params.keys():
            self.assertEqual(SCAN.get_param(key).value_for_export, _data[key])

    def test_import_from_file__given_Scan(self):
        _scan = Scan()
        SCAN_IO_YAML.import_from_file(self._path, scan=_scan)
        with open(self._path, "r") as stream:
            _data = yaml.safe_load(stream)
        for key in SCAN.params.keys():
            self.assertEqual(_scan.get_param(key).value_for_export, _data[key])

    def test_import_from_file__missing_keys(self):
        with open(self._tmppath + "yaml.yml", "w") as stream:
            stream.write("no_entry: True")
        with self.assertRaises(UserConfigError):
            SCAN_IO_YAML.import_from_file(self._tmppath + "yaml.yml")

    def test_import_from_file__wrong_format(self):
        with open(self._tmppath + "yaml.yml", "w") as stream:
            stream.write("no_entry =True")
        with self.assertRaises(AssertionError):
            SCAN_IO_YAML.import_from_file(self._tmppath + "yaml.yml")

    def test_export_to_file(self):
        _fname = self._tmppath + "yaml.yml"
        SCAN_IO_YAML.export_to_file(_fname)
        with open(self._tmppath + "yaml.yml", "r") as stream:
            _data = yaml.safe_load(stream)
        for key in SCAN.params:
            if key != "xray_energy":
                self.assertEqual(SCAN.get_param(key).value_for_export, _data[key])


if __name__ == "__main__":
    unittest.main()

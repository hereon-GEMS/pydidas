# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
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
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import os
import unittest
import shutil
import tempfile

from pydidas.core import UserConfigError
from pydidas.experiment.setup_scan import SetupScan
from pydidas.experiment.setup_scan.setup_scan_io_base import SetupScanIoBase


SCAN = SetupScan()
SCAN_IO = SetupScanIoBase


class TestSetupScanIoBase(unittest.TestCase):
    def setUp(self):
        _test_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self._path = os.path.join(_test_dir, "_data", "load_test_setup_scan_")
        self._tmppath = tempfile.mkdtemp()
        SCAN_IO.imported_params = {}

    def tearDown(self):
        del self._path
        shutil.rmtree(self._tmppath)

    def test_check_for_existing_file__file_present(self):
        _fname = os.path.join(self._tmppath, "test.txt")
        with open(_fname, "w") as f:
            f.write("test entry")
        with self.assertRaises(FileExistsError):
            SCAN_IO.check_for_existing_file(_fname)

    def test_check_for_existing_file__file_present_and_overwrite(self):
        _fname = os.path.join(self._tmppath, "test.txt")
        with open(_fname, "w") as f:
            f.write("test entry")
        SCAN_IO.check_for_existing_file(_fname, overwrite=True)
        # assert does not raise FileExistsError

    def test_check_for_existing_file__file_new(self):
        _fname = os.path.join(self._tmppath, "test.txt")
        SCAN_IO.check_for_existing_file(_fname)
        # assert does not raise FileExistsError

    def test_verify_all_entries_present__correct(self):
        for param in SCAN.params:
            SCAN_IO.imported_params[param] = True
        SCAN_IO._verify_all_entries_present()

    def test_verify_all_entries_present__missing_keys(self):
        with self.assertRaises(UserConfigError):
            SCAN_IO._verify_all_entries_present()


if __name__ == "__main__":
    unittest.main()

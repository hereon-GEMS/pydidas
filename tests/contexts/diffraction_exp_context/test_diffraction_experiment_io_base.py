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


import os
import shutil
import tempfile
import unittest

from pydidas.contexts.diffraction_exp_context import (
    DiffractionExperiment,
    DiffractionExperimentContext,
)
from pydidas.contexts.diffraction_exp_context.diffraction_experiment_io_base import (
    DiffractionExperimentIoBase,
)
from pydidas.core import UserConfigError


EXP = DiffractionExperimentContext()
EXP_IO = DiffractionExperimentIoBase


class TestDiffractionExperimentIoBase(unittest.TestCase):
    def setUp(self):
        _test_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self._path = os.path.join(_test_dir, "_data", "load_test_exp_settings_")
        self._tmppath = tempfile.mkdtemp()
        EXP_IO.imported_params = {}

    def tearDown(self):
        del self._path
        shutil.rmtree(self._tmppath)

    def test_verify_all_entries_present__correct(self):
        for param in EXP.params:
            EXP_IO.imported_params[param] = True
        EXP_IO._verify_all_entries_present()

    def test_verify_all_entries_present__missing_keys(self):
        with self.assertRaises(UserConfigError):
            EXP_IO._verify_all_entries_present()

    def test_verify_all_entries_present__exclude_det_mask(self):
        for param in EXP.params:
            EXP_IO.imported_params[param] = True
        del EXP_IO.imported_params["detector_mask_file"]
        EXP_IO._verify_all_entries_present(exclude_det_mask=True)

    def test_write_to_exp_settings(self):
        _det_name = "Test Name"
        _energy = 123.45
        EXP_IO.imported_params = {"detector_name": _det_name, "xray_energy": _energy}
        EXP_IO._write_to_exp_settings()
        self.assertEqual(EXP.get_param_value("detector_name"), _det_name)
        self.assertEqual(EXP.get_param_value("xray_energy"), _energy)

    def test_write_to_exp_settings__with_diffraction_exp(self):
        EXP.restore_all_defaults(True)
        _exp = DiffractionExperiment()
        _det_name = "Test Name"
        _energy = 123.45
        EXP_IO.imported_params = {"detector_name": _det_name, "xray_energy": _energy}
        EXP_IO._write_to_exp_settings(diffraction_exp=_exp)
        self.assertEqual(_exp.get_param_value("detector_name"), _det_name)
        self.assertEqual(_exp.get_param_value("xray_energy"), _energy)
        self.assertNotEqual(EXP.get_param_value("detector_name"), _det_name)
        self.assertNotEqual(EXP.get_param_value("xray_energy"), _energy)


if __name__ == "__main__":
    unittest.main()

# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import logging
import os
import shutil
import tempfile
import unittest

import pyFAI
from pyFAI.geometry import Geometry

from pydidas.contexts import DiffractionExperimentContext
from pydidas.contexts.diffraction_exp_context import DiffractionExperiment
from pydidas.contexts.diffraction_exp_context.diffraction_exp_context_io_poni import (
    DiffractionExperimentContextIoPoni,
)


EXP = DiffractionExperimentContext()
EXP_IO_PONI = DiffractionExperimentContextIoPoni

_logger = logging.getLogger("pyFAI.geometry")
_logger.setLevel(logging.CRITICAL)


class TestExperimentSettingsIoPoni(unittest.TestCase):
    def setUp(self):
        _test_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self._path = os.path.join(
            _test_dir, "_data", "load_test_diffraction_exp_context_"
        )
        self._tmppath = tempfile.mkdtemp()

    def tearDown(self):
        del self._path
        shutil.rmtree(self._tmppath)

    def test_update_geometry_from_pyFAI__correct(self):
        geo = Geometry().load(self._path + "poni.poni")
        EXP_IO_PONI._update_geometry_from_pyFAI(geo)
        for param in [
            "detector_dist",
            "detector_poni1",
            "detector_poni2",
            "detector_rot1",
            "detector_rot2",
            "detector_rot3",
            "xray_wavelength",
            "xray_energy",
        ]:
            self.assertTrue(param in EXP_IO_PONI.imported_params)

    def test_update_geometry_from_pyFAI__wrong_type(self):
        with self.assertRaises(TypeError):
            EXP_IO_PONI._update_geometry_from_pyFAI(12)

    def test_update_detector_from_pyfai__correct(self):
        det = pyFAI.detector_factory("Eiger 9M")
        EXP_IO_PONI._update_detector_from_pyFAI(det)

    def test_update_detector_from_pyfai__wrong_type(self):
        det = 12
        with self.assertRaises(TypeError):
            EXP_IO_PONI._update_detector_from_pyFAI(det)

    def test_import_from_file(self):
        EXP_IO_PONI.import_from_file(self._path + "poni.poni")
        geo = Geometry().load(self._path + "poni.poni").getPyFAI()
        for key in [
            "detector_dist",
            "detector_poni1",
            "detector_poni2",
            "detector_rot1",
            "detector_rot2",
            "detector_rot3",
        ]:
            self.assertEqual(EXP.get_param_value(key), geo[key.split("_")[1]])

    def test_import_from_file__w_diffraction_exp(self):
        _exp = DiffractionExperiment()
        EXP_IO_PONI.import_from_file(self._path + "poni.poni", diffraction_exp=_exp)
        geo = Geometry().load(self._path + "poni.poni").getPyFAI()
        for key in [
            "detector_dist",
            "detector_poni1",
            "detector_poni2",
            "detector_rot1",
            "detector_rot2",
            "detector_rot3",
        ]:
            self.assertEqual(_exp.get_param_value(key), geo[key.split("_")[1]])

    def test_export_to_file(self):
        _fname = self._tmppath + "poni.poni"
        EXP_IO_PONI.export_to_file(_fname)
        with open(_fname, "r") as f:
            content = f.read()
        for key in [
            "Detector",
            "Detector_config",
            "Distance",
            "Poni1",
            "Poni2",
            "Rot1",
            "Rot2",
            "Rot3",
            "Wavelength",
        ]:
            self.assertTrue(content.find(key) > 0)


if __name__ == "__main__":
    unittest.main()

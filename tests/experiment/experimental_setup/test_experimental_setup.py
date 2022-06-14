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


import unittest
import copy
import logging

import pyFAI

from pydidas.experiment.setup_experiment.setup_experiment import (
    _ExpSetup,
    SetupExperiment,
)


logger = logging.getLogger("pyFAI.detectors._common")
logger.setLevel(logging.CRITICAL)


class TestSetupExperiment(unittest.TestCase):
    def setUp(self):
        ...

    def tearDown(self):
        ...

    def test_creation(self):
        obj = SetupExperiment()
        self.assertIsInstance(obj, _ExpSetup)

    def test_set_param_generic(self):
        _name = "Test"
        obj = SetupExperiment()
        obj.set_param_value("detector_name", _name)
        self.assertEqual(obj.get_param_value("detector_name"), _name)

    def test_set_param_energy(self):
        _new_E = 15.7
        obj = SetupExperiment()
        obj.set_param_value("xray_energy", _new_E)
        self.assertEqual(obj.get_param_value("xray_energy"), _new_E)
        self.assertAlmostEqual(
            obj.get_param_value("xray_wavelength"), 0.7897080652951567, delta=0.00005
        )

    def test_set_param_wavelength(self):
        _new_lambda = 0.98765
        obj = SetupExperiment()
        obj.set_param_value("xray_wavelength", _new_lambda)
        self.assertEqual(obj.get_param_value("xray_wavelength"), _new_lambda)
        self.assertAlmostEqual(
            obj.get_param_value("xray_energy"), 12.55345175429956, delta=0.0005
        )

    def test_get_detector__from_param_name(self):
        _shape = (1000, 1000)
        obj = SetupExperiment()
        obj.set_param_value("detector_name", "Eiger 9M")
        obj.set_param_value("detector_npixy", _shape[0])
        obj.set_param_value("detector_npixx", _shape[1])
        _det = obj.get_detector()
        self.assertIsInstance(_det, pyFAI.detectors.Detector)
        self.assertEqual(_det.max_shape, _shape)

    def test_get_detector__new_name(self):
        _shape = (1000, 1000)
        _pixelsize = 100
        obj = SetupExperiment()
        obj.set_param_value("detector_name", "No Eiger")
        obj.set_param_value("detector_npixy", _shape[0])
        obj.set_param_value("detector_npixx", _shape[1])
        obj.set_param_value("detector_pxsizey", _pixelsize)
        obj.set_param_value("detector_pxsizex", _pixelsize)
        _det = obj.get_detector()
        self.assertIsInstance(_det, pyFAI.detectors.Detector)
        self.assertEqual(_det.max_shape, _shape)
        self.assertEqual(_det.pixel1, 1e-6 * _pixelsize)
        self.assertEqual(_det.pixel2, 1e-6 * _pixelsize)

    def test_copy(self):
        obj = SetupExperiment()
        obj2 = copy.copy(obj)
        self.assertEqual(obj, obj2)

    def test_set_detector_params_from_name__wrong_name(self):
        obj = SetupExperiment()
        with self.assertRaises(NameError):
            obj.set_detector_params_from_name("no such detector")

    def test_set_detector_params_from_name(self):
        _det = {"name": "Pilatus 300k", "pixsize": 172, "npixx": 487, "npixy": 619}
        obj = SetupExperiment()
        obj.set_detector_params_from_name(_det["name"])
        self.assertEqual(obj.get_param_value("detector_name"), _det["name"])
        self.assertEqual(obj.get_param_value("detector_pxsizex"), _det["pixsize"])
        self.assertEqual(obj.get_param_value("detector_pxsizey"), _det["pixsize"])
        self.assertEqual(obj.get_param_value("detector_npixy"), _det["npixy"])
        self.assertEqual(obj.get_param_value("detector_npixx"), _det["npixx"])


if __name__ == "__main__":
    unittest.main()

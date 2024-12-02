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


import logging
import unittest
from numbers import Real

import numpy as np
import pyFAI
from pydidas.contexts.diff_exp import (
    DiffractionExperiment,
    DiffractionExperimentContext,
)
from pydidas.core import UserConfigError


logger = logging.getLogger("pyFAI.detectors._common")
logger.setLevel(logging.CRITICAL)

_pyfai_geo_params = {
    "rot1": 12e-5,
    "rot2": 24e-4,
    "rot3": 0.421,
    "dist": 0.654,
    "poni1": 0.1,
    "poni2": 0.32,
}


def prepare_exp_with_Eiger():
    obj = DiffractionExperiment()
    obj.set_detector_params_from_name("Eiger 9M")
    return obj


class TestDiffractionExperiment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._xpos = 1623.546
        cls._ypos = 459.765
        cls._det_dist = 0.12
        cls._beamcenter = (cls._xpos, cls._ypos, cls._det_dist)
        cls._xpos_abs = cls._xpos * 75e-6
        cls._ypos_abs = cls._ypos * 75e-6

    def setUp(self): ...

    def tearDown(self): ...

    def assert_beamcenter_okay(self, obj, accuracy=8):
        _rot1 = obj.get_param_value("detector_rot1")
        _rot2 = obj.get_param_value("detector_rot2")
        _poni1 = obj.get_param_value("detector_poni1")
        _poni2 = obj.get_param_value("detector_poni2")
        _z = obj.get_param_value("detector_dist")
        _beam_center_x = (_poni2 - _z * np.tan(_rot1)) / 75e-6
        _beam_center_y = (_poni1 + _z * np.tan(_rot2) / np.cos(_rot1)) / 75e-6
        self.assertAlmostEqual(_beam_center_y, self._ypos, accuracy)
        self.assertAlmostEqual(_beam_center_x, self._xpos, accuracy)

    def test_set_param_energy(self):
        _new_E = 15.7
        obj = DiffractionExperimentContext()
        obj.set_param_value("xray_energy", _new_E)
        self.assertEqual(obj.get_param_value("xray_energy"), _new_E)
        self.assertAlmostEqual(
            obj.get_param_value("xray_wavelength"), 0.78970806, delta=0.00005
        )

    def test_set_param_wavelength(self):
        _new_lambda = 0.98765
        obj = DiffractionExperimentContext()
        obj.set_param_value("xray_wavelength", _new_lambda)
        self.assertEqual(obj.get_param_value("xray_wavelength"), _new_lambda)
        self.assertAlmostEqual(
            obj.get_param_value("xray_energy"), 12.5534517, delta=0.0005
        )

    def test_get_detector__from_param_name(self):
        _shape = (1000, 1000)
        obj = DiffractionExperimentContext()
        obj.set_param_value("detector_name", "Eiger 9M")
        obj.set_param_value("detector_npixy", _shape[0])
        obj.set_param_value("detector_npixx", _shape[1])
        _det = obj.get_detector()
        self.assertIsInstance(_det, pyFAI.detectors.Detector)
        self.assertEqual(_det.max_shape, _shape)

    def test_get_detector__new_name(self):
        _shape = (1000, 1000)
        _pixelsize = 100
        obj = DiffractionExperimentContext()
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

    def test_detector_is_valid__no_detector(self):
        obj = DiffractionExperiment()
        self.assertFalse(obj.detector_is_valid)

    def test_detector_is_valid__pyfai_detector(self):
        obj = DiffractionExperiment()
        obj.set_detector_params_from_name("Eiger 9M")
        self.assertTrue(obj.detector_is_valid)

    def test_detector_is_valid__manual_detector(self):
        obj = DiffractionExperiment()
        _shape = (1000, 1000)
        _pixelsize = 100
        obj.set_param_value("detector_name", "No Eiger")
        obj.set_param_value("detector_npixy", _shape[0])
        obj.set_param_value("detector_npixx", _shape[1])
        obj.set_param_value("detector_pxsizey", _pixelsize)
        obj.set_param_value("detector_pxsizex", _pixelsize)
        self.assertTrue(obj.detector_is_valid)

    def test_detector_is_valid__incomplete_manual_detector(self):
        obj = DiffractionExperiment()
        _shape = (1000, 1000)
        obj.set_param_value("detector_name", "No Eiger")
        obj.set_param_value("detector_npixy", _shape[0])
        obj.set_param_value("detector_npixx", _shape[1])
        obj.set_param_value("detector_pxsizey", 0)
        obj.set_param_value("detector_pxsizex", 100)
        self.assertFalse(obj.detector_is_valid)

    def test_as_pyfai_geometry(self):
        obj = prepare_exp_with_Eiger()
        for _key, _val in _pyfai_geo_params.items():
            obj.set_param_value(f"detector_{_key}", _val)
        _geo = obj.as_pyfai_geometry()
        self.assertIsInstance(_geo, pyFAI.geometry.Geometry)
        for _key, _val in _pyfai_geo_params.items():
            self.assertEqual(getattr(_geo, _key), _val)

    def test_set_detector_params_from_name__wrong_name(self):
        obj = DiffractionExperimentContext()
        with self.assertRaises(UserConfigError):
            obj.set_detector_params_from_name("no such detector")

    def test_update_from_diffraction_exp(self):
        obj = DiffractionExperimentContext()
        obj.set_param_value("detector_name", "Eiger 9M")
        _exp = DiffractionExperiment()
        _exp.update_from_diffraction_exp(obj)
        for _key, _val in obj.get_param_values_as_dict().items():
            if isinstance(_val, Real):
                self.assertAlmostEqual(_val, _exp.get_param_value(_key), delta=0.000001)
            else:
                self.assertEqual(_val, _exp.get_param_value(_key))

    def test_update_from_pyfai_geometry__no_detector(self):
        obj = DiffractionExperimentContext()
        obj.set_param_value("detector_name", "Eiger 9M")
        _geo = pyFAI.geometry.Geometry()
        for _key, _val in _pyfai_geo_params.items():
            setattr(_geo, _key, _val)
        obj.update_from_pyfai_geometry(_geo)
        for _key, _val in _pyfai_geo_params.items():
            self.assertEqual(obj.get_param_value(f"detector_{_key}"), _val)
        self.assertEqual(obj.get_param_value("detector_name"), "Eiger 9M")

    def test_update_from_pyfai_geometry__custom_detector(self):
        obj = DiffractionExperimentContext()
        _det = pyFAI.detectors.Detector(
            pixel1=12e-6, pixel2=24e-6, max_shape=(1234, 567)
        )
        _det.aliases = ["Dummy"]
        _geo = pyFAI.geometry.Geometry(**_pyfai_geo_params, detector=_det)
        obj.update_from_pyfai_geometry(_geo)
        for _key, _val in _pyfai_geo_params.items():
            self.assertEqual(obj.get_param_value(f"detector_{_key}"), _val)
        for _key, _val in [
            ["pxsizex", _det.pixel2 * 1e6],
            ["pxsizey", _det.pixel1 * 1e6],
            ["npixx", _det.max_shape[1]],
            ["npixy", _det.max_shape[0]],
            ["name", "Dummy"],
        ]:
            self.assertEqual(obj.get_param_value(f"detector_{_key}"), _val)

    def test_update_from_pyfai_geometry__generic_detector(self):
        obj = DiffractionExperimentContext()
        _geo = pyFAI.geometry.Geometry(**_pyfai_geo_params, detector="Eiger 9M")
        _det = pyFAI.detector_factory("Eiger 9M")
        obj.update_from_pyfai_geometry(_geo)
        for _key, _val in _pyfai_geo_params.items():
            self.assertEqual(obj.get_param_value(f"detector_{_key}"), _val)
        for _key, _val in [
            ["pxsizex", _det.pixel2 * 1e6],
            ["pxsizey", _det.pixel1 * 1e6],
            ["npixx", _det.max_shape[1]],
            ["npixy", _det.max_shape[0]],
            ["name", "Eiger 9M"],
        ]:
            self.assertEqual(obj.get_param_value(f"detector_{_key}"), _val)

    def test_set_detector_params_from_name(self):
        _det = {"name": "Pilatus 300k", "pixsize": 172, "npixx": 487, "npixy": 619}
        obj = DiffractionExperimentContext()
        obj.set_detector_params_from_name(_det["name"])
        self.assertEqual(obj.get_param_value("detector_name"), _det["name"])
        self.assertEqual(obj.get_param_value("detector_pxsizex"), _det["pixsize"])
        self.assertEqual(obj.get_param_value("detector_pxsizey"), _det["pixsize"])
        self.assertEqual(obj.get_param_value("detector_npixy"), _det["npixy"])
        self.assertEqual(obj.get_param_value("detector_npixx"), _det["npixx"])

    def test_set_beamcenter_from_fit2d_params__no_rot(self):
        obj = prepare_exp_with_Eiger()
        obj.set_beamcenter_from_fit2d_params(*self._beamcenter)
        self.assert_beamcenter_okay(obj)

    def test_set_beamcenter_from_fit2d_params__full_rot_degree(self):
        obj = prepare_exp_with_Eiger()
        obj.set_beamcenter_from_fit2d_params(
            *self._beamcenter, tilt=5, tilt_plane=270, rot_unit="degree"
        )
        self.assert_beamcenter_okay(obj)

    def test_set_beamcenter_from_fit2d_params_full_rot_rad(self):
        obj = prepare_exp_with_Eiger()
        obj.set_beamcenter_from_fit2d_params(
            *self._beamcenter, tilt=0.5, tilt_plane=1, rot_unit="rad"
        )
        self.assert_beamcenter_okay(obj)

    def test_as_fit2d_geometry_values(self):
        obj = prepare_exp_with_Eiger()
        _f2d = obj.as_fit2d_geometry_values()
        self.assertIsInstance(_f2d, dict)

    def test_as_fit2d_geometry_values__invalid_exp(self):
        obj = prepare_exp_with_Eiger()
        obj.set_param_value("detector_pxsizex", 0)
        with self.assertRaises(UserConfigError):
            obj.as_fit2d_geometry_values()

    def test_beamcenter__not_set(self):
        obj = prepare_exp_with_Eiger()
        _cx, _cy = obj.beamcenter
        self.assertEqual(_cx, 0)
        self.assertEqual(_cy, 0)

    def test_beamcenter__set(self):
        obj = prepare_exp_with_Eiger()
        _cx = 1248
        _cy = 1369.75
        obj.set_param_value(
            "detector_poni1", _cy * obj.get_param_value("detector_pxsizex") * 1e-6
        )
        obj.set_param_value(
            "detector_poni2", _cx * obj.get_param_value("detector_pxsizey") * 1e-6
        )
        _cx_calc, _cy_calc = obj.beamcenter
        self.assertAlmostEqual(_cx, _cx_calc, 8)
        self.assertAlmostEqual(_cy, _cy_calc, 8)

    def test_hash(self):
        obj = prepare_exp_with_Eiger()
        _copy = obj.copy()
        self.assertEqual(hash(obj), hash(_copy))


if __name__ == "__main__":
    unittest.main()

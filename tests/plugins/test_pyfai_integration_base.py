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
import os
import shutil
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pyFAI

from pydidas.contexts import DiffractionExperimentContext
from pydidas.core import UserConfigError, get_generic_parameter
from pydidas.plugins import BasePlugin, pyFAIintegrationBase


EXP = DiffractionExperimentContext()

logger = logging.getLogger("pydidas_logger")
logger.setLevel(logging.ERROR)


class TestPyFaiIntegrationBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._det_dist = 0.1
        EXP.set_param_value("detector_dist", cls._det_dist)
        cls._det_pxsize = 1000
        EXP.set_param_value("detector_pxsizex", cls._det_pxsize)
        EXP.set_param_value("detector_pxsizey", cls._det_pxsize)
        cls._lambda = 1
        EXP.set_param_value("xray_wavelength", cls._lambda)
        cls._test_vals_low = {
            "2theta": 12,
            "q": 4e-9 * np.pi / (cls._lambda * 1e-10) * np.sin(12 / 2 * np.pi / 180),
            "r": 1e3 * cls._det_dist * np.tan(12 * np.pi / 180),
        }
        cls._test_vals_high = {
            "2theta": 25,
            "q": 4e-9 * np.pi / (cls._lambda * 1e-10) * np.sin(25 / 2 * np.pi / 180),
            "r": 1e3 * cls._det_dist * np.tan(25 * np.pi / 180),
        }

    def setUp(self):
        self._temppath = tempfile.mkdtemp()
        self._shape = (50, 50)

    def tearDown(self):
        shutil.rmtree(self._temppath)
        EXP.set_param_value("detector_mask_file", Path())

    def initialize_base_plugin(self, **kwargs):
        for key, value in [
            ["rad_npoint", 900],
            ["rad_unit", "2theta / deg"],
            ["rad_use_range", "Full detector"],
            ["rad_range_lower", -1],
            ["rad_range_upper", 1],
            ["azi_npoint", 1],
            ["azi_unit", "chi / deg"],
            ["azi_use_range", "Full detector"],
            ["azi_range_lower", -1],
            ["azi_range_upper", 1],
            ["int_method", "CSR OpenCL"],
        ]:
            kwargs[key] = kwargs.get(key, value)
        plugin = pyFAIintegrationBase(**kwargs)
        return plugin

    def create_mask(self, shape=None):
        rng = np.random.default_rng(12345)
        _mask = rng.integers(
            low=0, high=2, size=shape if shape is not None else self._shape
        )
        _maskfilename = os.path.join(self._temppath, "mask.npy")
        np.save(_maskfilename, _mask)
        return _maskfilename, _mask

    def test_init__plain(self):
        plugin = pyFAIintegrationBase()
        self.assertIsInstance(plugin, BasePlugin)

    def test_init__with_kwargs(self):
        _npoints = 7215421
        plugin = pyFAIintegrationBase(rad_npoint=_npoints)
        self.assertEqual(plugin.get_param_value("rad_npoint"), _npoints)

    def test_init__with_params(self):
        _npoints = 7215421
        _param = get_generic_parameter("rad_npoint")
        _param.value = _npoints
        plugin = pyFAIintegrationBase(_param)
        self.assertEqual(plugin.get_param_value("rad_npoint"), _npoints)

    def test_is_basic_plugin__baseclass(self):
        for _plugin in [pyFAIintegrationBase, pyFAIintegrationBase()]:
            self.assertTrue(_plugin.is_basic_plugin())

    def test_is_basic_plugin__subclass(self):
        class TestPlugin(pyFAIintegrationBase):
            pass

        for _plugin in [TestPlugin, TestPlugin()]:
            self.assertFalse(_plugin.is_basic_plugin())

    def test_get_pyFAI_unit_from_param__plain(self):
        plugin = pyFAIintegrationBase(rad_unit="Q / nm^-1")
        self.assertEqual(plugin.get_pyFAI_unit_from_param("rad_unit"), "q_nm^-1")

    def test_modulate_and_store_azi_range__rad_ranges_flipped(self):
        plugin = pyFAIintegrationBase(
            azi_use_range="Specify azimuthal range",
            azi_unit="chi / rad",
            azi_range_lower=0.2,
            azi_range_upper=0.1,
        )
        with self.assertRaises(UserConfigError):
            plugin.modulate_and_store_azi_range()

    def test_modulate_and_store_azi_range__rad_mod_2pi(self):
        plugin = pyFAIintegrationBase(
            azi_use_range="Specify azimuthal range",
            azi_unit="chi / rad",
            azi_range_lower=0.1 - 2 * np.pi,
            azi_range_upper=0.2 - 2 * np.pi,
        )
        plugin.modulate_and_store_azi_range()
        _low, _high = plugin.get_azimuthal_range_native()
        self.assertAlmostEqual(_low, 0.1)
        self.assertAlmostEqual(_high, 0.2)

    def test_modulate_and_store_azi_range__rad__low_lt_zero(self):
        plugin = pyFAIintegrationBase(
            azi_use_range="Specify azimuthal range",
            azi_unit="chi / rad",
            azi_range_lower=-0.4,
            azi_range_upper=0.2,
        )
        plugin.modulate_and_store_azi_range()
        _low, _high = plugin.get_azimuthal_range_native()
        self.assertAlmostEqual(_low, -0.4)
        self.assertAlmostEqual(_high, 0.2)

    def test_modulate_and_store_azi_range__rad_mod_pi(self):
        plugin = pyFAIintegrationBase(
            azi_use_range="Specify azimuthal range",
            azi_unit="chi / rad",
            azi_range_lower=0.1 - np.pi,
            azi_range_upper=0.2 - np.pi,
        )
        plugin.modulate_and_store_azi_range()
        _low, _high = plugin.get_azimuthal_range_native()
        self.assertAlmostEqual(_low, 0.1 - np.pi)
        self.assertAlmostEqual(_high, 0.2 - np.pi)

    def test_modulate_and_store_azi_range__deg_ranges_flipped(self):
        plugin = pyFAIintegrationBase(
            azi_use_range="Specify azimuthal range",
            azi_unit="chi / deg",
            azi_range_lower=0.2,
            azi_range_upper=0.1,
        )
        with self.assertRaises(UserConfigError):
            plugin.modulate_and_store_azi_range()

    def test_modulate_and_store_azi_range__deg_mod_2pi(self):
        plugin = pyFAIintegrationBase(
            azi_use_range="Specify azimuthal range",
            azi_unit="chi / deg",
            azi_range_lower=0.1 - 360,
            azi_range_upper=0.2 - 360,
        )
        plugin.modulate_and_store_azi_range()
        _low, _high = plugin.get_azimuthal_range_native()
        self.assertAlmostEqual(_low, 0.1)
        self.assertAlmostEqual(_high, 0.2)

    def test_modulate_and_store_azi_range__deg_mod_pi(self):
        plugin = pyFAIintegrationBase(
            azi_use_range="Specify azimuthal range",
            azi_unit="chi / deg",
            azi_range_lower=0.1 - 180,
            azi_range_upper=0.2 - 180,
        )
        plugin.modulate_and_store_azi_range()
        _low, _high = plugin.get_azimuthal_range_native()
        self.assertAlmostEqual(_low, 0.1 - 180)
        self.assertAlmostEqual(_high, 0.2 - 180)

    def test_get_azimuthal_range_native__no_range(self):
        plugin = pyFAIintegrationBase(azi_use_range="Full detector")
        _range = plugin.get_azimuthal_range_native()
        self.assertEqual(_range, (-180, 180))

    def test_get_azimuthal_range_native__no_azi_use_range_param(self):
        plugin = pyFAIintegrationBase(azi_use_range="Full detector")
        del plugin.params["azi_use_range"]
        _range = plugin.get_azimuthal_range_native()
        self.assertEqual(_range, (-180, 180))

    def test_get_azimuthal_range_native__equal_boundaries(self):
        plugin = pyFAIintegrationBase(
            azi_use_range="Specify azimuthal range",
            azi_range_lower=12,
            azi_range_upper=12,
        )
        _range = plugin.get_azimuthal_range_native()
        self.assertEqual(_range, (-180, 180))

    def test_get_azimuthal_range_native__correct(self):
        _range = (12, 37)
        plugin = pyFAIintegrationBase(
            azi_use_range="Specify azimuthal range",
            azi_range_lower=_range[0],
            azi_range_upper=_range[1],
        )
        _newrange = plugin.get_azimuthal_range_native()
        self.assertEqual(_range, _newrange)

    def test_get_azimuthal_range_in_deg__empty(self):
        plugin = pyFAIintegrationBase(azi_use_range="Full detector")
        _newrange = plugin.get_azimuthal_range_in_deg()
        self.assertEqual(_newrange, (-180, 180))

    def test_get_azimuthal_range_in_deg__degree_input(self):
        _range = (12, 37)
        plugin = pyFAIintegrationBase(
            azi_use_range="Specify azimuthal range",
            azi_range_lower=_range[0],
            azi_range_upper=_range[1],
            azi_unit="chi / deg",
        )
        plugin.pre_execute()
        _newrange = plugin.get_azimuthal_range_in_deg()
        self.assertEqual(_range, _newrange)

    def test_get_azimuthal_range_in_deg__rad_input(self):
        _range = (1, 1.5)
        plugin = pyFAIintegrationBase(
            azi_use_range="Specify azimuthal range",
            azi_range_lower=_range[0],
            azi_range_upper=_range[1],
            azi_unit="chi / rad",
        )
        plugin.pre_execute()
        _newrange = plugin.get_azimuthal_range_in_deg()
        self.assertAlmostEqual(_newrange[0], _range[0] * 180 / np.pi, 5)
        self.assertAlmostEqual(_newrange[1], _range[1] * 180 / np.pi, 5)

    def test_get_azimuthal_range_in_rad__empty(self):
        plugin = pyFAIintegrationBase(azi_use_range="Full detector")
        _newrange = plugin.get_azimuthal_range_in_rad()
        self.assertTrue(np.allclose(_newrange, (-np.pi, np.pi)))

    def test_get_azimuthal_range_in_rad__degree_input(self):
        _range = (12, 37)
        plugin = pyFAIintegrationBase(
            azi_use_range="Specify azimuthal range",
            azi_range_lower=_range[0],
            azi_range_upper=_range[1],
            azi_unit="chi / deg",
        )
        plugin.pre_execute()
        _newrange = plugin.get_azimuthal_range_in_rad()
        self.assertAlmostEqual(_newrange[0] * 180 / np.pi, _range[0], 4)
        self.assertAlmostEqual(_newrange[1] * 180 / np.pi, _range[1], 4)

    def test_get_azimuthal_range_in_rad__rad_input(self):
        _range = (1, 2.5)
        plugin = pyFAIintegrationBase(
            azi_use_range="Specify azimuthal range",
            azi_range_lower=_range[0],
            azi_range_upper=_range[1],
            azi_unit="chi / rad",
        )
        plugin.pre_execute()
        _newrange = plugin.get_azimuthal_range_in_rad()
        self.assertEqual(_range, _newrange)

    def test_get_radial_range__no_range(self):
        plugin = pyFAIintegrationBase(rad_use_range="Full detector")
        _range = plugin.get_radial_range()
        self.assertIsNone(_range)

    def test_get_radial_range__no_rad_use_range_param(self):
        plugin = pyFAIintegrationBase(rad_use_range="Full detector")
        del plugin.params["rad_use_range"]
        _range = plugin.get_radial_range()
        self.assertIsNone(_range)

    def test_get_radial_range__lower_range_too_small(self):
        plugin = pyFAIintegrationBase(
            rad_use_range="Specify radial range", rad_range_lower=-1, rad_range_upper=1
        )
        _range = plugin.get_radial_range()
        self.assertIsNone(_range)

    def test_get_radial_range__upper_range_too_small(self):
        plugin = pyFAIintegrationBase(
            rad_use_range="Specify radial range", rad_range_lower=0, rad_range_upper=0
        )
        _range = plugin.get_radial_range()
        self.assertIsNone(_range)

    def test_get_radial_range__equal_boundaries(self):
        plugin = pyFAIintegrationBase(
            rad_use_range="Specify radial range", rad_range_lower=12, rad_range_upper=12
        )
        _range = plugin.get_radial_range()
        self.assertIsNone(_range)

    def test_get_radial_range__upper_bound_lower(self):
        plugin = pyFAIintegrationBase(
            rad_use_range="Specify radial range", rad_range_lower=15, rad_range_upper=12
        )
        _range = plugin.get_radial_range()
        self.assertIsNone(_range)

    def test_get_radial_range__correct(self):
        _range = (12, 37)
        plugin = pyFAIintegrationBase(
            rad_use_range="Specify radial range",
            rad_range_lower=_range[0],
            rad_range_upper=_range[1],
        )
        _newrange = plugin.get_radial_range()
        self.assertEqual(_range, _newrange)

    def test_get_radial_range_as_2theta(self):
        _input_low, _input_high = (12, 37)
        plugin = pyFAIintegrationBase(
            rad_use_range="Specify radial range",
            rad_unit="2theta / deg",
            rad_range_lower=_input_low,
            rad_range_upper=_input_high,
        )
        _low, _high = plugin.get_radial_range_as_2theta()
        self.assertAlmostEqual(_input_low, _low)
        self.assertAlmostEqual(_input_high, _high)

    def test_get_radial_range_as_2theta__input_r(self):
        _input_low, _input_high = (12, 37)
        plugin = pyFAIintegrationBase(
            rad_use_range="Specify radial range",
            rad_unit="r / mm",
            rad_range_lower=_input_low,
            rad_range_upper=_input_high,
        )
        _low, _high = plugin.get_radial_range_as_2theta()
        _low_target = 180 / np.pi * np.arctan(_input_low * 1e-3 / self._det_dist)
        _high_target = 180 / np.pi * np.arctan(_input_high * 1e-3 / self._det_dist)
        self.assertAlmostEqual(_low_target, _low)
        self.assertAlmostEqual(_high_target, _high)

    def test_get_radial_range_as_2theta__input_q(self):
        _input_low, _input_high = (12, 37)
        plugin = pyFAIintegrationBase(
            rad_use_range="Specify radial range",
            rad_unit="Q / nm^-1",
            rad_range_lower=_input_low,
            rad_range_upper=_input_high,
        )
        _low, _high = plugin.get_radial_range_as_2theta()
        _low_target = (
            180 / np.pi * 2 * np.arcsin(0.1 * _input_low * self._lambda / 4 / np.pi)
        )
        _high_target = (
            180 / np.pi * 2 * np.arcsin(0.1 * _input_high * self._lambda / 4 / np.pi)
        )
        self.assertAlmostEqual(_low_target, _low)
        self.assertAlmostEqual(_high_target, _high)

    def test_get_radial_range_as_2theta__rad(self):
        _input_low, _input_high = (12, 37)
        plugin = pyFAIintegrationBase(
            rad_use_range="Specify radial range",
            rad_unit="2theta / deg",
            rad_range_lower=_input_low,
            rad_range_upper=_input_high,
        )
        _low, _high = plugin.get_radial_range_as_2theta(unit="rad")
        self.assertAlmostEqual(_input_low * np.pi / 180, _low)
        self.assertAlmostEqual(_input_high * np.pi / 180, _high)

    def test_get_radial_range_as_r(self):
        _input_low, _input_high = (12, 37)
        plugin = pyFAIintegrationBase(
            rad_use_range="Specify radial range",
            rad_unit="2theta / deg",
            rad_range_lower=_input_low,
            rad_range_upper=_input_high,
        )
        _low, _high = plugin.get_radial_range_as_r()
        _target_low = self._det_dist * np.tan(_input_low * np.pi / 180) * 1e3
        _target_high = self._det_dist * np.tan(_input_high * np.pi / 180) * 1e3
        self.assertAlmostEqual(_low, _target_low)
        self.assertAlmostEqual(_high, _target_high)

    def test_get_radial_range_as_q(self):
        _input_low, _input_high = (12, 37)
        plugin = pyFAIintegrationBase(
            rad_use_range="Specify radial range",
            rad_unit="2theta / deg",
            rad_range_lower=_input_low,
            rad_range_upper=_input_high,
        )
        _low, _high = plugin.get_radial_range_as_q()
        # factor 10 is 1e-9 from q in nm times 1e10 from lambda in A
        _target_low = (
            4 * np.pi / self._lambda * np.sin(_input_low * np.pi / 180 / 2) * 10
        )
        _target_high = (
            4 * np.pi / self._lambda * np.sin(_input_high * np.pi / 180 / 2) * 10
        )
        self.assertAlmostEqual(_low, _target_low)
        self.assertAlmostEqual(_high, _target_high)

    def test_convert_radial_range_values__same_unit(self):
        plugin = pyFAIintegrationBase(
            rad_use_range="Specify radial range",
            rad_unit="2theta / deg",
            rad_range_lower=self._test_vals_low["2theta"],
            rad_range_upper=self._test_vals_high["2theta"],
        )
        plugin.convert_radial_range_values("2theta / deg", "2theta / deg")
        self.assertEqual(
            plugin.get_param_value("rad_range_lower"), self._test_vals_low["2theta"]
        )
        self.assertEqual(
            plugin.get_param_value("rad_range_upper"), self._test_vals_high["2theta"]
        )

    def test_convert_radial_range_values__2theta_to_q(self):
        plugin = pyFAIintegrationBase(
            rad_use_range="Specify radial range",
            rad_unit="2theta / deg",
            rad_range_lower=self._test_vals_low["2theta"],
            rad_range_upper=self._test_vals_high["2theta"],
        )
        plugin.convert_radial_range_values("2theta / deg", "Q / nm^-1")
        self.assertAlmostEqual(
            plugin.get_param_value("rad_range_lower"), self._test_vals_low["q"]
        )
        self.assertAlmostEqual(
            plugin.get_param_value("rad_range_upper"), self._test_vals_high["q"]
        )

    def test_convert_radial_range_values__2theta_to_r(self):
        plugin = pyFAIintegrationBase(
            rad_use_range="Specify radial range",
            rad_unit="2theta / deg",
            rad_range_lower=self._test_vals_low["2theta"],
            rad_range_upper=self._test_vals_high["2theta"],
        )
        plugin.convert_radial_range_values("2theta / deg", "r / mm")
        self.assertAlmostEqual(
            plugin.get_param_value("rad_range_lower"), self._test_vals_low["r"]
        )
        self.assertAlmostEqual(
            plugin.get_param_value("rad_range_upper"), self._test_vals_high["r"]
        )

    def test_convert_radial_range_values__q_to_2theta(self):
        plugin = pyFAIintegrationBase(
            rad_use_range="Specify radial range",
            rad_unit="Q / nm^-1",
            rad_range_lower=self._test_vals_low["q"],
            rad_range_upper=self._test_vals_high["q"],
        )
        plugin.convert_radial_range_values("Q / nm^-1", "2theta / deg")
        self.assertAlmostEqual(
            plugin.get_param_value("rad_range_lower"), self._test_vals_low["2theta"]
        )
        self.assertAlmostEqual(
            plugin.get_param_value("rad_range_upper"), self._test_vals_high["2theta"]
        )

    def test_convert_radial_range_values__q_to_r(self):
        plugin = pyFAIintegrationBase(
            rad_use_range="Specify radial range",
            rad_unit="Q / nm^-1",
            rad_range_lower=self._test_vals_low["q"],
            rad_range_upper=self._test_vals_high["q"],
        )
        plugin.convert_radial_range_values("Q / nm^-1", "r / mm")
        self.assertAlmostEqual(
            plugin.get_param_value("rad_range_lower"), self._test_vals_low["r"]
        )
        self.assertAlmostEqual(
            plugin.get_param_value("rad_range_upper"), self._test_vals_high["r"]
        )

    def test_convert_radial_range_values__r_to_2theta(self):
        plugin = pyFAIintegrationBase(
            rad_use_range="Specify radial range",
            rad_unit="r / mm",
            rad_range_lower=self._test_vals_low["r"],
            rad_range_upper=self._test_vals_high["r"],
        )
        plugin.convert_radial_range_values("r / mm", "2theta / deg")
        self.assertAlmostEqual(
            plugin.get_param_value("rad_range_lower"), self._test_vals_low["2theta"]
        )
        self.assertAlmostEqual(
            plugin.get_param_value("rad_range_upper"), self._test_vals_high["2theta"]
        )

    def test_convert_radial_range_values__r_to_q(self):
        plugin = pyFAIintegrationBase(
            rad_use_range="Specify radial range",
            rad_unit="r / mm",
            rad_range_lower=self._test_vals_low["r"],
            rad_range_upper=self._test_vals_high["r"],
        )
        plugin.convert_radial_range_values("r / mm", "Q / nm^-1")
        self.assertAlmostEqual(
            plugin.get_param_value("rad_range_lower"), self._test_vals_low["q"]
        )
        self.assertAlmostEqual(
            plugin.get_param_value("rad_range_upper"), self._test_vals_high["q"]
        )

    def test_calculate_result_shape(self):
        _range = (1234, 789)
        plugin = pyFAIintegrationBase(rad_npoint=_range[0], azi_npoint=_range[1])
        plugin.output_data_dim = 1
        with self.assertRaises(NotImplementedError):
            plugin.calculate_result_shape()

    def test_load_and_set_mask__correct(self):
        _maskfilename, _mask = self.create_mask()
        plugin = pyFAIintegrationBase()
        EXP.set_param_value("detector_mask_file", _maskfilename)
        plugin.load_and_set_mask()
        self.assertTrue((plugin._mask == _mask).all())

    def test_load_and_set_mask__wrong_size(self):
        _maskfilename, _mask = self.create_mask()
        plugin = pyFAIintegrationBase()
        EXP.set_param_value("detector_mask_file", _maskfilename)
        EXP.set_detector_params_from_name("Eiger2 9M")
        with self.assertRaises(UserConfigError):
            plugin.pre_execute()

    def test_load_and_set_mask__wrong_local_mask_and_q_settings(self):
        _maskfilename, _mask = self.create_mask()
        plugin = pyFAIintegrationBase()
        plugin._original_input_shape = (123, 50)
        EXP.set_param_value(
            "detector_mask_file", os.path.join(self._temppath, "no_mask.npy")
        )
        with self.assertRaises(UserConfigError):
            plugin.load_and_set_mask()

    def test_pre_execute(self):
        plugin = pyFAIintegrationBase()
        plugin._original_input_shape = (123, 45)
        plugin.pre_execute()
        self.assertIsInstance(plugin._ai, pyFAI.azimuthalIntegrator.AzimuthalIntegrator)

    def test_check_mask_shape__okay(self):
        _maskfilename, _mask = self.create_mask(shape=(3262, 3108))
        _data = np.zeros((3262, 3108))
        plugin = pyFAIintegrationBase()
        EXP.set_param_value("detector_mask_file", _maskfilename)
        EXP.set_detector_params_from_name("Eiger2 9M")
        plugin.pre_execute()
        plugin._check_mask_shape(_data)

    def test_check_mask_shape__wrong_size(self):
        _maskfilename, _mask = self.create_mask(shape=(3262, 3108))
        _data = np.zeros((100, 100))
        plugin = pyFAIintegrationBase()
        EXP.set_param_value("detector_mask_file", _maskfilename)
        EXP.set_detector_params_from_name("Eiger2 9M")
        plugin.pre_execute()
        with self.assertRaises(UserConfigError):
            plugin._check_mask_shape(_data)


if __name__ == "__main__":
    unittest.main()

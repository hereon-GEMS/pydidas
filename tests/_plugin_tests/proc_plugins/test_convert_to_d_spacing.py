# This file is part of pydidas.
#
# Copyright 2024, Helmholtz-Zentrum Hereon
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

__author__ = "Nonni Heere"
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import unittest

import numpy as np
from pydidas.contexts import DiffractionExperiment
from pydidas.core import Dataset, UserConfigError
from pydidas.plugins import BasePlugin
from pydidas.unittest_objects import LocalPluginCollection
from qtpy import QtCore


PLUGIN_COLLECTION = LocalPluginCollection()


class TestConvertToDSpacing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._lambda = 1.3
        cls._detector_distance = 1.6
        cls._EXP = DiffractionExperiment()
        cls._EXP.set_param_values(
            xray_wavelength=cls._lambda, detector_dist=cls._detector_distance
        )
        _range = np.array((0, 2, 10, 25, 325, 2500, 10000, 1e6))
        cls._ref = {
            "Q": (2 * np.pi) / _range[:0:-1],
            "r": cls._lambda
            / (2 * np.sin(np.arctan(_range / (cls._detector_distance * 1e3)) / 2))[
                :0:-1
            ],
            "2theta_deg": cls._lambda / (2 * np.sin(np.radians(_range) / 2))[:0:-1],
            "2theta_rad": cls._lambda / (2 * np.sin(_range / 2))[:0:-1],
        }
        cls._range = _range

    @classmethod
    def tearDownClass(cls):
        qs = QtCore.QSettings("Hereon", "pydidas")
        qs.remove("unittesting")

    def setUp(self):
        self._data = Dataset(np.arange(self._range.size))
        self._data.update_axis_range(0, self._range)

    def get_standard_plugin(self):
        return PLUGIN_COLLECTION.get_plugin_by_name("ConvertToDSpacing")(
            diffraction_exp=self._EXP
        )

    def test_creation(self):
        plugin = self.get_standard_plugin()
        self.assertIsInstance(plugin, BasePlugin)

    def test_execute__q_in_nm(self):
        plugin = self.get_standard_plugin()
        self._data.update_axis_label(0, "Q")
        self._data.update_axis_unit(0, "nm^-1")
        plugin.pre_execute()
        _result, _kwargs = plugin.execute(self._data)
        self.assertEqual(_result.axis_labels[0], "d-spacing")
        self.assertEqual(_result.axis_units[0], "A")
        self.assertTrue(np.allclose(_result.axis_ranges[0], self._ref["Q"] * 10))

    def test_execute__q_in_a(self):
        plugin = self.get_standard_plugin()
        self._data.update_axis_label(0, "Q")
        self._data.update_axis_unit(0, "A^-1")
        plugin.pre_execute()
        _result, _kwargs = plugin.execute(self._data)
        self.assertEqual(_result.axis_labels[0], "d-spacing")
        self.assertEqual(_result.axis_units[0], "A")
        self.assertTrue(np.allclose(_result.axis_ranges[0], self._ref["Q"]))

    def test_execute__r_mm(self):
        plugin = self.get_standard_plugin()
        self._data.update_axis_label(0, "r")
        self._data.update_axis_unit(0, "mm")
        plugin.pre_execute()
        plugin._lambda = self._lambda
        plugin._detector_dist = self._detector_distance
        _result, _kwargs = plugin.execute(self._data)
        self.assertEqual(_result.axis_labels[0], "d-spacing")
        self.assertEqual(_result.axis_units[0], "A")
        self.assertTrue(np.allclose(_result.axis_ranges[0], self._ref["r"]))

    def test_execute__2theta_in_deg(self):
        plugin = self.get_standard_plugin()
        self._data.update_axis_label(0, "2theta")
        self._data.update_axis_unit(0, "deg")
        plugin.pre_execute()
        plugin._lambda = self._lambda
        _result, _kwargs = plugin.execute(self._data)
        self.assertEqual(_result.axis_labels[0], "d-spacing")
        self.assertEqual(_result.axis_units[0], "A")
        self.assertTrue(np.allclose(_result.axis_ranges[0], self._ref["2theta_deg"]))

    def test_execute__2theta_in_rad(self):
        plugin = self.get_standard_plugin()
        self._data.update_axis_label(0, "2theta")
        self._data.update_axis_unit(0, "rad")
        plugin.pre_execute()
        plugin._lambda = self._lambda
        _result, _kwargs = plugin.execute(self._data)
        self.assertEqual(_result.axis_labels[0], "d-spacing")
        self.assertEqual(_result.axis_units[0], "A")
        self.assertTrue(np.allclose(_result.axis_ranges[0], self._ref["2theta_rad"]))

    def test_execute__output_in_nm(self):
        plugin = self.get_standard_plugin()
        plugin.set_param_value("d_spacing_unit", "nm")
        self._data.update_axis_label(0, "Q")
        self._data.update_axis_unit(0, "nm^-1")
        plugin.pre_execute()
        _result, _kwargs = plugin.execute(self._data)
        self.assertEqual(_result.axis_labels[0], "d-spacing")
        self.assertEqual(_result.axis_units[0], "nm")
        self.assertTrue(np.allclose(_result.axis_ranges[0], self._ref["Q"]))

    def test_execute__all_valid_input(self):
        plugin = self.get_standard_plugin()
        plugin.set_param_value("d_spacing_unit", "nm")
        self._data.update_axis_label(0, "Q")
        self._data.update_axis_unit(0, "nm^-1")
        plugin.pre_execute()
        _result, _kwargs = plugin.execute(self._data[1:])
        self.assertTrue(np.allclose(_result.axis_ranges[0], self._ref["Q"]))

    def test_execute__missing_axis_label(self):
        plugin = self.get_standard_plugin()
        plugin.pre_execute()
        with self.assertRaises(UserConfigError):
            plugin.execute(self._data)

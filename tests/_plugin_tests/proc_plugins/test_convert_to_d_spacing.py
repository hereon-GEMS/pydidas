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
from qtpy import QtCore

from pydidas.core import Dataset
from pydidas.plugins import BasePlugin
from pydidas.unittest_objects import LocalPluginCollection


PLUGIN_COLLECTION = LocalPluginCollection()


class TestConvertToDSpacing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._lambda = 1.3
        cls._detector_distance = 1.6

    @classmethod
    def tearDownClass(cls):
        qs = QtCore.QSettings("Hereon", "pydidas")
        qs.remove("unittesting")

    def setUp(self):
        self._data = Dataset(np.ones(8))
        self._data.update_axis_range(0, (0, 10, 25, 325, -5, 2, 10000, 1e6))
        self._ref_q = (2 * np.pi) / self._data.axis_ranges[0]
        self._ref_r = self._lambda / (
            2
            * np.sin(
                np.arctan(self._data.axis_ranges[0] / (self._detector_distance * 1e3))
                / 2
            )
        )
        self._ref_tdeg = self._lambda / (
            2 * np.sin(np.radians(self._data.axis_ranges[0]) / 2)
        )
        self._ref_trad = self._lambda / (2 * np.sin(self._data.axis_ranges[0] / 2))

    def test_creation(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("ConvertToDSpacing")()
        self.assertIsInstance(plugin, BasePlugin)

    def test__execute_qnm(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("ConvertToDSpacing")()
        self._data.update_axis_label(0, "Q")
        self._data.update_axis_unit(0, "nm^-1")
        _result, _kwargs = plugin.execute(self._data)
        self.assertEqual(_result.axis_labels[0], "d-spacing")
        self.assertEqual(_result.axis_units[0], "A")
        self.assertTrue(np.allclose(_result.axis_ranges[0], self._ref_q * 10))

    def test__execute_qna(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("ConvertToDSpacing")()
        self._data.update_axis_label(0, "Q")
        self._data.update_axis_unit(0, "A^-1")
        _result, _kwargs = plugin.execute(self._data)
        self.assertEqual(_result.axis_labels[0], "d-spacing")
        self.assertEqual(_result.axis_units[0], "A")
        self.assertTrue(np.allclose(_result.axis_ranges[0], self._ref_q))

    def test__execute_rmm(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("ConvertToDSpacing")()
        self._data.update_axis_label(0, "r")
        self._data.update_axis_unit(0, "mm")
        plugin._lambda = self._lambda
        plugin._detector_dist = self._detector_distance
        _result, _kwargs = plugin.execute(self._data)
        self.assertEqual(_result.axis_labels[0], "d-spacing")
        self.assertEqual(_result.axis_units[0], "A")
        self.assertTrue(np.allclose(_result.axis_ranges[0], self._ref_r))

    def test__execute_tdeg(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("ConvertToDSpacing")()
        self._data.update_axis_label(0, "2theta")
        self._data.update_axis_unit(0, "deg")
        plugin._lambda = self._lambda
        _result, _kwargs = plugin.execute(self._data)
        self.assertEqual(_result.axis_labels[0], "d-spacing")
        self.assertEqual(_result.axis_units[0], "A")
        self.assertTrue(np.allclose(_result.axis_ranges[0], self._ref_tdeg))

    def test__execute_trad(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("ConvertToDSpacing")()
        self._data.update_axis_label(0, "2theta")
        self._data.update_axis_unit(0, "rad")
        plugin._lambda = self._lambda
        _result, _kwargs = plugin.execute(self._data)
        self.assertEqual(_result.axis_labels[0], "d-spacing")
        self.assertEqual(_result.axis_units[0], "A")
        self.assertTrue(np.allclose(_result.axis_ranges[0], self._ref_trad))

    def test__execute_output_nm(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("ConvertToDSpacing")()
        plugin.set_param_value("d_spacing_unit", "nm")
        self._data.update_axis_label(0, "Q")
        self._data.update_axis_unit(0, "nm^-1")
        _result, _kwargs = plugin.execute(self._data)
        self.assertEqual(_result.axis_labels[0], "d-spacing")
        self.assertEqual(_result.axis_units[0], "nm")
        self.assertTrue(np.allclose(_result.axis_ranges[0], self._ref_q))

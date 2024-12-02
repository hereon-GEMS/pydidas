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
import warnings

import numpy as np
import pyFAI
from pydidas.core import Dataset, UserConfigError
from pydidas.plugins import BasePlugin
from pydidas.unittest_objects import LocalPluginCollection
from pyFAI.distortion import Distortion
from qtpy import QtCore


PLUGIN_COLLECTION = LocalPluginCollection()


class TestCorrectSplineDistortion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._temppath = tempfile.mkdtemp()
        cls.data_shape = (512, 512)
        cls._spline_files = {}
        cls._detectors = {}
        cls._corrections = {}
        cls._data_metadata = {
            "axis_labels": ["ax0", "ax1"],
            "axis_units": ["u0", "u1"],
            "axis_ranges": [
                np.arange(cls.data_shape[0]),
                2 * np.arange(cls.data_shape[1]),
            ],
            "data_label": "test data",
            "data_unit": "cts",
        }
        for _dir, _ext in enumerate(["shrink", "expand"]):
            _factor = 1 - 2 * _dir
            cls._spline_files[_ext] = os.path.join(
                cls._temppath, f"spline_file_{_ext}.txt"
            )
            _spline = pyFAI.spline.Spline()
            _spline.zeros(
                xmax=cls.data_shape[1], ymax=cls.data_shape[0], pixSize=(1, 1)
            )
            _spline.yDispArray = _factor * np.outer(
                np.arange(cls.data_shape[0]) / 128, -np.ones(cls.data_shape[1])
            )
            _spline.xDispArray = _factor * np.outer(
                np.ones(cls.data_shape[0]), (256 - np.arange(cls.data_shape[1])) / 128
            )
            _spline.grid = 50
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                _spline.array2spline()
            _spline.xmax = cls.data_shape[1]
            _spline.ymax = cls.data_shape[0]
            _spline.write(cls._spline_files[_ext])

            cls.spline = _spline
            _detector = pyFAI.detector_factory("FReLoN")
            _detector.set_splineFile(cls._spline_files[_ext])
            cls._detectors[_ext] = _detector
            cls._corrections[_ext] = Distortion(cls._detectors[_ext])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._temppath)
        qs = QtCore.QSettings("Hereon", "pydidas")
        qs.remove("unittesting")

    def create_input_dataset(self):
        return Dataset(np.ones(self.data_shape), **self._data_metadata)

    def check_output_data_keys(self, data_in, data_out):
        for _key in self._data_metadata:
            if _key == "axis_ranges":
                _ax_in = getattr(data_in, _key)
                _ax_out = getattr(data_out, _key)
                self.assertTrue(np.allclose(_ax_in[0], _ax_out[0]))
                self.assertTrue(np.allclose(_ax_in[1], _ax_out[1]))
            else:
                self.assertEqual(getattr(data_in, _key), getattr(data_out, _key))

    def check_shrunk_nan_mask(self, mask):
        """
        Check the shrunk mask (in fit2D geometry) is "correct".
        """
        self.assertTrue(np.allclose(mask[:3], 1))
        self.assertTrue(np.allclose(mask[-1, 3:-3], 0))
        self.assertTrue(np.allclose(mask[:, (0, 1, -2, -1)], 1))

    def test_creation(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("CorrectSplineDistortion")()
        self.assertIsInstance(plugin, BasePlugin)

    def test_pre_execute__wrong_filename(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("CorrectSplineDistortion")()
        plugin.set_param_value("spline_file", self._temppath)
        with self.assertRaises(UserConfigError):
            plugin.pre_execute()

    def test_pre_execute__fit2d_geo_shrink(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("CorrectSplineDistortion")()
        plugin.set_param_value("spline_file", self._spline_files["shrink"])
        plugin.set_param_value("geometry", "Fit2D")
        plugin.pre_execute()
        self.assertIsInstance(plugin._detector, pyFAI.detectors.Detector)
        self.assertIsInstance(plugin._correction, pyFAI.distortion.Distortion)
        self.check_shrunk_nan_mask(plugin._nan_mask)

    def test_pre_execute__fit2d_geo_expand(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("CorrectSplineDistortion")()
        plugin.set_param_value("spline_file", self._spline_files["expand"])
        plugin.set_param_value("geometry", "Fit2D")
        plugin.pre_execute()
        self.assertIsInstance(plugin._detector, pyFAI.detectors.Detector)
        self.assertIsInstance(plugin._correction, pyFAI.distortion.Distortion)
        self.assertTrue(np.allclose(plugin._nan_mask, 0))

    def test_pre_execute__pyFAI_spline_geometry(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("CorrectSplineDistortion")()
        plugin.set_param_value("spline_file", self._spline_files["shrink"])
        plugin.set_param_value("geometry", "pyFAI")
        plugin.pre_execute()
        self.assertIsInstance(plugin._detector, pyFAI.detectors.Detector)
        self.assertIsInstance(plugin._correction, pyFAI.distortion.Distortion)
        self.check_shrunk_nan_mask(np.flipud(plugin._nan_mask))

    def test_execute__pyFAI_shrink_no_fill(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("CorrectSplineDistortion")()
        plugin.set_param_value("spline_file", self._spline_files["shrink"])
        plugin.set_param_value("geometry", "pyFAI")
        plugin.set_param_value("fill_nan", False)
        plugin.pre_execute()
        _data_in = self.create_input_dataset()
        _data_out, _kws = plugin.execute(_data_in.copy())
        self.check_output_data_keys(_data_in, _data_out)
        self.assertEqual(0, np.where(_data_out == np.nan)[0].size)

    def test_execute__pyFAI_expand_no_fill(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("CorrectSplineDistortion")()
        plugin.set_param_value("spline_file", self._spline_files["expand"])
        plugin.set_param_value("geometry", "pyFAI")
        plugin.set_param_value("fill_nan", False)
        plugin.pre_execute()
        _data_in = self.create_input_dataset()
        _data_out, _kws = plugin.execute(_data_in.copy())
        self.check_output_data_keys(_data_in, _data_out)
        self.assertEqual(0, np.where(_data_out == np.nan)[0].size)

    def test_execute__pyFAI_fill_nan_shrink(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("CorrectSplineDistortion")()
        plugin.set_param_value("spline_file", self._spline_files["shrink"])
        plugin.set_param_value("geometry", "pyFAI")
        plugin.set_param_value("fill_nan", True)
        plugin.pre_execute()
        _data_in = self.create_input_dataset()
        _data_out, _kws = plugin.execute(_data_in.copy())
        self.check_output_data_keys(_data_in, _data_out)
        self.assertTrue(np.isnan(_data_out[-3:]).all())
        self.assertTrue(np.isfinite(_data_out[0, 3:-3]).all())
        self.assertTrue(np.isnan(_data_out.array[:, (0, 1, -2, -1)]).all())


if __name__ == "__main__":
    unittest.main()

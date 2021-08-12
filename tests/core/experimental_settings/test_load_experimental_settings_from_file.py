# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""Unit tests for pydidas modules."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import os
import unittest
import shutil
import tempfile

import yaml
import numpy as np
from pyFAI.geometry import Geometry

from pydidas.core.experimental_settings import (ExperimentalSettings,
                                                LoadExperimentSettingsFromFile)

EXP_SETTINGS = ExperimentalSettings()


class TestLoadExperimentSettingsFromFile(unittest.TestCase):

    def setUp(self):
        _test_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self._path = os.path.join(_test_dir, '_data', 'load_test_exp_settings_')
        self._tmppath = tempfile.mkdtemp()

    def tearDown(self):
        del self._path
        shutil.rmtree(self._tmppath)

    def test_creation(self):
        obj = LoadExperimentSettingsFromFile()
        self.assertIsInstance(obj, LoadExperimentSettingsFromFile)

    def test_load_no_file(self):
        obj = LoadExperimentSettingsFromFile()
        with self.assertRaises(FileNotFoundError):
            obj.load_from_file('None')

    def test_load_poni(self):
        LoadExperimentSettingsFromFile(self._path + 'poni.poni')
        geo = Geometry().load(self._path + 'poni.poni').getPyFAI()
        for key in ['detector_dist', 'detector_poni1', 'detector_poni2',
                    'detector_rot1', 'detector_rot2', 'detector_rot3']:
            self.assertEqual(EXP_SETTINGS.get_param_value(key),
                             geo[key.split('_')[1]])

    def test_load_yaml(self):
        LoadExperimentSettingsFromFile(self._path + 'yaml.yml')
        with open(self._path + 'yaml.yml', 'r') as stream:
            _data = yaml.safe_load(stream)
        for key in ['detector_dist', 'detector_poni1', 'detector_poni2',
                    'detector_rot1', 'detector_rot2', 'detector_rot3']:
            self.assertEqual(EXP_SETTINGS.get_param_value(key),
                             _data[key])

    def test_load_yaml_with_error(self):
        np.save(self._tmppath + 'error.npy', np.zeros((4,4)))
        shutil.move(self._tmppath + 'error.npy', self._tmppath + 'error.yaml')
        with self.assertRaises(yaml.YAMLError):
            LoadExperimentSettingsFromFile(self._tmppath + 'error.yaml')

    def test_load_wrong_ext(self):
        _fname = self._tmppath + 'unknown.any'
        with open(_fname, 'w') as f:
            f.write('test')
        with self.assertRaises(KeyError):
            LoadExperimentSettingsFromFile(_fname)

    def test__update_detector_from_pyfai_wrong_type(self):
        det = 12
        loader = LoadExperimentSettingsFromFile()
        with self.assertRaises(TypeError):
            loader._LoadExperimentSettingsFromFile__update_detector_from_pyFAI(
                det)

    def test__update_geometry_from_pyFAI_wrong_type(self):
        det = 12
        loader = LoadExperimentSettingsFromFile()
        with self.assertRaises(TypeError):
            loader._LoadExperimentSettingsFromFile__update_geometry_from_pyFAI(
                det)

    def test__verify_all_entries_present(self):
        loader = LoadExperimentSettingsFromFile()
        with self.assertRaises(KeyError):
            loader._LoadExperimentSettingsFromFile__verify_all_entries_present()


if __name__ == "__main__":
    unittest.main()

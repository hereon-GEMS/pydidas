# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Unit tests for pydidas modules."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import os
import unittest
import shutil
import tempfile

import yaml
import numpy as np
import pyFAI
from pyFAI.geometry import Geometry

from pydidas.core.experimental_settings import (ExperimentalSettings,
                                                LoadExperimentSettingsFromFileMixIn)
from pydidas.core.experimental_settings.experimental_settings import DEFAULTS
from pydidas.core import ObjectWithParameterCollection

EXP_SETTINGS = ExperimentalSettings()

class TestClass(ObjectWithParameterCollection,
                LoadExperimentSettingsFromFileMixIn):
    default_params = DEFAULTS

    def __init__(self):
        ObjectWithParameterCollection.__init__(self)
        self.set_default_params()
        self.tmp_params = {}

class TestLoadExperimentSettingsFromFileMixIn(unittest.TestCase):

    def setUp(self):
        _test_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self._path = os.path.join(_test_dir, '_data', 'load_test_exp_settings_')
        self._tmppath = tempfile.mkdtemp()

    def tearDown(self):
        del self._path
        shutil.rmtree(self._tmppath)

    def test_creation(self):
        obj = TestClass()
        self.assertIsInstance(obj, LoadExperimentSettingsFromFileMixIn)

    def test_update_geometry_from_pyFAI__correct(self):
        obj = TestClass()
        geo = pyFAI.geometry.Geometry().load(self._path + 'poni.poni')
        obj._LoadExperimentSettingsFromFileMixIn__update_geometry_from_pyFAI(
            geo)
        for param in ['detector_dist', 'detector_poni1', 'detector_poni2',
                      'detector_rot1', 'detector_rot2', 'detector_rot3',
                      'xray_wavelength', 'xray_energy']:
            self.assertTrue(param in obj.tmp_params)

    def test_update_geometry_from_pyFAI__wrong_type(self):
        obj = TestClass()
        with self.assertRaises(TypeError):
            obj._LoadExperimentSettingsFromFileMixIn__update_geometry_from_pyFAI(
                12)

    def test_update_detector_from_pyfai__correct(self):
        obj = TestClass()
        det = pyFAI.detector_factory('Eiger 9M')
        obj._LoadExperimentSettingsFromFileMixIn__update_detector_from_pyFAI(
            det)

    def test_update_detector_from_pyfai__wrong_type(self):
        obj = TestClass()
        det = 12
        with self.assertRaises(TypeError):
            obj._LoadExperimentSettingsFromFileMixIn__update_detector_from_pyFAI(
                det)

    def test_write_to_exp_settings(self):
        _det_name = 'Test Name'
        _energy = 123.45
        obj = TestClass()
        obj.tmp_params = {'detector_name': _det_name, 'xray_energy': _energy}
        obj._LoadExperimentSettingsFromFileMixIn__write_to_exp_settings()
        self.assertEqual(obj.get_param_value('detector_name'), _det_name)
        self.assertEqual(obj.get_param_value('xray_energy'), _energy)

    def test_verify_all_entries_present__correct(self):
        obj = TestClass()
        for param in EXP_SETTINGS.params:
            obj.tmp_params[param] = True
        obj._LoadExperimentSettingsFromFileMixIn__verify_all_entries_present()

    def test_verify_all_entries_present__missing_keys(self):
        obj = TestClass()
        with self.assertRaises(KeyError):
            obj._LoadExperimentSettingsFromFileMixIn__verify_all_entries_present()

    def test_load_no_file(self):
        obj = TestClass()
        with self.assertRaises(FileNotFoundError):
            obj.load_from_file('None')

    def test_load_poni(self):
        obj = TestClass()
        obj.load_from_file(self._path + 'poni.poni')
        geo = Geometry().load(self._path + 'poni.poni').getPyFAI()
        for key in ['detector_dist', 'detector_poni1', 'detector_poni2',
                    'detector_rot1', 'detector_rot2', 'detector_rot3']:
            self.assertEqual(obj.get_param_value(key),
                              geo[key.split('_')[1]])

    def test_load_yaml(self):
        obj = TestClass()
        obj.load_from_file(self._path + 'poni.poni')
        with open(self._path + 'yaml.yml', 'r') as stream:
            _data = yaml.safe_load(stream)
        for key in ['detector_dist', 'detector_poni1', 'detector_poni2',
                    'detector_rot1', 'detector_rot2', 'detector_rot3']:
            self.assertEqual(obj.get_param_value(key),
                              _data[key])

    def test_load_yaml_with_error(self):
        obj = TestClass()
        np.save(self._tmppath + 'error.npy', np.zeros((4,4)))
        shutil.move(self._tmppath + 'error.npy', self._tmppath + 'error.yaml')
        with self.assertRaises(yaml.YAMLError):
            obj.load_from_file(self._tmppath + 'error.yaml')

    def test_load_wrong_ext(self):
        obj = TestClass()
        _fname = self._tmppath + 'unknown.any'
        with open(_fname, 'w') as f:
            f.write('test')
        with self.assertRaises(KeyError):
            obj.load_from_file(_fname)


if __name__ == "__main__":
    unittest.main()

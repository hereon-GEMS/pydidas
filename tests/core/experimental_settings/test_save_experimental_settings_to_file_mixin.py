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

import unittest
import tempfile
import shutil

import yaml
from pyFAI.geometry import Geometry

from pydidas.core.experimental_settings import (
    ExperimentalSettings, SaveExperimentSettingsToFileMixIn)
from pydidas.core import ObjectWithParameterCollection
from pydidas.core.experimental_settings.experimental_settings import DEFAULTS

EXP_SETTINGS = ExperimentalSettings()

class TestClass(ObjectWithParameterCollection,
                SaveExperimentSettingsToFileMixIn):
    default_params = DEFAULTS

    def __init__(self):
        ObjectWithParameterCollection.__init__(self)
        self.set_default_params()
        self.tmp_params = {}


class TestSaveExperimentSettingsToFileMixIn(unittest.TestCase):

    def setUp(self):
        self._path = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self._path)

    def test_creation(self):
        obj = TestClass()
        self.assertIsInstance(obj, SaveExperimentSettingsToFileMixIn)

    def test_save_no_file_extension(self):
        obj = TestClass()
        with self.assertRaises(KeyError):
            obj.save_to_file('None')

    def test_save_poni_file(self):
        obj = TestClass()
        obj.fname = self._path + 'poni.poni'
        obj._SaveExperimentSettingsToFileMixIn__save_poni_file()
        geo = Geometry().load(self._path + 'poni.poni').getPyFAI()
        for key in ['detector_dist', 'detector_poni1', 'detector_poni2',
                    'detector_rot1', 'detector_rot2', 'detector_rot3']:
            self.assertEqual(obj.get_param_value(key),
                              geo[key.split('_')[1]])

    def test_save_yaml_file(self):
        obj = TestClass()
        obj.fname = self._path + 'yaml.yml'
        obj._SaveExperimentSettingsToFileMixIn__save_yaml_file()
        with open(self._path + 'yaml.yml', 'r') as stream:
            _data = yaml.safe_load(stream)
        for key in ['detector_dist', 'detector_poni1', 'detector_poni2',
                    'detector_rot1', 'detector_rot2', 'detector_rot3']:
            self.assertEqual(obj.get_param_value(key),
                              _data[key])

    def test_save_poni_without_det_config(self):
        obj = TestClass()
        obj.set_param_value('detector_name', 'pilatus1m_cdte')
        obj.save_to_file(self._path + 'poni.poni')
        with open(self._path + 'poni.poni', 'r') as f:
            lines = f.readlines()
        self.assertTrue('Detector_config: {}\n' in lines)


if __name__ == "__main__":
    unittest.main()

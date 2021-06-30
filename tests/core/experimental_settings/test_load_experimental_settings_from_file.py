"""
Unittests for the CompositeImage class from the pydidas.core module.
"""

import os
import tempfile
import shutil
import unittest

import yaml
from pyFAI.geometry import Geometry

from pydidas.core.experimental_settings import (ExperimentalSettings,
                                                LoadExperimentSettingsFromFile)


EXP_SETTINGS = ExperimentalSettings()


class TestLoadExperimentSettingsFromFile(unittest.TestCase):

    def setUp(self):
        _test_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self._path = os.path.join(_test_dir, '_data', 'load_test_exp_settings_')

    def tearDown(self):
        del self._path

    def test_creation(self):
        obj = LoadExperimentSettingsFromFile()
        self.assertIsInstance(obj, LoadExperimentSettingsFromFile)

    def test_load_no_file(self):
        obj = LoadExperimentSettingsFromFile()
        with self.assertRaises(FileNotFoundError):
            obj.load_from_file('None')

    def test_load_poni(self):
        obj = LoadExperimentSettingsFromFile(self._path + 'poni.poni')
        geo = Geometry().load(self._path + 'poni.poni').getPyFAI()
        for key in ['detector_dist', 'detector_poni1', 'detector_poni2',
                    'detector_rot1', 'detector_rot2', 'detector_rot3']:
            self.assertEqual(EXP_SETTINGS.get_param_value(key),
                             geo[key.split('_')[1]])

    def test_load_yaml(self):
        obj = LoadExperimentSettingsFromFile(self._path + 'yaml.yml')
        with open(self._path + 'yaml.yml', 'r') as stream:
            _data = yaml.safe_load(stream)
        for key in ['detector_dist', 'detector_poni1', 'detector_poni2',
                    'detector_rot1', 'detector_rot2', 'detector_rot3']:
            self.assertEqual(EXP_SETTINGS.get_param_value(key),
                             _data[key])


if __name__ == "__main__":
    unittest.main()

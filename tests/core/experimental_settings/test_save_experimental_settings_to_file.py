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
                                                SaveExperimentSettingsToFile)


EXP_SETTINGS = ExperimentalSettings()


class TestLoadExperimentSettingsFromFile(unittest.TestCase):

    def setUp(self):
        # self._path = tempfile.mkdtemp()
        self._path = 'e:\\tmp\\'

    def tearDown(self):
        # shutil.rmtree(self._path)
        ...

    def test_creation(self):
        obj = SaveExperimentSettingsToFile()
        self.assertIsInstance(obj, SaveExperimentSettingsToFile)

    def test_save_no_file_extension(self):
        obj = SaveExperimentSettingsToFile()
        with self.assertRaises(TypeError):
            obj.save_to_file('None')

    def test_save_poni(self):
        SaveExperimentSettingsToFile(self._path + 'poni.poni')
        geo = Geometry().load(self._path + 'poni.poni').getPyFAI()
        for key in ['detector_dist', 'detector_poni1', 'detector_poni2',
                    'detector_rot1', 'detector_rot2', 'detector_rot3']:
            self.assertEqual(EXP_SETTINGS.get_param_value(key),
                              geo[key.split('_')[1]])

    def test_save_yaml(self):
        SaveExperimentSettingsToFile(self._path + 'yaml.yml')
        with open(self._path + 'yaml.yml', 'r') as stream:
            _data = yaml.safe_load(stream)
        for key in ['detector_dist', 'detector_poni1', 'detector_poni2',
                    'detector_rot1', 'detector_rot2', 'detector_rot3']:
            self.assertEqual(EXP_SETTINGS.get_param_value(key),
                              _data[key])


if __name__ == "__main__":
    unittest.main()

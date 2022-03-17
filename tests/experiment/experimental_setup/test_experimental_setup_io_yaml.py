# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
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
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import os
import unittest
import shutil
import tempfile

import yaml

from pydidas.experiment import ExperimentalSetup
from pydidas.experiment.experimental_setup.experimental_setup_io_yaml import (
    ExperimentalSetupIoYaml)


EXP_SETTINGS = ExperimentalSetup()
EXP_IO_YAML = ExperimentalSetupIoYaml


class TestExperimentSettingsIoYaml(unittest.TestCase):

    def setUp(self):
        _test_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(__file__)))
        self._path = os.path.join(_test_dir, '_data',
                                  'load_test_exp_settings_')
        self._tmppath = tempfile.mkdtemp()

    def tearDown(self):
        del self._path
        shutil.rmtree(self._tmppath)

    def test_import_from_file__correct(self):
        EXP_IO_YAML.import_from_file(self._path + 'yaml.yml')
        with open(self._path + 'yaml.yml', 'r') as stream:
            _data = yaml.safe_load(stream)
        for key in ['detector_dist', 'detector_poni1', 'detector_poni2',
                    'detector_rot1', 'detector_rot2', 'detector_rot3']:
            self.assertEqual(EXP_SETTINGS.get_param_value(key),
                             _data[key])

    def test_import_from_file__missing_keys(self):
        with open(self._tmppath + 'yaml.yml', 'w') as stream:
            stream.write('no_entry: True')
        with self.assertRaises(KeyError):
            EXP_IO_YAML.import_from_file(self._tmppath + 'yaml.yml')

    def test_import_from_file__wrong_format(self):
        with open(self._tmppath + 'yaml.yml', 'w') as stream:
            stream.write('no_entry =True')
        with self.assertRaises(AssertionError):
            EXP_IO_YAML.import_from_file(self._tmppath + 'yaml.yml')

    def test_export_to_file(self):
        _fname = self._tmppath + 'yaml.yml'
        EXP_IO_YAML.export_to_file(_fname)
        with open(self._tmppath + 'yaml.yml', 'r') as stream:
            _data = yaml.safe_load(stream)
        for key in EXP_SETTINGS.params:
            if key != 'xray_energy':
                self.assertEqual(EXP_SETTINGS.get_param_value(key),
                                 _data[key])


if __name__ == "__main__":
    unittest.main()

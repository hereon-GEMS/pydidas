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
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import os
import unittest
import shutil
import tempfile
import logging

import pyFAI
from pyFAI.geometry import Geometry

from pydidas.experiment import ExperimentalSetup
from pydidas.experiment.experimental_setup.experimental_setup_io_poni import \
    ExperimentalSetupIoPoni

import pyFAI.geometry


EXP_SETTINGS = ExperimentalSetup()
EXP_IO_PONI = ExperimentalSetupIoPoni

_logger = logging.getLogger('pyFAI.geometry')
_logger.setLevel(logging.CRITICAL)


class TestExperimentSettingsIoPoni(unittest.TestCase):

    def setUp(self):
        _test_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self._path = os.path.join(_test_dir, '_data', 'load_test_exp_settings_')
        self._tmppath = tempfile.mkdtemp()

    def tearDown(self):
        del self._path
        shutil.rmtree(self._tmppath)

    def test_update_geometry_from_pyFAI__correct(self):
        geo = pyFAI.geometry.Geometry().load(self._path + 'poni.poni')
        EXP_IO_PONI._update_geometry_from_pyFAI(geo)
        for param in ['detector_dist', 'detector_poni1', 'detector_poni2',
                      'detector_rot1', 'detector_rot2', 'detector_rot3',
                      'xray_wavelength', 'xray_energy']:
            self.assertTrue(param in EXP_IO_PONI.imported_params)

    def test_update_geometry_from_pyFAI__wrong_type(self):
        with self.assertRaises(TypeError):
            EXP_IO_PONI._update_geometry_from_pyFAI(12)

    def test_update_detector_from_pyfai__correct(self):
        det = pyFAI.detector_factory('Eiger 9M')
        EXP_IO_PONI._update_detector_from_pyFAI(det)

    def test_update_detector_from_pyfai__wrong_type(self):
        det = 12
        with self.assertRaises(TypeError):
            EXP_IO_PONI._update_detector_from_pyFAI(det)

    def test_import_from_file(self):
        EXP_IO_PONI.import_from_file(self._path + 'poni.poni')
        geo = Geometry().load(self._path + 'poni.poni').getPyFAI()
        for key in ['detector_dist', 'detector_poni1', 'detector_poni2',
                    'detector_rot1', 'detector_rot2', 'detector_rot3']:
            self.assertEqual(EXP_SETTINGS.get_param_value(key),
                             geo[key.split('_')[1]])

    def test_export_to_file(self):
        _fname = self._tmppath + 'poni.poni'
        EXP_IO_PONI.export_to_file(_fname)
        with open(_fname, 'r') as f:
            content = f.read()
        for key in ['Detector', 'Detector_config', 'Distance', 'Poni1',
                    'Poni2', 'Rot1', 'Rot2', 'Rot3', 'Wavelength']:
            self.assertTrue(content.find(key) > 0)


if __name__ == "__main__":
    unittest.main()

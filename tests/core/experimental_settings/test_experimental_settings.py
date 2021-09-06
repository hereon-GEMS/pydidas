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
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import unittest
import copy

from pydidas.core.experimental_settings import ExperimentalSettings
from pydidas.core.experimental_settings.experimental_settings import (
    _ExpSettings)
from pydidas.config import LAMBDA_TO_E


class TestExperimentalSettings(unittest.TestCase):

    def setUp(self):
        ...

    def tearDown(self):
        ...

    def test_creation(self):
        obj = ExperimentalSettings()
        self.assertIsInstance(obj, _ExpSettings)

    def test_set_param_generic(self):
        _name = 'Test'
        obj = ExperimentalSettings()
        obj.set_param_value('detector_name', _name)
        self.assertEqual(obj.get_param_value('detector_name'), _name)

    def test_set_param_energy(self):
        _new_E = 15.7
        obj = ExperimentalSettings()
        obj.set_param_value('xray_energy', _new_E)
        self.assertEqual(obj.get_param_value('xray_energy'), _new_E)
        self.assertAlmostEqual(obj.get_param_value('xray_wavelength'),
                               0.7897080652951567, delta=0.00005)

    def test_set_param_wavelength(self):
        _new_lambda = 0.98765
        obj = ExperimentalSettings()
        obj.set_param_value('xray_wavelength', _new_lambda)
        self.assertEqual(obj.get_param_value('xray_wavelength'), _new_lambda)
        self.assertAlmostEqual(obj.get_param_value('xray_energy'),
                               12.55345175429956, delta=0.0005)

    def test_copy(self):
        obj = ExperimentalSettings()
        obj2 = copy.copy(obj)
        self.assertEqual(obj, obj2)


if __name__ == "__main__":
    unittest.main()

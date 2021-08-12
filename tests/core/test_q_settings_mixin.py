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

import unittest
import copy

from PyQt5 import QtCore

from pydidas.core import (PydidasQsettingsMixin, ParameterCollection,
                          Parameter)
from pydidas.core.pydidas_q_settings_mixin import copyableQSettings


class TestQSettingsMixin(unittest.TestCase):

    def setUp(self):
        self._params = ParameterCollection(
            Parameter('param_float', float, default=123.45),
            Parameter('param_int', int, default=23),
            Parameter('param_str', str, default='test123'))
        self.q_settings = QtCore.QSettings('Hereon', 'pydidas')
        for key in self._params:
            self.q_settings.setValue(f'global/{key}',
                                     self._params.get_value(key))

    def tearDown(self):
        for key in self._params:
            self.q_settings.remove(f'global/{key}')

    def test_creation(self):
        obj = PydidasQsettingsMixin()
        self.assertIsInstance(obj, PydidasQsettingsMixin)
        self.assertTrue(hasattr(obj, 'q_settings'))
        self.assertIsInstance(obj.q_settings, copyableQSettings)

    def test_qsettings_convert_value_type_no_param(self):
        _value = [123, 456]
        obj = PydidasQsettingsMixin()
        _newval = obj._qsettings_convert_value_type('test', _value)
        self.assertEqual(_value, _newval)

    def test_qsettings_convert_value_type_float(self):
        _value = self._params.get_value('param_float')
        obj = PydidasQsettingsMixin()
        obj.params = self._params
        obj.get_param = obj.params.get
        _newval = obj._qsettings_convert_value_type('param_float', _value)
        self.assertEqual(_value, _newval)

    def test_qsettings_convert_value_type_int(self):
        _value = self._params.get_value('param_int')
        obj = PydidasQsettingsMixin()
        obj.params = self._params
        obj.get_param = obj.params.get
        _newval = obj._qsettings_convert_value_type('param_int', _value)
        self.assertEqual(_value, _newval)

    def test_qsettings_convert_value_type_other(self):
        _value = self._params.get_value('param_str')
        obj = PydidasQsettingsMixin()
        obj.params = self._params
        obj.get_param = obj.params.get
        _newval = obj._qsettings_convert_value_type('param_str', _value)
        self.assertEqual(_value, _newval)

    def test_q_settings_get_global_value(self):
        obj = PydidasQsettingsMixin()
        obj.params = self._params
        obj.get_param = obj.params.get
        _val = obj.q_settings_get_global_value('param_float')
        self.assertEqual(_val, self._params.get_value('param_float'))

    def test_copyableQSettings_copy(self):
        _qsettings = copyableQSettings('Hereon', 'pydidas')
        _copy = copy.copy(_qsettings)
        self.assertIsInstance(_copy, copyableQSettings)
        self.assertNotEqual(_qsettings, _copy)


if __name__ == "__main__":
    unittest.main()

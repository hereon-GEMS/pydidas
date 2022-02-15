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
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import unittest
import copy
import pickle

from qtpy import QtCore

from pydidas.core import (PydidasQsettingsMixin, ParameterCollection,
                          Parameter, CopyableQSettings)


class TestPydidasQSettingsMixin(unittest.TestCase):

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
        self.assertIsInstance(obj.q_settings, CopyableQSettings)

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

    def test_q_settings_get_global_value__plain(self):
        obj = PydidasQsettingsMixin()
        obj.params = self._params
        obj.get_param = obj.params.get
        _val = obj.q_settings_get_global_value('param_float')
        self.assertEqual(_val, self._params.get_value('param_float'))

    def test_q_settings_get_global_value__with_argtype(self):
        obj = PydidasQsettingsMixin()
        _val = obj.q_settings_get_global_value('param_float', float)
        self.assertTrue(isinstance(_val, float))
        self.assertEqual(_val, self._params.get_value('param_float'))

    def test_q_settings_pickle(self):
        obj = PydidasQsettingsMixin()
        obj.params = self._params
        new_obj = pickle.loads(pickle.dumps(obj))
        self.assertIsInstance(new_obj, PydidasQsettingsMixin)

    def test_CopyableQSettings_copy(self):
        _qsettings = CopyableQSettings('Hereon', 'pydidas')
        _copy = copy.copy(_qsettings)
        self.assertIsInstance(_copy, CopyableQSettings)
        self.assertNotEqual(_qsettings, _copy)

    def test_CopyableQSettings_getstate(self):
        _qsettings = CopyableQSettings('some', 'thing')
        _state = _qsettings.__getstate__()
        self.assertEqual(_state['org_name'], 'some')
        self.assertEqual(_state['app_name'], 'thing')

    def test_CopyableQSettings_setstate(self):
        _qsettings = CopyableQSettings('some', 'thing')
        _state = {'org_name': 'Hereon', 'app_name': 'pydidas'}
        _qsettings.__setstate__(_state)
        self.assertEqual(_qsettings.organizationName(), _state['org_name'])
        self.assertEqual(_qsettings.applicationName(), _state['app_name'])

    def test_CopyableQSettings_pickle(self):
        _qsettings = CopyableQSettings('Hereon', 'pydidas')
        _new = pickle.loads(pickle.dumps(_qsettings))
        self.assertIsInstance(_new, CopyableQSettings)
        self.assertEqual(_qsettings.organizationName(), 'Hereon')
        self.assertEqual(_qsettings.applicationName(), 'pydidas')


if __name__ == "__main__":
    unittest.main()

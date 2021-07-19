"""
Unittests for the CompositeImage class from the pydidas.core module.
"""

import os
import tempfile
import shutil
import unittest

import numpy as np
from PyQt5 import QtCore

from pydidas.core import PydidasQsettingsMixin, ParameterCollection, Parameter
from pydidas.core.pydidas_q_settings_mixin import copyableQSettings
from pydidas._exceptions import AppConfigError

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
        _newval = obj._qsettings_convert_value_type('param_float', _value)
        self.assertEqual(_value, _newval)

    def test_qsettings_convert_value_type_int(self):
        _value = self._params.get_value('param_int')
        obj = PydidasQsettingsMixin()
        obj.params = self._params
        _newval = obj._qsettings_convert_value_type('param_int', _value)
        self.assertEqual(_value, _newval)

    def test_qsettings_convert_value_type_other(self):
        _value = self._params.get_value('param_str')
        obj = PydidasQsettingsMixin()
        obj.params = self._params
        _newval = obj._qsettings_convert_value_type('param_str', _value)
        self.assertEqual(_value, _newval)

    def test_q_settings_get_global_value(self):
        obj = PydidasQsettingsMixin()
        obj.params = self._params
        obj.get_param = obj.params.get
        _val = obj.q_settings_get_global_value('param_float')
        self.assertEqual(_val, self._params.get_value('param_float'))

if __name__ == "__main__":
    unittest.main()

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
import tempfile
import os
import shutil
from contextlib import redirect_stdout


from qtpy import QtCore

from pydidas.core import (PydidasQsettings, ParameterCollection,
                          Parameter, CopyableQSettings)


class TestPydidasQSettings(unittest.TestCase):

    def setUp(self):
        self._tmpdir = tempfile.mkdtemp()
        self._params = ParameterCollection(
            Parameter('param_float', float, default=123.45),
            Parameter('param_int', int, default=23),
            Parameter('param_str', str, default='test123'))
        self.q_settings = QtCore.QSettings('Hereon', 'pydidas')
        for key in self._params:
            self.q_settings.setValue(f'global/{key}',
                                     self._params.get_value(key))

    def tearDown(self):
        shutil.rmtree(self._tmpdir)
        for key in self._params:
            self.q_settings.remove(f'global/{key}')

    def test_creation(self):
        obj = PydidasQsettings()
        self.assertIsInstance(obj, PydidasQsettings)
        self.assertTrue(hasattr(obj, 'q_settings'))
        self.assertIsInstance(obj.q_settings, CopyableQSettings)

    def test_show_all_stored_q_settings(self):
        obj = PydidasQsettings()
        _fname = os.path.join(self._tmpdir, 'out.txt')
        with open(_fname, 'w') as _f:
            with redirect_stdout(_f):
                obj.show_all_stored_q_settings()
        with open(_fname, 'r') as _f:
            _text = _f.read()
        for _key in self._params:
            _val = self._params.get_value(_key)
            self.assertIn(f'global/{_key}: {_val}', _text)

    def test_get_all_stored_q_settings(self):
        obj = PydidasQsettings()
        _settings = obj.get_all_stored_q_settings()
        for _key, _param in self._params.items():
            _stored_val = _settings[f'global/{_key}']
            self.assertEqual(str(_param.value), str(_stored_val))

    def test_set_value(self):
        _val = -456.789
        obj = PydidasQsettings()
        obj.set_value('global/param_float', _val)
        _settings = obj.get_all_stored_q_settings()
        self.assertEqual(float(_settings['global/param_float']), _val)


if __name__ == "__main__":
    unittest.main()

# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
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
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import copy
import pickle
import unittest
from numbers import Integral, Real

from qtpy import QtCore

from pydidas.core import Parameter, ParameterCollection, PydidasQsettingsMixin
from pydidas.core.pydidas_q_settings_mixin import _CopyablePydidasQSettings


VERSION = "unittesting"


class TestPydidasQSettingsMixin(unittest.TestCase):
    def setUp(self):
        self._params = ParameterCollection(
            Parameter("param_float", float, default=123.45),
            Parameter("param_int", int, default=23),
            Parameter("param_str", str, default="test123"),
            Parameter("param_bool", int, default=True, choices=[True, False]),
        )
        self.q_settings = QtCore.QSettings("Hereon", "pydidas")
        self.q_settings.setValue("old_version/param_int", 42)
        for key in self._params:
            self.q_settings.setValue(f"{VERSION}/{key}", self._params.get_value(key))

    def tearDown(self):
        self.q_settings.remove("old_version")
        self.q_settings.remove(VERSION)

    def test_creation(self):
        obj = PydidasQsettingsMixin(version="unittesting")
        self.assertIsInstance(obj, PydidasQsettingsMixin)
        self.assertTrue(hasattr(obj, "q_settings"))
        self.assertIsInstance(obj.q_settings, _CopyablePydidasQSettings)

    def test_q_settings_get_value__plain(self):
        obj = PydidasQsettingsMixin(version="unittesting")
        obj.params = self._params
        obj.get_param = obj.params.get
        _val = obj.q_settings_get("param_float")
        self.assertEqual(float(_val), self._params.get_value("param_float"))

    def test_q_settings_get_value__with_dtype(self):
        obj = PydidasQsettingsMixin(version="unittesting")
        _val = obj.q_settings_get("param_float", dtype=float)
        self.assertTrue(isinstance(_val, float))
        self.assertEqual(_val, self._params.get_value("param_float"))

    def test_q_settings_get_value__with_bool(self):
        obj = PydidasQsettingsMixin(version="unittesting")
        _val = obj.q_settings_get("param_bool", dtype=bool)
        self.assertTrue(isinstance(_val, bool))
        self.assertEqual(_val, self._params.get_value("param_bool"))

    def test_q_settings_get_value__with_Integral(self):
        obj = PydidasQsettingsMixin(version="unittesting")
        _val = obj.q_settings_get("param_int", dtype=Integral)
        self.assertTrue(isinstance(_val, int))
        self.assertEqual(_val, self._params.get_value("param_int"))

    def test_q_settings_get_value__int_with_bool(self):
        obj = PydidasQsettingsMixin(version="unittesting")
        _val = obj.q_settings_get("param_bool", dtype=Integral)
        self.assertTrue(isinstance(_val, int))
        self.assertEqual(_val, self._params.get_value("param_bool"))

    def test_q_settings_get_value__with_Real(self):
        obj = PydidasQsettingsMixin(version="unittesting")
        _val = obj.q_settings_get("param_float", dtype=Real)
        self.assertTrue(isinstance(_val, float))
        self.assertEqual(_val, self._params.get_value("param_float"))

    def test_q_settings_set(self):
        _val = 42.1235
        obj = PydidasQsettingsMixin(version="unittesting")
        obj.q_settings_set("param_float", _val)
        _new_val = float(obj.q_settings.value(f"{VERSION}/param_float"))
        self.assertEqual(_val, _new_val)

    def test_q_settings_pickle(self):
        obj = PydidasQsettingsMixin(version="unittesting")
        obj.params = self._params
        new_obj = pickle.loads(pickle.dumps(obj))
        self.assertIsInstance(new_obj, PydidasQsettingsMixin)

    def test__CopyablePydidasQSettings_copy(self):
        _qsettings = _CopyablePydidasQSettings()
        _copy = copy.copy(_qsettings)
        self.assertIsInstance(_copy, _CopyablePydidasQSettings)
        self.assertNotEqual(_qsettings, _copy)

    def test__CopyablePydidasQSettings_getstate(self):
        _qsettings = _CopyablePydidasQSettings()
        _state = _qsettings.__getstate__()
        self.assertEqual(_state["org_name"], "Hereon")
        self.assertEqual(_state["app_name"], "pydidas")

    def test__CopyablePydidasQSettings_setstate(self):
        _qsettings = _CopyablePydidasQSettings()
        _state = {"org_name": "Hereon", "app_name": "pydidas"}
        _qsettings.__setstate__(_state)
        self.assertEqual(_qsettings.organizationName(), _state["org_name"])
        self.assertEqual(_qsettings.applicationName(), _state["app_name"])

    def test__CopyablePydidasQSettings_pickle(self):
        _qsettings = _CopyablePydidasQSettings()
        _new = pickle.loads(pickle.dumps(_qsettings))
        self.assertIsInstance(_new, _CopyablePydidasQSettings)
        self.assertEqual(_qsettings.organizationName(), "Hereon")
        self.assertEqual(_qsettings.applicationName(), "pydidas")


if __name__ == "__main__":
    unittest.main()

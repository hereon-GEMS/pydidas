# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import unittest

from pydidas.core import (
    Parameter,
    ParameterCollection,
    get_generic_param_collection,
    get_generic_parameter,
)
from pydidas.core.generic_params import GENERIC_PARAMS_METADATA


class TestGetGenericParameter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        GENERIC_PARAMS_METADATA["a_dummy_test_entry"] = {
            "type": int,
            "default": 42,
            "name": "A dummy test entry",
            "choices": None,
            "range": (-5, 120),
            "allow_None": True,
        }

    @classmethod
    def tearDownClass(cls):
        del GENERIC_PARAMS_METADATA["a_dummy_test_entry"]

    def test_get_param(self):
        _p = get_generic_parameter("first_file")
        self.assertIsInstance(_p, Parameter)

    def test_get_param__wrong_key(self):
        with self.assertRaises(KeyError):
            get_generic_parameter("there_should_be_no_such_key")

    def test_get_generic_param_collection__empty(self):
        _pc = get_generic_param_collection()
        self.assertIsInstance(_pc, ParameterCollection)

    def test_get_generic_param_collection(self):
        _keys = ["first_file", "last_file"]
        _pc = get_generic_param_collection(*_keys)
        for _key in _keys:
            self.assertIn(_key, _pc)

    def test_get_generic_param_with_range(self):
        _p = get_generic_parameter("a_dummy_test_entry")
        self.assertEqual(_p.range, (-5, 120))


if __name__ == "__main__":
    unittest.main()

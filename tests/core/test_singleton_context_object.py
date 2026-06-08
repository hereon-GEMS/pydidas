# This file is part of pydidas.
#
# Copyright 2025 - 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2025 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"

import copy

import numpy as np
import pytest

from pydidas.core import ObjectWithParameterCollection, Parameter, PydidasQsettingsMixin
from pydidas.core.singleton_context import Singleton


class _NonContextClass(ObjectWithParameterCollection):
    """Testing class to test Singleton."""

    def __init__(self):
        ObjectWithParameterCollection.__init__(self)
        self.add_params(
            Parameter("test1", int, 1),
            Parameter("test2", int, 2),
        )


class _NonContextSubClass(_NonContextClass): ...


class _ContextClass(_NonContextClass, metaclass=Singleton): ...


class _SubContextClass(_ContextClass): ...


class _ContextWithSubClass(_NonContextSubClass, metaclass=Singleton): ...


_CONTEXT_CLASSES = [_ContextClass, _ContextWithSubClass, _SubContextClass]


@pytest.fixture(autouse=True)
def clear_singletons():
    """Fixture to reset singletons."""
    # Reset singleton state before each test
    Singleton._instances = {}
    yield


def test_init():
    assert _ContextClass not in Singleton._instances
    obj = _ContextClass()
    assert isinstance(obj, _ContextClass)
    assert isinstance(obj, _NonContextClass)
    assert Singleton._instances[_ContextClass] is obj


@pytest.mark.parametrize(
    "singleton_class", [_ContextClass, _ContextWithSubClass, _SubContextClass]
)
def test_init__repeated_calls(singleton_class):
    obj = singleton_class()
    obj2 = singleton_class()
    assert id(obj) == id(obj2)
    assert obj is obj2
    assert isinstance(obj, singleton_class)


def test_init__w_multiple_contexts():
    objA = _ContextClass()
    objB = _ContextWithSubClass()
    objC = _SubContextClass()
    assert id(objA) != id(objB)
    assert id(objA) != id(objC)
    assert id(objB) != id(objC)
    assert isinstance(objA, _ContextClass)
    assert isinstance(objB, _ContextWithSubClass)
    assert isinstance(objC, _SubContextClass)
    assert Singleton._instances[_ContextClass] == objA
    assert Singleton._instances[_ContextWithSubClass] == objB
    assert Singleton._instances[_SubContextClass] == objC


def test_init__w_incompatible_non_context_class():
    with pytest.raises(TypeError):

        class IncompatibleClass(PydidasQsettingsMixin, metaclass=Singleton): ...


@pytest.mark.parametrize("singleton_class", _CONTEXT_CLASSES)
def test_copy(singleton_class):
    obj = singleton_class()
    obj._config["test_key"] = 42
    obj._config["is_false"] = False
    obj.add_param(Parameter("test3", int, 21))
    obj_copy = obj.copy()
    assert id(obj) != id(obj_copy)
    assert isinstance(obj_copy, _NonContextClass)
    for _context_class in _CONTEXT_CLASSES:
        assert not isinstance(obj_copy, _context_class)
    assert obj_copy.get_param_value("test3") == obj.get_param_value("test3")
    assert obj_copy.get_param("test3") is not obj.get_param("test3")
    for _key, _val in obj._config.items():
        assert obj_copy._config[_key] == _val


@pytest.mark.parametrize("singleton_class", _CONTEXT_CLASSES)
def test_copy__w_ndarray(singleton_class):
    obj = singleton_class()
    _ref_w_obj = np.array([[1, 2, 3], [2, 3]], dtype=object)
    _ref = np.array([1, 2, 3])
    obj._config["obj_arr"] = copy.deepcopy(_ref_w_obj)
    obj._config["arr"] = copy.copy(_ref)
    copyA = obj.copy()
    copyB = copy.copy(obj)
    deepcopyA = obj.deepcopy()
    deepcopyB = copy.deepcopy(obj)
    for _item in [copyA, deepcopyA, copyB, deepcopyB]:
        assert id(obj) != id(_item)
        assert isinstance(_item, _NonContextClass)
        assert not isinstance(_item, singleton_class)
    obj._config["obj_arr"][0][0] = 42
    obj._config["arr"][0] = 7
    for _item in [copyA, copyB]:
        assert id(obj._config["arr"]) == id(_item._config["arr"])
        assert np.allclose(obj._config["arr"], _item._config["arr"])
    for _item in [deepcopyA, deepcopyB]:
        assert id(obj._config["arr"]) != id(_item._config["arr"])
        assert not np.allclose(obj._config["arr"], _item._config["arr"])
    assert copyA._config["obj_arr"][0][0] == 42
    assert copyB._config["obj_arr"][0][0] == 42
    assert deepcopyA._config["obj_arr"][0][0] == 1
    assert deepcopyB._config["obj_arr"][0][0] == 1


if __name__ == "__main__":
    pytest.main([__file__])

# This file is part of pydidas.
#
# Copyright 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"

import copy
from typing import Any

import numpy as np
import pytest

from pydidas.core import Parameter, PydidasQsettingsMixin
from pydidas.core.parameter_collection import ParameterCollection
from pydidas.core.singleton import Singleton


class _NonContextClass:
    """Testing class to test Singleton."""

    def __init__(self):
        self._config: dict[str, Any] = {"valueA": 1}
        self.is_copy: bool = False
        self.valueA: int = 1


class _NonContextSubClass(_NonContextClass): ...


class _NonContextClassWithCustomCopy(_NonContextClass):
    """Testing class to test Singleton."""

    def copy(self) -> "_NonContextClassWithCustomCopy":
        return self.__copy__()

    def deepcopy(self) -> "_NonContextClassWithCustomCopy":
        memo = {}
        return self.__deepcopy__(memo)

    def __copy__(self) -> "_NonContextClassWithCustomCopy":
        _copy = self.__class__()
        _copy._config = copy.copy(self._config)
        _copy.valueA = copy.copy(self.valueA)
        _copy.is_copy = True
        return _copy

    def __deepcopy__(self, memo) -> "_NonContextClassWithCustomCopy":
        _copy = self.__class__()
        _copy._config = copy.deepcopy(self._config)
        _copy.valueA = copy.deepcopy(self.valueA)
        _copy.is_copy = True
        return _copy


class _NonContextClassFromDict(ParameterCollection):
    """Testing class to test Singleton."""

    def __init__(self):
        ParameterCollection.__init__(self)
        self.add_params(
            Parameter("test1", int, 1),
            Parameter("test2", int, 2),
        )
        self._config: dict[str, Any] = {}


class _ContextClass(_NonContextClass, metaclass=Singleton): ...


class _ContextWithSubClass(_NonContextSubClass, metaclass=Singleton): ...


class _ContextClassWithCustomCopy(
    _NonContextClassWithCustomCopy, metaclass=Singleton
): ...


class _ContextClassFromDict(_NonContextClassFromDict, metaclass=Singleton): ...


class _SubContextClass(_ContextClass): ...


_CONTEXT_CLASSES = [
    _ContextClass,
    _ContextWithSubClass,
    _SubContextClass,
    _ContextClassWithCustomCopy,
    _ContextClassFromDict,
]


@pytest.fixture(autouse=True)
def clear_singletons():
    """Fixture to reset singletons."""
    # Reset singleton state before each test
    _stored_instances = Singleton._instances
    Singleton._instances = {}
    yield
    Singleton._instances = _stored_instances


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


def test_init__w_class_without_params():
    class OtherClass(PydidasQsettingsMixin, metaclass=Singleton): ...

    assert getattr(OtherClass, "params", None) is None
    assert getattr(OtherClass, "_config", None) is None


@pytest.mark.parametrize("singleton_class", _CONTEXT_CLASSES)
def test_reset_instance__basic(singleton_class):
    """Test that reset_instance removes only the stored singleton instance."""
    _ = [_cls() for _cls in _CONTEXT_CLASSES]
    assert singleton_class in Singleton._instances
    singleton_class.reset_instance()
    for _cls in _CONTEXT_CLASSES:
        if _cls is singleton_class:
            assert _cls not in Singleton._instances
        else:
            assert _cls in Singleton._instances


@pytest.mark.parametrize("singleton_class", _CONTEXT_CLASSES)
def test_reset_instance__creates_new_instance(singleton_class):
    """Test that after reset, a new instance is created on next call."""
    obj1 = singleton_class()
    obj1_id = id(obj1)
    singleton_class.reset_instance()
    obj2 = singleton_class()
    obj2_id = id(obj2)
    assert obj1_id != obj2_id
    assert obj1 is not obj2


@pytest.mark.parametrize("singleton_class", _CONTEXT_CLASSES)
def test_reset_instance__multiple_resets(singleton_class):
    """Test that reset_instance can be called multiple times safely."""
    obj1 = singleton_class()
    singleton_class.reset_instance()
    obj2 = singleton_class()
    singleton_class.reset_instance()
    obj3 = singleton_class()
    singleton_class.reset_instance()
    assert id(obj1) != id(obj2)
    assert id(obj2) != id(obj3)
    assert id(obj1) != id(obj3)


def test_reset_instance__preserves_state_until_call():
    """Test that resetting instance doesn't affect existing references."""
    obj1 = _ContextClass()
    obj1.valueA = 42
    original_value = obj1.valueA
    _ContextClass.reset_instance()
    obj2 = _ContextClass()
    assert obj1.valueA == original_value
    assert obj2.valueA == 1  # default value


@pytest.mark.parametrize("singleton_class", _CONTEXT_CLASSES)
def test_reset_instance__on_empty_stack(singleton_class):
    """Test that reset_instance silently succeeds even if no instance exists."""
    assert singleton_class not in Singleton._instances
    singleton_class.reset_instance()
    assert singleton_class not in Singleton._instances


@pytest.mark.parametrize("singleton_class", _CONTEXT_CLASSES)
@pytest.mark.parametrize("use_copy_module", [True, False])
def test_copy(singleton_class, use_copy_module):
    if not hasattr(singleton_class, "copy") and not use_copy_module:
        pytest.skip("Skipping copy test with invalid configuration")
    obj = singleton_class()
    obj._config["test_key"] = 42
    obj._config["is_false"] = False
    obj.valueA = 11
    if use_copy_module:
        obj_copy = copy.copy(obj)
    else:
        obj_copy = obj.copy()
    assert id(obj) != id(obj_copy)
    assert isinstance(obj_copy, Singleton.get_base_class(singleton_class))
    for _context_class in _CONTEXT_CLASSES:
        assert not isinstance(obj_copy, _context_class)
    assert obj_copy.valueA == (
        obj.valueA
        if singleton_class in [_ContextClassWithCustomCopy, _ContextClassFromDict]
        else 1
    )
    assert obj_copy._config is not obj._config
    for _key, _val in obj._config.items():
        assert obj_copy._config[_key] == _val


@pytest.mark.parametrize("singleton_class", _CONTEXT_CLASSES)
def test_copy__w_ndarray(singleton_class):
    obj = singleton_class()
    _ref_w_obj = np.array([[1, 2, 3], [2, 3]], dtype=object)
    _ref = np.array([1, 2, 3])
    obj._config["obj_arr"] = copy.deepcopy(_ref_w_obj)
    obj._config["arr"] = copy.copy(_ref)
    _copy = copy.copy(obj)
    _deepcopy = copy.deepcopy(obj)
    for _item in [_copy, _deepcopy]:
        assert id(obj) != id(_item)
        assert isinstance(_item, Singleton.get_base_class(singleton_class))
        assert not isinstance(_item, singleton_class)
    obj._config["obj_arr"][0][0] = 42
    obj._config["arr"][0] = 7
    assert id(obj._config["arr"]) == id(_copy._config["arr"])
    assert np.allclose(obj._config["arr"], _copy._config["arr"])
    assert id(obj._config["arr"]) != id(_deepcopy._config["arr"])
    assert not np.allclose(obj._config["arr"], _deepcopy._config["arr"])
    assert _copy._config["obj_arr"][0][0] == 42
    assert _deepcopy._config["obj_arr"][0][0] == 1


if __name__ == "__main__":
    pytest.main([__file__])

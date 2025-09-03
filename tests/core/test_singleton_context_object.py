# This file is part of pydidas.
#
# Copyright 2025, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import pytest

from pydidas.core import ObjectWithParameterCollection, Parameter, PydidasQsettingsMixin
from pydidas.core.singleton_context_object import SingletonContextObject


class ImplementedNonContextClass(ObjectWithParameterCollection):
    """Testing class to test SingletonContextObject."""

    def __init__(self):
        ObjectWithParameterCollection.__init__(self)
        self.add_params(
            Parameter("test1", int, 1),
            Parameter("test2", int, 2),
        )


class ImplementedClass(SingletonContextObject, ImplementedNonContextClass):
    non_context_class = ImplementedNonContextClass


class SubClass(ImplementedClass):
    pass


@pytest.fixture
def singleton_class():
    """Fixture to create a SingletonContextObject instance."""
    ImplementedClass._instance = None
    ImplementedClass._initialized = False
    yield ImplementedClass


@pytest.fixture
def singleton_subclass():
    SubClass._instance = None
    SubClass._initialized = False
    yield SubClass


def test_init(singleton_class):
    assert singleton_class._instance is None
    assert not singleton_class._initialized
    obj = singleton_class()
    assert isinstance(obj, SingletonContextObject)
    assert singleton_class._instance is obj
    assert singleton_class._initialized


def test_init__repeated_calls(singleton_class):
    obj = singleton_class()
    obj2 = singleton_class()
    assert isinstance(obj, SingletonContextObject)
    assert id(obj) == id(obj2)
    assert obj is obj2


def test_init__w_modified_non_context_class(singleton_subclass):
    obj = singleton_subclass()
    assert isinstance(obj, singleton_subclass)
    assert isinstance(obj, SubClass)
    assert obj.get_param_value("test1") == 1
    assert obj.get_param_value("test2") == 2


def test_init__w_incompatible_non_context_class():
    class IncompatibleClass(SingletonContextObject, PydidasQsettingsMixin):
        non_context_class = PydidasQsettingsMixin

    with pytest.raises(TypeError):
        _ = IncompatibleClass()


def test_copy(singleton_class):
    obj = singleton_class()
    obj._config["test_key"] = 42
    obj._config["is_false"] = False
    obj.add_param(Parameter("test3", int, 21))
    obj_copy = obj.copy()
    assert id(obj) != id(obj_copy)
    assert isinstance(obj_copy, singleton_class.non_context_class)
    assert not isinstance(obj_copy, singleton_class)
    assert obj_copy.get_param_value("test3") == obj.get_param_value("test3")
    for _key, _val in obj._config.items():
        assert obj_copy._config[_key] == _val


def test_copy__w_modified_non_context_class(singleton_subclass):
    obj = singleton_subclass()
    obj._config["test_key"] = 42
    obj._config["is_false"] = False
    obj_copy = obj.copy()
    assert id(obj) != id(obj_copy)
    assert isinstance(obj_copy, singleton_subclass.non_context_class)
    assert not isinstance(obj_copy, singleton_subclass)
    for _key, _val in obj.param_values.items():
        assert obj_copy.get_param_value(_key) == _val
    for _key, _val in obj._config.items():
        assert obj_copy._config[_key] == _val


if __name__ == "__main__":
    pytest.main()

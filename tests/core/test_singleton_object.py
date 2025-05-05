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


import copy
from typing import Any

import pytest
from qtpy import QtCore

from pydidas.core import SingletonObject


class BaseClass:
    init_called = False

    def __init__(self, *args: Any, **kwargs: Any):
        self.init_called = True
        self.args = args
        self.kwargs = kwargs


class SubClass(BaseClass):
    is_sub = True
    sub_init_called = False

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.sub_init_called = True


class DirectClass(SingletonObject):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.init_called = True
        self.args = args
        self.kwargs = kwargs


class TestClass(SingletonObject, BaseClass): ...


class TestSubClass(SingletonObject, SubClass): ...


@pytest.fixture
def singleton_class():
    TestClass._instance = None
    TestClass._initialized = False
    yield TestClass


@pytest.fixture
def singleton_subclass():
    TestSubClass._instance = None
    TestSubClass._initialized = False
    yield TestSubClass


@pytest.fixture
def direct_class():
    DirectClass._instance = None
    DirectClass._initialized = False
    yield DirectClass


@pytest.mark.parametrize(
    "test_class",
    [
        ["singleton_class", BaseClass],
        ["singleton_subclass", SubClass],
        ["direct_class", DirectClass],
    ],
)
def test_init(request, test_class):
    _singleton_class_name, _base_class = test_class
    _singleton_class = request.getfixturevalue(_singleton_class_name)
    _args = ("test", 42)
    _kwargs = {"table": 12, "spam": 2.4, "eggs": 23, "ham": None}
    assert _singleton_class._instance is None
    assert not _singleton_class._initialized
    obj = _singleton_class(*_args, **_kwargs)
    assert isinstance(obj, SingletonObject)
    assert isinstance(obj, _base_class)
    assert obj.init_called
    assert obj.args == _args
    assert obj.kwargs == _kwargs
    assert _singleton_class._instance is obj
    assert _singleton_class._initialized


def test_init__w_direct_class(direct_class):
    _args = ("test", 42)
    _kwargs = {"table": 12, "spam": 2.4, "eggs": 23, "ham": None}
    assert direct_class._instance is None
    assert not direct_class._initialized
    obj = direct_class(*_args, **_kwargs)
    assert isinstance(obj, SingletonObject)
    assert isinstance(obj, direct_class)
    assert obj.init_called
    assert obj.args == _args
    assert obj.kwargs == _kwargs
    assert direct_class._instance is obj
    assert direct_class._initialized


@pytest.mark.parametrize(
    "test_class",
    [
        ["singleton_class", BaseClass],
        ["singleton_subclass", SubClass],
        ["direct_class", DirectClass],
    ],
)
def test_init__repeated_calls(request, test_class):
    _singleton_class_name, _base_class = test_class
    _singleton_class = request.getfixturevalue(_singleton_class_name)
    obj = _singleton_class()
    obj2 = _singleton_class()
    assert isinstance(obj2, SingletonObject)
    assert isinstance(obj2, _base_class)
    assert id(obj) == id(obj2)
    assert obj is obj2


def test_init__repeated_calls__w_new_args(singleton_class):
    obj = singleton_class()
    with pytest.warns(UserWarning):
        obj2 = singleton_class("test")
    assert id(obj) == id(obj2)
    assert obj is obj2


def test_init__w_subclass(singleton_subclass):
    obj = singleton_subclass()
    assert isinstance(obj, SubClass)
    assert isinstance(obj, SingletonObject)
    assert obj.init_called
    assert obj.is_sub
    assert obj.sub_init_called


def test_init__w_qobject():
    class TestQObject(SingletonObject, QtCore.QObject): ...

    qparent = QtCore.QObject()
    obj = TestQObject(parent=qparent)
    assert isinstance(obj, SingletonObject)
    assert isinstance(obj, QtCore.QObject)
    assert obj.parent() == qparent


def test_copy(singleton_class):
    obj = singleton_class()
    with pytest.raises(TypeError):
        _ = obj.copy()


def test_copy_module(singleton_class):
    obj = singleton_class()
    with pytest.raises(TypeError):
        _ = copy.copy(obj)


def test_copy__w_subclass(singleton_subclass):
    obj = singleton_subclass()
    with pytest.raises(TypeError):
        _ = obj.copy()


if __name__ == "__main__":
    pytest.main()

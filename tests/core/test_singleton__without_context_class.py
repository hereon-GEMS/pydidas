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
#
# Parts of this file have been created using the AI-tool Claude Haiku 4.5.

"""
Unit tests for singleton patterns with direct class definitions (no explicit base).

This test module verifies that the Singleton and QtSingleton metaclasses work
correctly for classes defined directly as singletons without inheriting from
an explicit base class. These are edge cases that previously failed but now
work correctly with the updated metaclass implementation.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import copy

import pytest
from qtpy import QtWidgets

from pydidas.core import ObjectWithParameterCollection
from pydidas.core.singleton import QtSingleton, Singleton


class DirectSingletonClass(metaclass=Singleton):
    """Direct Singleton class (no explicit base)."""

    def __init__(self):
        self.value = 42
        self._config = {"key": "test"}


class DirectSingletonClassB(metaclass=Singleton):
    """Another direct Singleton class (no explicit base)."""

    def __init__(self):
        self.data = "example"
        self._config = {}


class DirectQtSingletonClass(metaclass=QtSingleton):
    """Direct QtSingleton class (no explicit base).."""

    def __init__(self):
        self.value = 99
        self._config = {"qt_key": "qt_value"}


class DirectQtSingletonClassB(metaclass=QtSingleton):
    """Another direct QtSingleton class (no explicit base).."""

    def __init__(self):
        self.data = "qt_example"
        self._config = {}


class SingletonQLineEdit(QtWidgets.QLineEdit, metaclass=QtSingleton):
    """A QLineEdit singleton derived from Qt widget."""

    def __init__(self):
        super().__init__()
        self.custom_value = "line_edit_1"
        self._config = {"widget_type": "QLineEdit"}


class SingletonQLineEditB(QtWidgets.QLineEdit, metaclass=QtSingleton):
    """Another QLineEdit singleton derived from the same Qt widget."""

    def __init__(self):
        super().__init__()
        self.custom_value = "line_edit_2"
        self._config = {"widget_type": "AnotherQLineEdit"}


class SingletonQPushButton(QtWidgets.QPushButton, metaclass=QtSingleton):
    """A QPushButton singleton derived from a different Qt widget."""

    def __init__(self):
        super().__init__()
        self.button_label = "button_1"
        self._config = {"widget_type": "QPushButton"}


class SingletonQPushButtonB(QtWidgets.QPushButton, metaclass=QtSingleton):
    """Another QPushButton singleton derived from the same Qt widget."""

    def __init__(self):
        super().__init__()
        self.button_label = "button_2"
        self._config = {"widget_type": "Spam & Ham"}


_DIRECT_SINGLETON_CLASSES: list[tuple[type, type]] = [
    (Singleton, DirectSingletonClass),
    (Singleton, DirectSingletonClassB),
    (QtSingleton, DirectQtSingletonClass),
    (QtSingleton, DirectQtSingletonClassB),
]


_QT_WIDGET_SINGLETON_CLASSES = (
    SingletonQLineEdit,
    SingletonQLineEditB,
    SingletonQPushButton,
    SingletonQPushButtonB,
)


@pytest.fixture(autouse=True)
def clear_singletons():
    """Fixture to reset singletons before each test."""
    _stored_singleton_instances = Singleton._instances
    _stored_qt_singleton_instances = QtSingleton._instances
    Singleton._instances = {}
    QtSingleton._instances = {}
    yield
    Singleton._instances = _stored_singleton_instances
    QtSingleton._instances = _stored_qt_singleton_instances


@pytest.mark.parametrize("metaclass, singleton_class", _DIRECT_SINGLETON_CLASSES)
def test__direct_singletons__init(metaclass, singleton_class):
    assert singleton_class not in metaclass._instances
    obj = singleton_class()
    assert isinstance(obj, singleton_class)
    assert singleton_class in metaclass._instances
    assert metaclass._instances[singleton_class] is obj


@pytest.mark.parametrize("metaclass, singleton_class", _DIRECT_SINGLETON_CLASSES)
def test__direct_singleton__repeated_calls(metaclass, singleton_class):
    obj = singleton_class()
    obj2 = singleton_class()
    assert id(obj) == id(obj2)
    assert obj is obj2


def test__direct_singleton__check_instance_registry():
    objects = []
    for _metaclass, _class in _DIRECT_SINGLETON_CLASSES:
        _instance = _class()
        objects.append((_metaclass, _instance))
    _ids = [id(obj) for _, obj in objects]
    assert len(set(_ids)) == len(objects)
    for _metaclass, _instance in objects:
        assert _metaclass._instances[_instance.__class__] == _instance


@pytest.mark.parametrize("metaclass, singleton_class", _DIRECT_SINGLETON_CLASSES)
def test__direct_singleton__get_base_class(metaclass, singleton_class):
    _ = singleton_class()
    base_class = metaclass.get_base_class(singleton_class)
    # This defaults to the ObjectWithParameterCollection
    assert base_class is ObjectWithParameterCollection


@pytest.mark.parametrize("metaclass, singleton_class", _DIRECT_SINGLETON_CLASSES)
def test__direct_singleton__reset_instance(metaclass, singleton_class):
    obj1 = singleton_class()
    assert singleton_class in metaclass._instances
    singleton_class.reset_instance()
    assert singleton_class not in metaclass._instances
    obj2 = singleton_class()
    assert id(obj1) != id(obj2)


@pytest.mark.parametrize("metaclass, singleton_class", _DIRECT_SINGLETON_CLASSES)
def test__direct_singleton__copy(metaclass, singleton_class):
    obj = singleton_class()
    obj._config["added_key"] = "added_value"
    obj_copy = copy.copy(obj)
    assert id(obj) != id(obj_copy)
    assert isinstance(obj_copy, ObjectWithParameterCollection)
    assert not isinstance(obj_copy, singleton_class)
    assert obj_copy._config is not obj._config
    assert obj_copy._config == obj._config
    assert obj_copy._config["added_key"] == obj._config["added_key"]


@pytest.mark.parametrize("metaclass, singleton_class", _DIRECT_SINGLETON_CLASSES)
def test__direct_singleton__deepcopy(metaclass, singleton_class):
    obj = singleton_class()
    obj._config["nested"] = {"inner": "value"}
    obj_deepcopy = copy.deepcopy(obj)
    obj._config["nested"]["inner"] = "modified"
    assert id(obj) != id(obj_deepcopy)
    assert isinstance(obj_deepcopy, ObjectWithParameterCollection)
    assert not isinstance(obj_deepcopy, singleton_class)
    assert obj_deepcopy._config is not obj._config
    assert obj_deepcopy._config["nested"]["inner"] == "value"


def test__editing_copy_does_not_affect_singleton():
    obj = DirectSingletonClass()
    original_id = id(obj)
    obj_copy = copy.copy(obj)
    obj_copy.value = 999
    obj_copy._config["new_key"] = "new_value"
    assert id(obj) == original_id
    assert obj.value == 42
    assert "new_key" not in obj._config


@pytest.mark.parametrize("singleton_class", _QT_WIDGET_SINGLETON_CLASSES)
def test__qwidget_singleton___init(singleton_class):
    assert singleton_class not in QtSingleton._instances
    obj = singleton_class()
    assert isinstance(obj, singleton_class)
    assert isinstance(obj, (QtWidgets.QPushButton, QtWidgets.QLineEdit))
    assert singleton_class in QtSingleton._instances
    assert QtSingleton._instances[singleton_class] is obj


@pytest.mark.parametrize("singleton_class", _QT_WIDGET_SINGLETON_CLASSES)
def test__qwidget_singleton__repeated_calls(singleton_class):
    obj = singleton_class()
    obj2 = singleton_class()
    assert id(obj) == id(obj2)
    assert obj is obj2


def test__qwidget_singleton__multiple_widgets_are_separate():
    objects = []
    for _class in _QT_WIDGET_SINGLETON_CLASSES:
        _instance = _class()
        objects.append(_instance)
    _ids = [id(obj) for obj in objects]
    assert len(set(_ids)) == len(objects)
    for _obj in objects:
        assert QtSingleton._instances[_obj.__class__] is _obj
        if isinstance(_obj, SingletonQLineEdit):
            assert _obj.custom_value == "line_edit_1"
        elif isinstance(_obj, SingletonQLineEditB):
            assert _obj.custom_value == "line_edit_2"
        elif isinstance(_obj, SingletonQPushButton):
            assert _obj.button_label == "button_1"
        elif isinstance(_obj, SingletonQPushButtonB):
            assert _obj.button_label == "button_2"


@pytest.mark.parametrize("singleton_class", _QT_WIDGET_SINGLETON_CLASSES)
def test__qwidget_singleton__reset_instance(singleton_class):
    obj1 = singleton_class()
    assert singleton_class in QtSingleton._instances
    singleton_class.reset_instance()
    assert singleton_class not in QtSingleton._instances
    obj2 = singleton_class()
    assert id(obj1) != id(obj2)


@pytest.mark.parametrize("singleton_class", _QT_WIDGET_SINGLETON_CLASSES)
def test__qwidget_singleton__copy(singleton_class):
    obj = singleton_class()
    obj_copy = copy.copy(obj)
    assert id(obj) != id(obj_copy)
    assert not isinstance(obj_copy, singleton_class)
    assert isinstance(obj_copy, (QtWidgets.QPushButton, QtWidgets.QLineEdit))


@pytest.mark.parametrize("singleton_class", _QT_WIDGET_SINGLETON_CLASSES)
def test__qwidget_singleton__deepcopy(singleton_class):
    obj = singleton_class()
    obj_deepcopy = copy.deepcopy(obj)
    assert id(obj) != id(obj_deepcopy)
    # Deepcopy should create an instance of the Qt widget lib class
    assert isinstance(obj_deepcopy, (QtWidgets.QPushButton, QtWidgets.QLineEdit))


@pytest.mark.parametrize("singleton_class", _QT_WIDGET_SINGLETON_CLASSES)
def test__qwidget_singleton__get_base_class(singleton_class):
    _instance = singleton_class()
    _base_class = QtSingleton.get_base_class(_instance.__class__)
    if QtWidgets.QLineEdit in _instance.__class__.__bases__:
        assert _base_class is QtWidgets.QLineEdit
    elif QtWidgets.QPushButton in _instance.__class__.__bases__:
        assert _base_class is QtWidgets.QPushButton


if __name__ == "__main__":
    pytest.main([__file__])

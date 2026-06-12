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

from pydidas.core.singleton import QtSingleton, Singleton


# Direct Singleton classes (no explicit base)
class DirectSingletonClass(metaclass=Singleton):
    """A singleton class defined directly without explicit base class."""

    def __init__(self):
        self.value = 42
        self._config = {"key": "test"}


class AnotherDirectSingletonClass(metaclass=Singleton):
    """Another singleton class defined directly without explicit base class."""

    def __init__(self):
        self.data = "example"
        self._config = {}


# Direct QtSingleton classes (no explicit base)
class DirectQtSingletonClass(metaclass=QtSingleton):
    """A Qt singleton class defined directly without explicit base class."""

    def __init__(self):
        self.value = 99
        self._config = {"qt_key": "qt_value"}


class AnotherDirectQtSingletonClass(metaclass=QtSingleton):
    """Another Qt singleton class defined directly without explicit base class."""

    def __init__(self):
        self.data = "qt_example"
        self._config = {}


# Qt widget derived classes with QtSingleton
class SingletonQLineEdit(QtWidgets.QLineEdit, metaclass=QtSingleton):
    """A QLineEdit singleton derived from Qt widget."""

    def __init__(self):
        super().__init__()
        self.custom_value = "line_edit_1"
        self._config = {"widget_type": "QLineEdit"}


class AnotherSingletonQLineEdit(QtWidgets.QLineEdit, metaclass=QtSingleton):
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


class AnotherSingletonQPushButton(QtWidgets.QPushButton, metaclass=QtSingleton):
    """Another QPushButton singleton derived from the same Qt widget."""

    def __init__(self):
        super().__init__()
        self.button_label = "button_2"
        self._config = {"widget_type": "AnotherQPushButton"}


_DIRECT_SINGLETON_CLASSES = [
    DirectSingletonClass,
    AnotherDirectSingletonClass,
]

_DIRECT_QT_SINGLETON_CLASSES = [
    DirectQtSingletonClass,
    AnotherDirectQtSingletonClass,
]

_QT_WIDGET_SINGLETON_CLASSES_QLINEEDIT = [
    SingletonQLineEdit,
    AnotherSingletonQLineEdit,
]

_QT_WIDGET_SINGLETON_CLASSES_QPUSHBUTTON = [
    SingletonQPushButton,
    AnotherSingletonQPushButton,
]

_ALL_QT_WIDGET_SINGLETON_CLASSES = (
    _QT_WIDGET_SINGLETON_CLASSES_QLINEEDIT
    + _QT_WIDGET_SINGLETON_CLASSES_QPUSHBUTTON
)


@pytest.fixture(autouse=True)
def clear_singletons():
    """Fixture to reset singletons before each test."""
    # Store original instances
    _stored_singleton_instances = Singleton._instances
    _stored_qt_singleton_instances = QtSingleton._instances
    Singleton._instances = {}
    QtSingleton._instances = {}
    yield
    # Restore original instances
    Singleton._instances = _stored_singleton_instances
    QtSingleton._instances = _stored_qt_singleton_instances


class TestDirectSingletonDefinition:
    """Tests for Singleton metaclass with direct class definitions."""

    @pytest.mark.parametrize("singleton_class", _DIRECT_SINGLETON_CLASSES)
    def test_init(self, singleton_class):
        """Test that direct singleton can be instantiated."""
        assert singleton_class not in Singleton._instances
        obj = singleton_class()
        assert isinstance(obj, singleton_class)
        assert singleton_class in Singleton._instances
        assert Singleton._instances[singleton_class] is obj

    @pytest.mark.parametrize("singleton_class", _DIRECT_SINGLETON_CLASSES)
    def test_init__repeated_calls(self, singleton_class):
        """Test that repeated calls return the same instance."""
        obj = singleton_class()
        obj2 = singleton_class()
        assert id(obj) == id(obj2)
        assert obj is obj2

    def test_init__multiple_singletons(self):
        """Test that different singleton classes have different instances."""
        objA = DirectSingletonClass()
        objB = AnotherDirectSingletonClass()
        assert id(objA) != id(objB)
        assert isinstance(objA, DirectSingletonClass)
        assert isinstance(objB, AnotherDirectSingletonClass)
        assert Singleton._instances[DirectSingletonClass] == objA
        assert Singleton._instances[AnotherDirectSingletonClass] == objB

    @pytest.mark.parametrize("singleton_class", _DIRECT_SINGLETON_CLASSES)
    def test_get_base_class(self, singleton_class):
        """Test that get_base_class returns ObjectWithParameterCollection."""
        _ = singleton_class()
        base_class = Singleton.get_base_class(singleton_class)
        # The base class should be ObjectWithParameterCollection for direct singletons
        from pydidas.core.object_with_parameter_collection import (
            ObjectWithParameterCollection,
        )

        assert base_class is ObjectWithParameterCollection

    @pytest.mark.parametrize("singleton_class", _DIRECT_SINGLETON_CLASSES)
    def test_reset_instance(self, singleton_class):
        """Test that reset_instance removes the singleton."""
        obj1 = singleton_class()
        assert singleton_class in Singleton._instances
        singleton_class.reset_instance()
        assert singleton_class not in Singleton._instances
        obj2 = singleton_class()
        assert id(obj1) != id(obj2)

    @pytest.mark.parametrize("singleton_class", _DIRECT_SINGLETON_CLASSES)
    def test_copy(self, singleton_class):
        """Test that copy creates a non-singleton instance."""
        obj = singleton_class()
        obj_copy = copy.copy(obj)
        assert id(obj) != id(obj_copy)
        from pydidas.core.object_with_parameter_collection import (
            ObjectWithParameterCollection,
        )

        assert isinstance(obj_copy, ObjectWithParameterCollection)
        assert not isinstance(obj_copy, singleton_class)

    @pytest.mark.parametrize("singleton_class", _DIRECT_SINGLETON_CLASSES)
    def test_deepcopy(self, singleton_class):
        """Test that deepcopy creates a non-singleton instance."""
        obj = singleton_class()
        obj_deepcopy = copy.deepcopy(obj)
        assert id(obj) != id(obj_deepcopy)
        from pydidas.core.object_with_parameter_collection import (
            ObjectWithParameterCollection,
        )

        assert isinstance(obj_deepcopy, ObjectWithParameterCollection)
        assert not isinstance(obj_deepcopy, singleton_class)

    def test_copy_preserves_config(self):
        """Test that copy preserves _config."""
        obj = DirectSingletonClass()
        obj._config["added_key"] = "added_value"
        obj_copy = copy.copy(obj)
        assert obj_copy._config is not obj._config
        assert obj_copy._config["key"] == obj._config["key"]
        assert obj_copy._config["added_key"] == obj._config["added_key"]

    def test_deepcopy_preserves_config(self):
        """Test that deepcopy preserves _config with deep copy."""
        obj = DirectSingletonClass()
        obj._config["nested"] = {"inner": "value"}
        obj_deepcopy = copy.deepcopy(obj)
        assert obj_deepcopy._config is not obj._config
        assert obj_deepcopy._config == obj._config
        # Verify it's a deep copy
        obj._config["nested"]["inner"] = "modified"
        assert obj_deepcopy._config["nested"]["inner"] == "value"


class TestDirectQtSingletonDefinition:
    """Tests for QtSingleton metaclass with direct class definitions."""

    @pytest.mark.parametrize("singleton_class", _DIRECT_QT_SINGLETON_CLASSES)
    def test_init(self, singleton_class):
        """Test that direct Qt singleton can be instantiated."""
        assert singleton_class not in QtSingleton._instances
        obj = singleton_class()
        assert isinstance(obj, singleton_class)
        assert singleton_class in QtSingleton._instances
        assert QtSingleton._instances[singleton_class] is obj

    @pytest.mark.parametrize("singleton_class", _DIRECT_QT_SINGLETON_CLASSES)
    def test_init__repeated_calls(self, singleton_class):
        """Test that repeated calls return the same instance."""
        obj = singleton_class()
        obj2 = singleton_class()
        assert id(obj) == id(obj2)
        assert obj is obj2

    def test_init__multiple_singletons(self):
        """Test that different Qt singleton classes have different instances."""
        objA = DirectQtSingletonClass()
        objB = AnotherDirectQtSingletonClass()
        assert id(objA) != id(objB)
        assert isinstance(objA, DirectQtSingletonClass)
        assert isinstance(objB, AnotherDirectQtSingletonClass)
        assert QtSingleton._instances[DirectQtSingletonClass] == objA
        assert QtSingleton._instances[AnotherDirectQtSingletonClass] == objB

    @pytest.mark.parametrize("singleton_class", _DIRECT_QT_SINGLETON_CLASSES)
    def test_get_base_class(self, singleton_class):
        """Test that get_base_class returns ObjectWithParameterCollection."""
        _ = singleton_class()
        base_class = QtSingleton.get_base_class(singleton_class)
        from pydidas.core.object_with_parameter_collection import (
            ObjectWithParameterCollection,
        )

        assert base_class is ObjectWithParameterCollection

    @pytest.mark.parametrize("singleton_class", _DIRECT_QT_SINGLETON_CLASSES)
    def test_reset_instance(self, singleton_class):
        """Test that reset_instance removes the Qt singleton."""
        obj1 = singleton_class()
        assert singleton_class in QtSingleton._instances
        singleton_class.reset_instance()
        assert singleton_class not in QtSingleton._instances
        obj2 = singleton_class()
        assert id(obj1) != id(obj2)

    @pytest.mark.parametrize("singleton_class", _DIRECT_QT_SINGLETON_CLASSES)
    def test_copy(self, singleton_class):
        """Test that copy creates a non-singleton instance."""
        obj = singleton_class()
        obj_copy = copy.copy(obj)
        assert id(obj) != id(obj_copy)
        from pydidas.core.object_with_parameter_collection import (
            ObjectWithParameterCollection,
        )

        assert isinstance(obj_copy, ObjectWithParameterCollection)
        assert not isinstance(obj_copy, singleton_class)

    @pytest.mark.parametrize("singleton_class", _DIRECT_QT_SINGLETON_CLASSES)
    def test_deepcopy(self, singleton_class):
        """Test that deepcopy creates a non-singleton instance."""
        obj = singleton_class()
        obj_deepcopy = copy.deepcopy(obj)
        assert id(obj) != id(obj_deepcopy)
        from pydidas.core.object_with_parameter_collection import (
            ObjectWithParameterCollection,
        )

        assert isinstance(obj_deepcopy, ObjectWithParameterCollection)
        assert not isinstance(obj_deepcopy, singleton_class)

    def test_copy_preserves_config(self):
        """Test that copy preserves _config."""
        obj = DirectQtSingletonClass()
        obj._config["added_key"] = "added_value"
        obj_copy = copy.copy(obj)
        assert obj_copy._config is not obj._config
        assert obj_copy._config["qt_key"] == obj._config["qt_key"]
        assert obj_copy._config["added_key"] == obj._config["added_key"]

    def test_deepcopy_preserves_config(self):
        """Test that deepcopy preserves _config with deep copy."""
        obj = DirectQtSingletonClass()
        obj._config["nested"] = {"inner": "qt_value"}
        obj_deepcopy = copy.deepcopy(obj)
        assert obj_deepcopy._config is not obj._config
        assert obj_deepcopy._config == obj._config
        # Verify it's a deep copy
        obj._config["nested"]["inner"] = "modified"
        assert obj_deepcopy._config["nested"]["inner"] == "qt_value"


class TestMixedSingletonDefinitions:
    """Tests mixing different singleton types."""

    def test_direct_and_context_singletons_coexist(self):
        """Test that direct singletons and context singletons work together."""
        # Create a direct singleton
        direct_obj = DirectSingletonClass()
        # Create a context singleton with a base class
        class ContextBasedClass:
            def __init__(self):
                self.value = 100
                self._config = {}

        class ContextSingleton(ContextBasedClass, metaclass=Singleton):
            pass

        context_obj = ContextSingleton()
        assert id(direct_obj) != id(context_obj)
        assert isinstance(direct_obj, DirectSingletonClass)
        assert isinstance(context_obj, ContextSingleton)

    def test_copy_does_not_affect_singleton(self):
        """Test that copying a singleton instance doesn't affect the original."""
        obj = DirectSingletonClass()
        original_id = id(obj)
        obj_copy = copy.copy(obj)
        obj_copy.value = 999
        obj_copy._config["new_key"] = "new_value"
        assert id(obj) == original_id
        assert obj.value == 42
        assert "new_key" not in obj._config


class TestQtWidgetDerivedSingleton:
    """Tests for QtSingleton with Qt widget base classes."""

    @pytest.mark.parametrize("singleton_class", _QT_WIDGET_SINGLETON_CLASSES_QLINEEDIT)
    def test_qlineedit_init(self, singleton_class):
        """Test that QLineEdit singleton can be instantiated."""
        assert singleton_class not in QtSingleton._instances
        obj = singleton_class()
        assert isinstance(obj, singleton_class)
        assert isinstance(obj, QtWidgets.QLineEdit)
        assert singleton_class in QtSingleton._instances
        assert QtSingleton._instances[singleton_class] is obj

    @pytest.mark.parametrize("singleton_class", _QT_WIDGET_SINGLETON_CLASSES_QLINEEDIT)
    def test_qlineedit_repeated_calls(self, singleton_class):
        """Test that repeated calls return the same QLineEdit instance."""
        obj = singleton_class()
        obj2 = singleton_class()
        assert id(obj) == id(obj2)
        assert obj is obj2

    @pytest.mark.parametrize("singleton_class", _QT_WIDGET_SINGLETON_CLASSES_QPUSHBUTTON)
    def test_qpushbutton_init(self, singleton_class):
        """Test that QPushButton singleton can be instantiated."""
        assert singleton_class not in QtSingleton._instances
        obj = singleton_class()
        assert isinstance(obj, singleton_class)
        assert isinstance(obj, QtWidgets.QPushButton)
        assert singleton_class in QtSingleton._instances
        assert QtSingleton._instances[singleton_class] is obj

    @pytest.mark.parametrize("singleton_class", _QT_WIDGET_SINGLETON_CLASSES_QPUSHBUTTON)
    def test_qpushbutton_repeated_calls(self, singleton_class):
        """Test that repeated calls return the same QPushButton instance."""
        obj = singleton_class()
        obj2 = singleton_class()
        assert id(obj) == id(obj2)
        assert obj is obj2

    def test_multiple_qlineedit_singletons_are_separate(self):
        """Test that different QLineEdit singletons are separate instances."""
        obj1 = SingletonQLineEdit()
        obj2 = AnotherSingletonQLineEdit()
        assert id(obj1) != id(obj2)
        assert obj1.custom_value == "line_edit_1"
        assert obj2.custom_value == "line_edit_2"
        assert isinstance(obj1, SingletonQLineEdit)
        assert isinstance(obj2, AnotherSingletonQLineEdit)

    def test_multiple_qpushbutton_singletons_are_separate(self):
        """Test that different QPushButton singletons are separate instances."""
        obj1 = SingletonQPushButton()
        obj2 = AnotherSingletonQPushButton()
        assert id(obj1) != id(obj2)
        assert obj1.button_label == "button_1"
        assert obj2.button_label == "button_2"
        assert isinstance(obj1, SingletonQPushButton)
        assert isinstance(obj2, AnotherSingletonQPushButton)

    def test_different_widget_types_are_separate(self):
        """Test that QLineEdit and QPushButton singletons are separate."""
        line_edit = SingletonQLineEdit()
        push_button = SingletonQPushButton()
        assert id(line_edit) != id(push_button)
        assert isinstance(line_edit, QtWidgets.QLineEdit)
        assert isinstance(push_button, QtWidgets.QPushButton)

    @pytest.mark.parametrize("singleton_class", _ALL_QT_WIDGET_SINGLETON_CLASSES)
    def test_qt_widget_reset_instance(self, singleton_class):
        """Test that reset_instance removes the Qt widget singleton."""
        obj1 = singleton_class()
        assert singleton_class in QtSingleton._instances
        singleton_class.reset_instance()
        assert singleton_class not in QtSingleton._instances
        obj2 = singleton_class()
        assert id(obj1) != id(obj2)

    @pytest.mark.parametrize("singleton_class", _ALL_QT_WIDGET_SINGLETON_CLASSES)
    def test_qt_widget_copy(self, singleton_class):
        """Test that copy creates a non-singleton instance for Qt widgets."""
        obj = singleton_class()
        obj_copy = copy.copy(obj)
        assert id(obj) != id(obj_copy)
        # Copy should create an instance of the Qt widget lib class
        assert not isinstance(obj_copy, singleton_class)

    @pytest.mark.parametrize("singleton_class", _ALL_QT_WIDGET_SINGLETON_CLASSES)
    def test_qt_widget_deepcopy(self, singleton_class):
        """Test that deepcopy creates a non-singleton instance for Qt widgets."""
        obj = singleton_class()
        obj_deepcopy = copy.deepcopy(obj)
        assert id(obj) != id(obj_deepcopy)
        # Deepcopy should create an instance of the Qt widget lib class
        assert not isinstance(obj_deepcopy, singleton_class)

    def test_qlineedit_singleton_config_preserved(self):
        """Test that QLineEdit singleton config is preserved on copy."""
        obj = SingletonQLineEdit()
        obj._config["custom"] = "value"
        obj_copy = copy.copy(obj)
        assert obj_copy._config["widget_type"] == obj._config["widget_type"]
        assert obj_copy._config["custom"] == obj._config["custom"]
        assert obj_copy._config is not obj._config

    def test_qpushbutton_singleton_config_preserved(self):
        """Test that QPushButton singleton config is preserved on copy."""
        obj = SingletonQPushButton()
        obj._config["custom"] = "button_value"
        obj_copy = copy.copy(obj)
        assert obj_copy._config["widget_type"] == obj._config["widget_type"]
        assert obj_copy._config["custom"] == obj._config["custom"]
        assert obj_copy._config is not obj._config

    def test_qlineedit_get_base_class(self):
        """Test that get_base_class returns correct base for QLineEdit singleton."""
        _ = SingletonQLineEdit()
        base_class = QtSingleton.get_base_class(SingletonQLineEdit)
        # The base class should be QLineEdit since it's the direct parent
        assert base_class is QtWidgets.QLineEdit

    def test_qpushbutton_get_base_class(self):
        """Test that get_base_class returns correct base for QPushButton singleton."""
        _ = SingletonQPushButton()
        base_class = QtSingleton.get_base_class(SingletonQPushButton)
        # The base class should be QPushButton since it's the direct parent
        assert base_class is QtWidgets.QPushButton

    def test_qt_widget_singleton_isolation(self):
        """Test that modifications to one Qt singleton don't affect others."""
        obj1 = SingletonQLineEdit()
        obj2 = AnotherSingletonQLineEdit()
        original_value_1 = obj1.custom_value
        original_value_2 = obj2.custom_value
        obj1.custom_value = "modified_1"
        obj2.custom_value = "modified_2"
        assert obj1.custom_value == "modified_1"
        assert obj2.custom_value == "modified_2"


if __name__ == "__main__":
    pytest.main([__file__])








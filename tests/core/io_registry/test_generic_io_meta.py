# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import pytest

from pydidas.core import UserConfigError
from pydidas.core.io_registry import GenericIoMeta


@pytest.fixture(autouse=True)
def clear_registry():
    GenericIoMeta.clear_registry()
    yield
    GenericIoMeta.clear_registry()


@pytest.fixture
def test_class():
    class TestClass(metaclass=GenericIoMeta):
        extensions = [".dummy", ".test"]
        format_name = "TEST"

    return TestClass()


@pytest.fixture
def test_class2():
    class TestClass2(metaclass=GenericIoMeta):
        extensions = [".test2"]
        format_name = "Test2"

    return TestClass2()


@pytest.fixture
def get_unregistered_test_class():
    class TestClass3:
        extensions = [".test3", ".test4"]
        format_name = "Test3"

    return TestClass3


def test_empty():
    assert GenericIoMeta.registry == {}


def test_get_registered_formats__empty():
    assert GenericIoMeta.get_registered_formats() == {}


def test_get_registered_formats__with_entry(test_class):
    _formats = GenericIoMeta.get_registered_formats()
    _target = {test_class.format_name: test_class.extensions}
    assert _formats == _target


def test_get_string_of_formats(test_class):
    _str = GenericIoMeta.get_string_of_formats()
    _target = "All supported files (*.dummy *.test);;TEST (*.dummy *.test)"
    assert _str == _target


def test_get_string_of_formats__no_files_registered():
    _str = GenericIoMeta.get_string_of_formats()
    _target = "All supported files ()"
    assert _str == _target


def test_is_extension_registered__True(test_class):
    assert GenericIoMeta.is_extension_registered(".dummy") is True


def test_is_extension_registered__False(test_class):
    assert GenericIoMeta.is_extension_registered(".none") is False


def test_verify_extension_is_registered__correct(test_class):
    GenericIoMeta.verify_extension_is_registered(".test")


def test_verify_extension_is_registered__incorrect(test_class):
    with pytest.raises(UserConfigError):
        GenericIoMeta.verify_extension_is_registered(".none")


def test_new__method(test_class):
    for _ext in test_class.extensions:
        assert _ext in GenericIoMeta.registry


def test_new__method__multiple(test_class, test_class2):
    for _ext in test_class.extensions + test_class2.extensions:
        assert _ext in GenericIoMeta.registry


def test_clear_registry(test_class):
    GenericIoMeta.clear_registry()
    assert GenericIoMeta.registry == {}


def test_register_class__plain(get_unregistered_test_class):
    klass = get_unregistered_test_class
    GenericIoMeta.register_class(klass)
    for _ext in klass.extensions:
        assert _ext in GenericIoMeta.registry


def test_register_class__same_ext_no_update(get_unregistered_test_class):
    klass = get_unregistered_test_class
    GenericIoMeta.register_class(klass)
    with pytest.raises(KeyError):
        GenericIoMeta.register_class(klass)


def test_register_class__same_ext_and_update(get_unregistered_test_class):
    klass = get_unregistered_test_class
    GenericIoMeta.register_class(klass)
    GenericIoMeta.register_class(klass, update_registry=True)
    for _ext in klass.extensions:
        assert _ext in GenericIoMeta.registry


def test_register_class__normalizes_extensions():
    class TestClassUpper(metaclass=GenericIoMeta):
        extensions = ["DUMMY", ".TEST", "MiXeD"]
        format_name = "NORM"

    assert ".dummy" in GenericIoMeta.registry
    assert ".test" in GenericIoMeta.registry
    assert ".mixed" in GenericIoMeta.registry


@pytest.mark.parametrize("ext", ["DUMMY", ".DUMMY", "dummy", ".dummy"])
def test_is_extension_registered__case_and_dot_insensitive(test_class, ext):
    assert GenericIoMeta.is_extension_registered(ext) is True


@pytest.mark.parametrize("ext", ["TEST", ".TEST", "test", ".test"])
def test_verify_extension_is_registered__case_and_dot_insensitive(test_class, ext):
    GenericIoMeta.verify_extension_is_registered(ext)


def test_registry__stores_extensions_normalized(test_class):
    for key in GenericIoMeta.registry:
        assert key == key.lower()
        assert key.startswith(".")


def test_register_class__duplicate_after_normalization():
    class TestClass1(metaclass=GenericIoMeta):
        extensions = [".TEST"]
        format_name = "A"

    class TestClass2:
        extensions = ["test"]
        format_name = "B"

    with pytest.raises(KeyError):
        GenericIoMeta.register_class(TestClass2)

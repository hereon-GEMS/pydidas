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

"""Unit tests for LazyObject, LazySet, and LazyDict in lazy_objects."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import pytest

from pydidas.core.lazy_imports.lazy_objects import LazyDict, LazyObject, LazySet


# ---------------------------------------------------------------------------
# LazyObject
# ---------------------------------------------------------------------------


def test_lazy_object__real_obj_none_before_use():
    proxy = LazyObject("pathlib", "Path")
    assert proxy._real_obj is None


def test_lazy_object__repr_before_resolution():
    proxy = LazyObject("some.module", "SomeClass")
    assert repr(proxy) == "<lazy proxy for some.module.SomeClass>"


def test_lazy_object__call_no_args():
    from pathlib import Path

    proxy = LazyObject("pathlib", "Path")
    result = proxy()
    assert isinstance(result, Path)


def test_lazy_object__call_with_positional_arg():
    from pathlib import Path

    proxy = LazyObject("pathlib", "Path")
    result = proxy("/tmp")
    assert result == Path("/tmp")


def test_lazy_object__call_with_keyword_args():
    proxy = LazyObject("os.path", "join")
    import os.path

    result = proxy("a", "b", "c")
    assert result == os.path.join("a", "b", "c")


@pytest.mark.parametrize(
    "args",
    [(), ("/some/path",), ("a", "b")],
)
def test_lazy_object__call_various_signatures(args):
    from pathlib import Path

    proxy = LazyObject("pathlib", "Path")
    result = proxy(*args)
    assert isinstance(result, Path)


def test_lazy_object__real_obj_cached_after_call():
    proxy = LazyObject("pathlib", "Path")
    proxy()
    assert proxy._real_obj is not None


def test_lazy_object__real_obj_is_same_on_repeated_calls():
    proxy = LazyObject("pathlib", "Path")
    proxy()
    cached = proxy._real_obj
    proxy("/other")
    assert proxy._real_obj is cached


def test_lazy_object__resolve_imports_once(monkeypatch):
    import importlib

    call_count = {"n": 0}
    _original = importlib.import_module

    def counting_import(name, *args, **kwargs):
        call_count["n"] += 1
        return _original(name, *args, **kwargs)

    proxy = LazyObject("pathlib", "Path")
    monkeypatch.setattr(importlib, "import_module", counting_import)
    proxy()
    proxy()
    proxy("/third")
    assert call_count["n"] == 1


def test_lazy_object__getattr_forwards_to_real_class():
    from pathlib import Path

    proxy = LazyObject("pathlib", "Path")
    assert proxy.home() == Path.home()


def test_lazy_object__isinstance_true_for_instance_of_real_class():
    from pathlib import Path

    proxy = LazyObject("pathlib", "Path")
    assert isinstance(Path("."), proxy)


def test_lazy_object__isinstance_true_for_proxy_created_instance():
    proxy = LazyObject("pathlib", "Path")
    instance = proxy("/tmp")
    assert isinstance(instance, proxy)


def test_lazy_object__isinstance_false_for_unrelated_type():
    proxy = LazyObject("pathlib", "Path")
    assert not isinstance(42, proxy)
    assert not isinstance("string", proxy)


def test_lazy_object__subclasscheck_true_for_subclass():
    from pathlib import Path

    proxy = LazyObject("pathlib", "PurePath")
    assert issubclass(Path, proxy)


def test_lazy_object__subclasscheck_false_for_unrelated_class():
    proxy = LazyObject("pathlib", "Path")
    assert not issubclass(int, proxy)


def test_lazy_object__function_proxy_callable():
    proxy = LazyObject("os.path", "join")
    import os.path

    assert proxy("foo", "bar") == os.path.join("foo", "bar")


def test_lazy_object__invalid_module_raises_on_resolve():
    proxy = LazyObject("no.such.module", "SomeClass")
    with pytest.raises(ModuleNotFoundError):
        proxy()


def test_lazy_object__invalid_attr_raises_on_resolve():
    proxy = LazyObject("pathlib", "NoSuchClass")
    with pytest.raises(AttributeError):
        proxy()


# ---------------------------------------------------------------------------
# LazySet
# ---------------------------------------------------------------------------


def _make_lazy_set(items):
    """Return a LazySet whose init_function yields *items*."""
    return LazySet(lambda: items)


def test_lazy_set__not_initialized_before_first_access():
    ls = _make_lazy_set({1, 2, 3})
    assert not ls._initialized


def test_lazy_set__contains_triggers_initialization():
    ls = _make_lazy_set({10, 20, 30})
    _ = 10 in ls
    assert ls._initialized


def test_lazy_set__contains_true_for_member():
    ls = _make_lazy_set({"a", "b", "c"})
    assert "a" in ls
    assert "b" in ls


def test_lazy_set__contains_false_for_non_member():
    ls = _make_lazy_set({"a", "b"})
    assert "z" not in ls


def test_lazy_set__iter_yields_all_items():
    items = {1, 2, 3, 4}
    ls = _make_lazy_set(items)
    assert {x for x in ls} == items


def test_lazy_set__len_returns_correct_count():
    ls = _make_lazy_set({1, 2, 3})
    assert len(ls) == 3


def test_lazy_set__len_empty_set_is_zero():
    ls = _make_lazy_set(set())
    assert len(ls) == 0


def test_lazy_set__bool_true_for_non_empty():
    ls = _make_lazy_set({42})
    assert bool(ls)


def test_lazy_set__bool_false_for_empty():
    ls = _make_lazy_set(set())
    assert not bool(ls)


def test_lazy_set__init_function_called_once():
    call_count = {"n": 0}

    def counting_init():
        call_count["n"] += 1
        return {1, 2, 3}

    ls = LazySet(counting_init)
    _ = 1 in ls
    _ = 2 in ls
    _ = len(ls)
    assert call_count["n"] == 1


@pytest.mark.parametrize("items", [{1, 2, 3}, {"x", "y"}, set()])
def test_lazy_set__parametrized_items(items):
    ls = _make_lazy_set(items)
    assert {x for x in ls} == items


# ---------------------------------------------------------------------------
# LazyDict
# ---------------------------------------------------------------------------


def _make_lazy_dict(mapping):
    """Return a LazyDict whose init_function yields *mapping*."""
    return LazyDict(lambda: mapping)


def test_lazy_dict__not_initialized_before_first_access():
    ld = _make_lazy_dict({"a": 1})
    assert not ld._initialized


def test_lazy_dict__getitem_triggers_initialization():
    ld = _make_lazy_dict({"key": "value"})
    _ = ld["key"]
    assert ld._initialized


def test_lazy_dict__getitem_returns_correct_value():
    ld = _make_lazy_dict({"x": 42, "y": 99})
    assert ld["x"] == 42
    assert ld["y"] == 99


def test_lazy_dict__getitem_missing_key_raises():
    ld = _make_lazy_dict({"a": 1})
    with pytest.raises(KeyError):
        _ = ld["missing"]


def test_lazy_dict__contains_true_for_existing_key():
    ld = _make_lazy_dict({"hello": "world"})
    assert "hello" in ld


def test_lazy_dict__contains_false_for_missing_key():
    ld = _make_lazy_dict({"hello": "world"})
    assert "missing" not in ld


def test_lazy_dict__setitem_adds_entry():
    ld = _make_lazy_dict({"a": 1})
    ld["b"] = 2
    assert ld["b"] == 2


def test_lazy_dict__setitem_triggers_initialization():
    ld = _make_lazy_dict({"a": 1})
    ld["b"] = 2
    assert ld._initialized


def test_lazy_dict__iter_yields_all_keys():
    mapping = {"x": 1, "y": 2, "z": 3}
    ld = _make_lazy_dict(mapping)
    assert set(ld) == set(mapping)


def test_lazy_dict__len_returns_correct_count():
    ld = _make_lazy_dict({"a": 1, "b": 2, "c": 3})
    assert len(ld) == 3


def test_lazy_dict__len_empty_dict_is_zero():
    ld = _make_lazy_dict({})
    assert len(ld) == 0


def test_lazy_dict__bool_true_for_non_empty():
    ld = _make_lazy_dict({"k": "v"})
    assert bool(ld)


def test_lazy_dict__bool_false_for_empty():
    ld = _make_lazy_dict({})
    assert not bool(ld)


def test_lazy_dict__init_function_called_once():
    call_count = {"n": 0}

    def counting_init():
        call_count["n"] += 1
        return {"a": 1, "b": 2}

    ld = LazyDict(counting_init)
    _ = "a" in ld
    _ = ld["b"]
    _ = len(ld)
    assert call_count["n"] == 1


@pytest.mark.parametrize(
    "mapping",
    [{"a": 1, "b": 2}, {"x": "hello"}, {}],
)
def test_lazy_dict__parametrized_contents(mapping):
    ld = _make_lazy_dict(mapping)
    assert {k: ld[k] for k in ld} == mapping


if __name__ == "__main__":
    pytest.main([__file__])

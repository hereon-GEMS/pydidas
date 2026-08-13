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


def test_lazy_object__resolve_returns_real_class():
    from pathlib import Path

    proxy = LazyObject("pathlib", "Path")
    assert proxy.resolve() is Path


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


def test_lazy_object__mro_entries_used_as_base_class():
    from pathlib import PurePath

    proxy = LazyObject("pathlib", "PurePath")

    class MyPath(proxy):
        pass

    assert issubclass(MyPath, PurePath)


def test_lazy_object__mro_entries_returns_tuple_with_real_class():
    proxy = LazyObject("pathlib", "Path")
    result = proxy.__mro_entries__(())
    from pathlib import Path

    assert result == (Path,)


def test_lazy_object__or_two_lazy_objects():
    import types

    proxy_a = LazyObject("pathlib", "Path")
    proxy_b = LazyObject("pathlib", "PurePath")
    union = proxy_a | proxy_b
    assert isinstance(union, types.UnionType)


def test_lazy_object__or_with_real_type():
    import types

    proxy = LazyObject("pathlib", "Path")
    union = proxy | int
    assert isinstance(union, types.UnionType)


def test_lazy_object__ror_with_real_type():
    import types

    proxy = LazyObject("pathlib", "Path")
    union = int | proxy
    assert isinstance(union, types.UnionType)


# ---------------------------------------------------------------------------
# LazySet
# ---------------------------------------------------------------------------


def _make_lazy_set(items):
    """Return a LazySet whose init_function yields *items*."""
    return LazySet(lambda: items)


def test_lazy_set__not_initialized_before_first_access():
    ls = _make_lazy_set({1, 2, 3})
    assert not ls._initialized


def test_lazy_set__named_methods_replaced_with_native_after_init():
    ls = _make_lazy_set({1, 2, 3})
    _ = 1 in ls
    assert type(ls.copy) is type(set.__dict__["copy"].__get__(ls))


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


def test_lazy_set__iter_triggers_initialization():
    ls = _make_lazy_set({1, 2, 3})
    _ = list(ls)
    assert ls._initialized


def test_lazy_set__iter_yields_all_items():
    items = {1, 2, 3, 4}
    ls = _make_lazy_set(items)
    assert {x for x in ls} == items


def test_lazy_set__len_triggers_initialization():
    ls = _make_lazy_set({1, 2, 3})
    _ = len(ls)
    assert ls._initialized


def test_lazy_set__len_returns_correct_count():
    ls = _make_lazy_set({1, 2, 3})
    assert len(ls) == 3


def test_lazy_set__len_empty_set_is_zero():
    ls = _make_lazy_set(set())
    assert len(ls) == 0


def test_lazy_set__bool_triggers_initialization():
    ls = _make_lazy_set({1})
    _ = bool(ls)
    assert ls._initialized


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


def test_lazy_dict__named_methods_replaced_with_native_after_init():
    ld = _make_lazy_dict({"a": 1})
    _ = ld["a"]
    assert type(ld.keys) is type(dict.__dict__["keys"].__get__(ld))


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


def test_lazy_dict__contains_triggers_initialization():
    ld = _make_lazy_dict({"hello": "world"})
    _ = "hello" in ld
    assert ld._initialized


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


def test_lazy_dict__iter_triggers_initialization():
    ld = _make_lazy_dict({"x": 1, "y": 2})
    _ = list(ld)
    assert ld._initialized


def test_lazy_dict__iter_yields_all_keys():
    mapping = {"x": 1, "y": 2, "z": 3}
    ld = _make_lazy_dict(mapping)
    assert set(ld) == set(mapping)


def test_lazy_dict__len_triggers_initialization():
    ld = _make_lazy_dict({"a": 1, "b": 2})
    _ = len(ld)
    assert ld._initialized


def test_lazy_dict__len_returns_correct_count():
    ld = _make_lazy_dict({"a": 1, "b": 2, "c": 3})
    assert len(ld) == 3


def test_lazy_dict__len_empty_dict_is_zero():
    ld = _make_lazy_dict({})
    assert len(ld) == 0


def test_lazy_dict__bool_triggers_initialization():
    ld = _make_lazy_dict({"k": "v"})
    _ = bool(ld)
    assert ld._initialized


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


def test_lazy_dict__get_returns_value_for_existing_key():
    ld = _make_lazy_dict({"x": 42})
    assert ld.get("x") == 42


def test_lazy_dict__get_returns_default_for_missing_key():
    ld = _make_lazy_dict({"x": 42})
    assert ld.get("missing") is None
    assert ld.get("missing", 99) == 99


def test_lazy_dict__get_triggers_initialization():
    ld = _make_lazy_dict({"x": 1})
    _ = ld.get("x")
    assert ld._initialized


def test_lazy_set__copy_triggers_initialization():
    ls = _make_lazy_set({1, 2, 3})
    _ = ls.copy()
    assert ls._initialized


def test_lazy_set__copy_returns_correct_set():
    ls = _make_lazy_set({1, 2, 3})
    assert ls.copy() == {1, 2, 3}


def test_lazy_set__eq_triggers_initialization():
    ls = _make_lazy_set({1, 2})
    _ = ls == {1, 2}
    assert ls._initialized


def test_lazy_set__eq_correct():
    ls = _make_lazy_set({1, 2, 3})
    assert ls == {1, 2, 3}
    assert not (ls == {1, 2})


def test_lazy_set__union_triggers_initialization():
    ls = _make_lazy_set({1, 2})
    _ = ls.union({3})
    assert ls._initialized


def test_lazy_set__union_returns_correct_set():
    ls = _make_lazy_set({1, 2})
    assert ls.union({3}) == {1, 2, 3}


def test_lazy_set__intersection_returns_correct_set():
    ls = _make_lazy_set({1, 2, 3})
    assert ls.intersection({2, 3, 4}) == {2, 3}


def test_lazy_set__difference_returns_correct_set():
    ls = _make_lazy_set({1, 2, 3})
    assert ls.difference({2}) == {1, 3}


def test_lazy_set__symmetric_difference_returns_correct_set():
    ls = _make_lazy_set({1, 2, 3})
    assert ls.symmetric_difference({2, 4}) == {1, 3, 4}


def test_lazy_set__issubset_triggers_initialization():
    ls = _make_lazy_set({1, 2})
    _ = ls.issubset({1, 2, 3})
    assert ls._initialized


@pytest.mark.parametrize(
    "items,other,expected",
    [
        ({1, 2}, {1, 2, 3}, True),
        ({1, 2}, {1}, False),
    ],
)
def test_lazy_set__issubset(items, other, expected):
    ls = _make_lazy_set(items)
    assert ls.issubset(other) == expected


@pytest.mark.parametrize(
    "items,other,expected",
    [
        ({1, 2, 3}, {1, 2}, True),
        ({1}, {1, 2}, False),
    ],
)
def test_lazy_set__issuperset(items, other, expected):
    ls = _make_lazy_set(items)
    assert ls.issuperset(other) == expected


@pytest.mark.parametrize(
    "items,other,expected",
    [
        ({1, 2}, {3, 4}, True),
        ({1, 2}, {2, 3}, False),
    ],
)
def test_lazy_set__isdisjoint(items, other, expected):
    ls = _make_lazy_set(items)
    assert ls.isdisjoint(other) == expected


def test_lazy_set__or_operator_triggers_initialization():
    ls = _make_lazy_set({1, 2})
    _ = ls | {3}
    assert ls._initialized


def test_lazy_set__or_operator_returns_correct_set():
    ls = _make_lazy_set({1, 2})
    assert (ls | {3}) == {1, 2, 3}


def test_lazy_set__and_operator_returns_correct_set():
    ls = _make_lazy_set({1, 2, 3})
    assert (ls & {2, 3, 4}) == {2, 3}


def test_lazy_set__sub_operator_returns_correct_set():
    ls = _make_lazy_set({1, 2, 3})
    assert (ls - {2}) == {1, 3}


def test_lazy_set__xor_operator_returns_correct_set():
    ls = _make_lazy_set({1, 2, 3})
    assert (ls ^ {2, 4}) == {1, 3, 4}


def test_lazy_set__ior_triggers_initialization():
    ls = _make_lazy_set({1, 2})
    ls |= {3}
    assert ls._initialized


def test_lazy_set__ior_updates_correctly():
    ls = _make_lazy_set({1, 2})
    ls |= {3}
    assert 3 in ls


def test_lazy_set__iand_updates_correctly():
    ls = _make_lazy_set({1, 2, 3})
    ls &= {2, 3}
    assert ls == {2, 3}


def test_lazy_set__isub_updates_correctly():
    ls = _make_lazy_set({1, 2, 3})
    ls -= {2}
    assert ls == {1, 3}


def test_lazy_set__ixor_updates_correctly():
    ls = _make_lazy_set({1, 2, 3})
    ls ^= {2, 4}
    assert ls == {1, 3, 4}


def test_lazy_set__add_triggers_initialization():
    ls = _make_lazy_set({1, 2})
    ls.add(99)
    assert ls._initialized


def test_lazy_set__add_includes_existing_and_new_elements():
    ls = _make_lazy_set({1, 2})
    ls.add(3)
    assert ls == {1, 2, 3}


def test_lazy_set__remove_triggers_initialization():
    ls = _make_lazy_set({1, 2, 3})
    ls.remove(1)
    assert ls._initialized


def test_lazy_set__remove_deletes_element():
    ls = _make_lazy_set({1, 2, 3})
    ls.remove(2)
    assert ls == {1, 3}


def test_lazy_set__discard_does_not_raise_for_missing():
    ls = _make_lazy_set({1, 2})
    ls.discard(99)
    assert ls == {1, 2}


def test_lazy_set__pop_triggers_initialization():
    ls = _make_lazy_set({42})
    _ = ls.pop()
    assert ls._initialized


def test_lazy_set__pop_reduces_length():
    ls = _make_lazy_set({1, 2, 3})
    ls.pop()
    assert len(ls) == 2


def test_lazy_set__clear_triggers_initialization():
    ls = _make_lazy_set({1, 2, 3})
    ls.clear()
    assert ls._initialized


def test_lazy_set__clear_empties_set():
    ls = _make_lazy_set({1, 2, 3})
    ls.clear()
    assert len(ls) == 0


def test_lazy_set__update_triggers_initialization():
    ls = _make_lazy_set({1, 2})
    ls.update({3})
    assert ls._initialized


def test_lazy_set__update_adds_elements():
    ls = _make_lazy_set({1, 2})
    ls.update({3, 4})
    assert ls == {1, 2, 3, 4}


def test_lazy_set__intersection_update_updates_correctly():
    ls = _make_lazy_set({1, 2, 3})
    ls.intersection_update({2, 3})
    assert ls == {2, 3}


def test_lazy_set__difference_update_updates_correctly():
    ls = _make_lazy_set({1, 2, 3})
    ls.difference_update({2})
    assert ls == {1, 3}


def test_lazy_set__symmetric_difference_update_updates_correctly():
    ls = _make_lazy_set({1, 2, 3})
    ls.symmetric_difference_update({2, 4})
    assert ls == {1, 3, 4}


# ---------------------------------------------------------------------------
# LazyDict — additional mapping API
# ---------------------------------------------------------------------------


def test_lazy_dict__keys_triggers_initialization():
    ld = _make_lazy_dict({"a": 1, "b": 2})
    _ = list(ld.keys())
    assert ld._initialized


def test_lazy_dict__keys_returns_all_keys():
    mapping = {"a": 1, "b": 2}
    ld = _make_lazy_dict(mapping)
    assert set(ld.keys()) == set(mapping.keys())


def test_lazy_dict__values_triggers_initialization():
    ld = _make_lazy_dict({"a": 1})
    _ = list(ld.values())
    assert ld._initialized


def test_lazy_dict__values_returns_all_values():
    ld = _make_lazy_dict({"a": 1, "b": 2})
    assert sorted(ld.values()) == [1, 2]


def test_lazy_dict__items_triggers_initialization():
    ld = _make_lazy_dict({"a": 1})
    _ = list(ld.items())
    assert ld._initialized


def test_lazy_dict__items_returns_all_pairs():
    mapping = {"a": 1, "b": 2}
    ld = _make_lazy_dict(mapping)
    assert dict(ld.items()) == mapping


def test_lazy_dict__copy_triggers_initialization():
    ld = _make_lazy_dict({"a": 1})
    _ = ld.copy()
    assert ld._initialized


def test_lazy_dict__copy_returns_correct_dict():
    mapping = {"a": 1, "b": 2}
    ld = _make_lazy_dict(mapping)
    assert ld.copy() == mapping


def test_lazy_dict__eq_triggers_initialization():
    ld = _make_lazy_dict({"a": 1})
    _ = ld == {"a": 1}
    assert ld._initialized


def test_lazy_dict__eq_correct():
    mapping = {"a": 1, "b": 2}
    ld = _make_lazy_dict(mapping)
    assert ld == mapping
    # explicitly test equality, therefore not ( a == b) instead of a != b:
    assert not (ld == {"a": 1})  # noqa: SIM201


def test_lazy_dict__pop_triggers_initialization():
    ld = _make_lazy_dict({"a": 1, "b": 2})
    _ = ld.pop("a")
    assert ld._initialized


def test_lazy_dict__pop_removes_and_returns_value():
    ld = _make_lazy_dict({"a": 1, "b": 2})
    val = ld.pop("a")
    assert val == 1
    assert "a" not in ld


def test_lazy_dict__pop_returns_default_for_missing_key():
    ld = _make_lazy_dict({"a": 1})
    assert ld.pop("missing", 99) == 99


def test_lazy_dict__popitem_triggers_initialization():
    ld = _make_lazy_dict({"a": 1})
    _ = ld.popitem()
    assert ld._initialized


def test_lazy_dict__popitem_removes_and_returns_pair():
    ld = _make_lazy_dict({"a": 1})
    key, val = ld.popitem()
    assert key == "a"
    assert val == 1
    assert len(ld) == 0


def test_lazy_dict__update_triggers_initialization():
    ld = _make_lazy_dict({"a": 1})
    ld.update({"b": 2})
    assert ld._initialized


def test_lazy_dict__update_merges_entries():
    ld = _make_lazy_dict({"a": 1})
    ld.update({"b": 2, "c": 3})
    assert ld["a"] == 1
    assert ld["b"] == 2
    assert ld["c"] == 3


def test_lazy_dict__setdefault_triggers_initialization():
    ld = _make_lazy_dict({"a": 1})
    ld.setdefault("b", 99)
    assert ld._initialized


def test_lazy_dict__setdefault_returns_existing_value():
    ld = _make_lazy_dict({"a": 1})
    assert ld.setdefault("a", 99) == 1


def test_lazy_dict__setdefault_inserts_and_returns_default():
    ld = _make_lazy_dict({"a": 1})
    assert ld.setdefault("new", 42) == 42
    assert ld["new"] == 42


def test_lazy_dict__or_operator_triggers_initialization():
    ld = _make_lazy_dict({"a": 1})
    _ = ld | {"b": 2}
    assert ld._initialized


def test_lazy_dict__or_operator_merges_correctly():
    ld = _make_lazy_dict({"a": 1})
    result = ld | {"b": 2}
    assert result == {"a": 1, "b": 2}


def test_lazy_dict__ior_operator_merges_correctly():
    ld = _make_lazy_dict({"a": 1})
    ld |= {"b": 2}
    assert ld["a"] == 1
    assert ld["b"] == 2


# ---------------------------------------------------------------------------
# Startup import contract (subprocess isolation)
# ---------------------------------------------------------------------------


def test_pydidas_import__does_not_eagerly_load_heavy_deps():
    import subprocess
    import sys

    script = (
        "import sys; "
        "import pydidas; "
        "heavy = ['pyFAI', 'fabio', 'skimage', 'matplotlib.pyplot']; "
        "loaded = [m for m in heavy if m in sys.modules]; "
        "print(loaded)"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "[]", (
        f"Unexpected eager imports after 'import pydidas': {result.stdout.strip()}"
    )


if __name__ == "__main__":
    pytest.main([__file__])

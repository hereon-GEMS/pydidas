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
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import copy
import json
import pickle

import pytest
import yaml

from pydidas.core import ConfigDict


def test_init__empty():
    assert ConfigDict() == {}


def test_init__with_data():
    cfg = ConfigDict({"a": 1}, b=2)
    assert cfg == {"a": 1, "b": 2}
    assert isinstance(cfg, dict)


@pytest.mark.parametrize("key", [1, None, (1, 2), 1.5])
def test_init__non_str_key(key):
    with pytest.raises(TypeError):
        ConfigDict({key: 1})


@pytest.mark.parametrize("key", [1, None, b"a"])
def test_setitem__non_str_key(key):
    cfg = ConfigDict()
    with pytest.raises(TypeError):
        cfg[key] = 1
    assert len(cfg) == 0


def test_update__non_str_key():
    cfg = ConfigDict(a=1)
    with pytest.raises(TypeError):
        cfg.update({"b": 2, 3: 4})
    with pytest.raises(TypeError):
        cfg.update([(3, 4)])
    assert "a" in cfg


def test_setdefault():
    cfg = ConfigDict(a=1)
    assert cfg.setdefault("a", 5) == 1
    assert cfg.setdefault("b", 5) == 5
    assert cfg.b == 5
    with pytest.raises(TypeError):
        cfg.setdefault(1, 2)


def test_getattr():
    cfg = ConfigDict(a=1)
    assert cfg.a == 1


def test_getattr__missing():
    with pytest.raises(AttributeError):
        _ = ConfigDict().missing
    assert not hasattr(ConfigDict(), "missing")


def test_setattr():
    cfg = ConfigDict()
    cfg.new = 12
    assert cfg["new"] == 12
    cfg.new = 13
    assert cfg["new"] == 13


def test_setattr__reserved_name():
    cfg = ConfigDict()
    with pytest.raises(AttributeError):
        cfg.items = 1
    assert len(cfg) == 0


def test_reserved_key_item_access():
    cfg = ConfigDict(items=1)
    assert cfg["items"] == 1
    assert callable(cfg.items)


def test_delattr():
    cfg = ConfigDict(a=1)
    del cfg.a
    assert "a" not in cfg
    with pytest.raises(AttributeError):
        del cfg.a


def test_delattr__reserved_name():
    cfg = ConfigDict(items=1)

    with pytest.raises(AttributeError, match="reserved name"):
        del cfg.items
    assert cfg["items"] == 1


def test_copy():
    cfg = ConfigDict(a=1)
    new = cfg.copy()
    assert isinstance(new, ConfigDict)
    assert new == cfg
    assert new is not cfg


def test_deepcopy_and_pickle():
    cfg = ConfigDict(a=[1, 2])
    deep = copy.deepcopy(cfg)
    assert isinstance(deep, ConfigDict)
    assert deep == cfg and deep.a is not cfg.a
    assert pickle.loads(pickle.dumps(cfg)) == cfg
    assert isinstance(pickle.loads(pickle.dumps(cfg)), ConfigDict)


def test_fromkeys():
    cfg = ConfigDict.fromkeys(["a", "b"], 3)
    assert isinstance(cfg, ConfigDict)
    assert cfg == {"a": 3, "b": 3}
    with pytest.raises(TypeError):
        ConfigDict.fromkeys([1])


def test_or_operators():
    cfg = ConfigDict(a=1)
    merged = cfg | {"b": 2}
    assert isinstance(merged, ConfigDict) and merged == {"a": 1, "b": 2}
    rmerged = {"b": 2} | cfg
    assert isinstance(rmerged, ConfigDict) and rmerged == {"a": 1, "b": 2}
    with pytest.raises(TypeError):
        cfg | {1: 2}
    cfg |= {"c": 3}
    assert cfg.c == 3
    with pytest.raises(TypeError):
        cfg |= {1: 2}


@pytest.mark.parametrize("operator", ["or", "ror"])
def test_merge_operators__non_dict_operand(operator):
    cfg = ConfigDict(a=1)
    method = cfg.__or__ if operator == "or" else cfg.__ror__

    assert method(object()) is NotImplemented


def test_dir():
    assert "my_key" in dir(ConfigDict(my_key=1))


@pytest.mark.parametrize(
    ("cfg", "expected"),
    [(ConfigDict(), "ConfigDict()"), (ConfigDict(a=1), "ConfigDict('a': 1)")],
)
def test_repr(cfg, expected):
    assert repr(cfg) == expected


def test_hash__empty_config():
    assert hash(ConfigDict()) == 0


def test_hash__equal_configs_with_different_insertion_order():
    first = ConfigDict(a=1, b={"c": [2, 3], "d": 4}, e=(5, 6))
    second = ConfigDict(e=(5, 6), b={"d": 4, "c": [2, 3]}, a=1)

    assert first == second
    assert hash(first) == hash(second)


def test_hash__unhashable_nested_value_warns_and_continues():
    cfg = ConfigDict(values=[1, {"nested": [2, 3]}, {4, 5}])

    with pytest.warns(UserWarning, match="Could not hash"):
        result = hash(cfg)

    assert isinstance(result, int)


class _SubConfigDict(ConfigDict):
    pass


def test_copy__preserves_subclass():
    cfg = _SubConfigDict(a=1)
    new = cfg.copy()
    assert type(new) is _SubConfigDict
    assert new == cfg and new is not cfg


def test_fromkeys__preserves_subclass():
    cfg = _SubConfigDict.fromkeys(["a", "b"], 3)
    assert type(cfg) is _SubConfigDict
    assert cfg == {"a": 3, "b": 3}


def test_or_operators__preserve_subclass():
    cfg = _SubConfigDict(a=1)
    assert type(cfg | {"b": 2}) is _SubConfigDict
    assert type({"b": 2} | cfg) is _SubConfigDict
    alias = cfg
    cfg |= {"c": 3}
    assert cfg is alias and cfg.c == 3


def test_pickle__preserves_subclass():
    cfg = _SubConfigDict(a=1)
    restored = pickle.loads(pickle.dumps(cfg))
    assert type(restored) is _SubConfigDict
    assert restored == cfg


class _IntValueConfigDict(ConfigDict):
    restricted_value_types = (int,)


class _IntKeyConfigDict(ConfigDict):
    restricted_key_types = (int,)


def test_restricted_types__defaults():
    assert ConfigDict.restricted_key_types == (str,)
    assert ConfigDict.restricted_value_types is None


def test_restricted_value_types__accepts_valid_values():
    cfg = _IntValueConfigDict({"a": 1}, b=2)
    cfg.c = 3
    cfg.update(d=4)
    assert cfg == {"a": 1, "b": 2, "c": 3, "d": 4}
    assert cfg.setdefault("e", 5) == 5


@pytest.mark.parametrize("value", ["a", 1.5, None, [1]])
def test_restricted_value_types__rejects_invalid_values(value):
    cfg = _IntValueConfigDict(a=1)
    with pytest.raises(TypeError, match="values must be of type"):
        cfg["b"] = value
    with pytest.raises(TypeError):
        cfg.b = value
    with pytest.raises(TypeError):
        cfg.update(b=value)
    with pytest.raises(TypeError):
        _IntValueConfigDict(b=value)
    with pytest.raises(TypeError):
        cfg.setdefault("b", value)
    assert cfg == {"a": 1}


def test_restricted_value_types__applies_to_operators_and_copy():
    cfg = _IntValueConfigDict(a=1)
    assert type(cfg | {"b": 2}) is _IntValueConfigDict
    assert type(cfg.copy()) is _IntValueConfigDict
    with pytest.raises(TypeError):
        cfg | {"b": "invalid"}
    with pytest.raises(TypeError):
        {"b": "invalid"} | cfg
    with pytest.raises(TypeError):
        cfg |= {"b": "invalid"}


def test_restricted_key_types__custom_keys():
    cfg = _IntKeyConfigDict({1: "a"})
    cfg[2] = "b"
    assert cfg == {1: "a", 2: "b"}
    with pytest.raises(TypeError, match="_IntKeyConfigDict keys must be of type"):
        cfg["a"] = 1
    with pytest.raises(TypeError):
        _IntKeyConfigDict({"a": 1})


def test_check_key__error_message_contains_class_and_type_names():
    with pytest.raises(TypeError, match=r"ConfigDict keys must be of type.*int"):
        ConfigDict({1: 1})
    with pytest.raises(TypeError, match="_SubConfigDict keys must be of type"):
        _SubConfigDict({1: 1})


def _nested_config() -> ConfigDict:
    return ConfigDict(
        text="a",
        number=1,
        real=1.5,
        flag=True,
        nothing=None,
        sequence=[1, "b", None],
        mapping={"x": 1, "y": [2, 3]},
        nested=ConfigDict(inner="p", values=[1, 2]),
    )


@pytest.mark.parametrize("protocol", range(pickle.HIGHEST_PROTOCOL + 1))
def test_pickle__all_protocols_and_nested_values(protocol):
    cfg = _nested_config()
    restored = pickle.loads(pickle.dumps(cfg, protocol=protocol))
    assert type(restored) is ConfigDict
    assert restored == cfg
    assert type(restored.nested) is ConfigDict


def test_pickle__empty_config():
    restored = pickle.loads(pickle.dumps(ConfigDict()))
    assert type(restored) is ConfigDict
    assert restored == {}


def test_json_dumps__roundtrip():
    cfg = _nested_config()
    restored = ConfigDict(json.loads(json.dumps(cfg)))
    assert type(restored) is ConfigDict
    assert restored == cfg


@pytest.mark.parametrize("config_class", [ConfigDict, _SubConfigDict])
def test_yaml_safe_dump__roundtrip(config_class):
    cfg = config_class(_nested_config())
    text = yaml.safe_dump(cfg)
    restored = config_class(yaml.safe_load(text))
    assert type(restored) is config_class
    assert restored == cfg


def test_yaml_safe_dump__nested_config_dict_is_a_plain_mapping():
    cfg = _SubConfigDict(a=1, b=ConfigDict(c=2))
    assert yaml.safe_load(yaml.safe_dump({"outer": cfg})) == {
        "outer": {"a": 1, "b": {"c": 2}}
    }


if __name__ == "__main__":
    pytest.main([__file__])

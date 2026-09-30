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
import pickle

import pytest

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
        ConfigDict().missing
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


def test_dir():
    assert "my_key" in dir(ConfigDict(my_key=1))

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

import pytest

from pydidas.core import ConfigDict, ConfigDictMixin, ObjectWithParameterCollection
from pydidas.workflow import GenericTree


class _InitRecorder:
    def __init__(self, *args, **kwargs):
        self.init_args = args
        self.init_kwargs = kwargs


class _ConfigDictOwner(ConfigDictMixin, _InitRecorder):
    pass


def test_config_dict_mixin_init__forwards_arguments_and_config():
    owner = _ConfigDictOwner(
        "positional", config={"value": 1}, option=True, super_init=True
    )

    assert isinstance(owner.config, ConfigDict)
    assert owner.config == {"value": 1}
    assert owner.init_args == ("positional",)
    assert owner.init_kwargs == {"option": True, "super_init": True}


def test_config_dict_mixin_init__without_super_init():
    owner = _ConfigDictOwner(config={"value": 1}, super_init=False)

    assert owner.config == {"value": 1}
    assert not hasattr(owner, "init_args")


def test_config_dict_mixin_init__invalid_config_type():
    with pytest.raises(TypeError, match="Expected a dict"):
        _ConfigDictOwner(config=[])


@pytest.mark.parametrize("create_object", [ObjectWithParameterCollection, GenericTree])
def test_config_property__exposes_mapping_and_rejects_replacement(create_object):
    obj = create_object()

    assert isinstance(obj.config, ConfigDict)
    assert obj.config is obj.config
    with pytest.raises(AttributeError, match="cannot be replaced"):
        obj.config = {}
    with pytest.raises(TypeError):
        obj.config[1] = "invalid"


@pytest.mark.parametrize("create_object", [ObjectWithParameterCollection, GenericTree])
def test_config_property__preserves_config_dict_when_copied(create_object):
    obj = create_object()
    obj.config["nested"] = [1]

    shallow_copy = copy.copy(obj)
    deep_copy = copy.deepcopy(obj)

    assert isinstance(shallow_copy.config, ConfigDict)
    assert isinstance(deep_copy.config, ConfigDict)
    assert shallow_copy.config["nested"] == obj.config["nested"]
    assert deep_copy.config["nested"] == obj.config["nested"]
    assert deep_copy.config["nested"] is not obj.config["nested"]


if __name__ == "__main__":
    pytest.main([__file__])

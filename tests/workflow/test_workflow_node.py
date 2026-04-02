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


from typing import Any

import numpy as np
import pytest

from pydidas.contexts import DiffractionExperimentContext
from pydidas.core import Dataset
from pydidas.unittest_objects import DummyLoader, DummyProc
from pydidas.workflow import WorkflowNode


EXP = DiffractionExperimentContext()


class _PluginModifyInPlace(DummyProc):
    """Plugin to test modifying input data in place."""

    def execute(self, data: Dataset, **kwargs: Any) -> tuple[Dataset, dict]:
        data[0] = self.node_id
        kwargs[self.node_id] = "::called::"
        return data, kwargs


def create_node_tree(
    depth: int = 3,
    width: int = 3,
    root: WorkflowNode | None = None,
    node_register: dict | None = None,
) -> tuple:
    """
    Create a node tree for testing.

    Parameters
    ----------
    depth : int
        The depth of the tree.
    width : int
        The branching width of the tree.
    root : WorkflowNode or None
        The root of the tree.
    node_register : dict or None
        A dictionary to register nodes by their node_id.

    Returns
    -------
    tuple
        The node tree and the total number of nodes created.
    """
    if root is None:
        root = WorkflowNode(node_id=0, plugin=DummyLoader())
        node_register = {0: root}
    _this_tier = []
    for _ in range(width):
        _index = max(node_register) + 1
        _node = WorkflowNode(node_id=_index, plugin=DummyProc())
        root.add_child(_node)
        node_register[_node.node_id] = _node
        _this_tier.append(_node)

    if depth > 0:
        for _node in _this_tier:
            node_register = create_node_tree(
                depth=depth - 1, width=width, root=_node, node_register=node_register
            )
    return node_register


def test_init():
    """Test that plugin node_id is set correctly during initialization."""
    _node_id = 42
    obj = WorkflowNode(plugin=DummyLoader(), node_id=_node_id)
    assert obj.plugin.node_id == _node_id
    assert obj.results is None


def test_copy():
    """Test that copying a WorkflowNode preserves node_id."""
    _node_id = 42
    obj = WorkflowNode(plugin=DummyLoader(), node_id=_node_id)
    obj.plugin.set_param_value("binning", 3)
    new = obj.copy()
    assert new.plugin.node_id == _node_id
    assert obj.plugin.node_id == _node_id
    assert new.plugin.get_param_value("binning") == 3


def test_copy__with_EXP_property():
    """Test that copying preserves _EXP property."""
    _node_id = 42
    obj = WorkflowNode(plugin=DummyLoader(), node_id=_node_id)
    obj.plugin._EXP = EXP
    new = obj.copy()
    assert new.plugin.node_id == _node_id
    assert obj.plugin.node_id == _node_id
    assert obj.plugin._EXP == EXP
    assert new.plugin._EXP == EXP


@pytest.mark.parametrize("node_id", [None, 12, 42])
def test_node_id_property_get(node_id):
    """Test getting node_id property with various values."""
    obj = WorkflowNode(plugin=DummyLoader(), node_id=node_id)
    assert obj.node_id == node_id


@pytest.mark.parametrize("initial_id, new_id", [(None, 12), (5, 20), (42, 99)])
def test_node_id_property_set(initial_id, new_id):
    """Test setting node_id property syncs with plugin."""
    obj = WorkflowNode(plugin=DummyLoader(), node_id=initial_id)
    obj.node_id = new_id
    assert obj._node_id == new_id
    assert obj.plugin.node_id == new_id


@pytest.mark.parametrize("keep_results, expected", [(False, None), (True, (10, 10))])
def test_result_shape(keep_results, expected):
    """Test result_shape property with various configurations."""
    obj = WorkflowNode(plugin=DummyLoader())
    if keep_results:
        obj.plugin.set_param_value("keep_results", True)
        obj.execute_plugin(0)
    assert obj.result_shape == expected


def test_dump():
    """Test dump method returns dict with required keys."""
    obj = WorkflowNode(plugin=DummyLoader())
    _dump = obj.dump()
    assert isinstance(_dump, dict)
    for key in ("node_id", "parent", "children", "plugin_class", "plugin_params"):
        assert key in _dump.keys()


def test_execute_plugin_chain__w_plugin_modify_in_place():
    """Test execute_plugin_chain with plugins modifying data in place."""
    root = WorkflowNode(node_id=0, plugin=DummyLoader())
    child1 = WorkflowNode(node_id=1, plugin=_PluginModifyInPlace())
    child2 = WorkflowNode(node_id=2, plugin=_PluginModifyInPlace())
    child3 = WorkflowNode(node_id=3, plugin=DummyProc())
    root.add_child(child1)
    root.add_child(child2)
    root.add_child(child3)
    root.execute_plugin_chain(0, force_store_results=True, offset=3)
    _root_data = root.results
    _child1_data = child1.results
    _child2_data = child2.results
    _child3_data = child3.results
    assert np.all(_root_data > 0)
    assert np.allclose(_root_data + 3, _child3_data)
    assert np.allclose(_child1_data[0], 1)
    assert np.allclose(_child2_data[0], 2)
    for _key, _node in [[1, child1], [2, child2], ["offset_03", child3]]:
        assert set(_node.result_kws) == {_key, "offset", "index", "force_store_results"}


@pytest.mark.parametrize("force_store", [False, True])
def test_execute_plugin_chain__w_store_results(force_store):
    _depth = 3
    nodes = create_node_tree(depth=_depth)
    root = nodes[0]
    root.execute_plugin_chain(0, force_store_results=force_store)
    for _id, _node in nodes.items():
        if force_store or _node.is_leaf:
            assert _node.results is not None
            assert _node.result_kws is not None
        else:
            assert _node.results is None
            assert _node.result_kws is None


@pytest.mark.parametrize(
    "input_data,is_loader", [(0, True), (np.random.random((10, 10)), False)]
)
def test_execute_plugin_results(input_data, is_loader):
    """Test execute_plugin result types with different inputs."""
    if is_loader:
        obj = WorkflowNode(plugin=DummyLoader())
    else:
        obj = WorkflowNode(plugin=DummyProc())
    _res = obj.execute_plugin(input_data)
    assert isinstance(_res[1], dict)
    if not is_loader:
        assert isinstance(_res[0], np.ndarray)


def test_execute_plugin__simple():
    """Test simple plugin execution with DummyLoader."""
    _node = WorkflowNode(plugin=DummyLoader())
    _res = _node.execute_plugin(0)
    assert isinstance(_res[1], dict)


def test_execute_plugin__array_input():
    """Test plugin execution preserves array shape."""
    _input = np.random.random((10, 10))
    _node = WorkflowNode(plugin=DummyProc())
    _res = _node.execute_plugin(_input)
    assert isinstance(_res[0], np.ndarray)
    assert _input.shape == _res[0].shape


def test_execute_plugin__single_in_tree():
    """Test plugin execution within a node tree."""
    nodes = create_node_tree()
    _node = nodes[1]
    _res, _kws = _node.execute_plugin(0)
    assert isinstance(_res, (float, Dataset))
    assert isinstance(_kws, dict)


# Prepare execution test


def test_prepare_execution():
    """Test prepare_execution calls pre_execute on all nodes."""
    nodes = create_node_tree()
    _root = nodes[0]
    _root.prepare_execution()
    for _node in nodes.values():
        assert _node.plugin._pre_executed


def test_confirm_plugin_existence_and_type__no_plugin():
    """Test that KeyError is raised when no plugin is provided."""
    with pytest.raises(KeyError):
        WorkflowNode()


def test_confirm_plugin_existence_and_type__wrong_plugin():
    """Test that TypeError is raised when plugin is not BasePlugin."""
    with pytest.raises(TypeError):
        WorkflowNode(plugin=12)


def test_confirm_plugin_existence_and_type__correct_plugin():
    """Test that correct plugin type is accepted."""
    obj = WorkflowNode(plugin=DummyLoader())
    assert isinstance(obj, WorkflowNode)


@pytest.mark.parametrize(
    "ndim_parent_out,ndim_plugin_in,expected_check",
    [
        (-1, None, True),
        (-1, 2, True),
        (2, -1, True),
        (2, 2, True),
        (2, 1, False),
    ],
)
def test_consistency_check(ndim_parent_out, ndim_plugin_in, expected_check):
    """Test consistency_check with various dimension configurations."""
    _root = WorkflowNode(plugin=DummyLoader())
    assert _root.consistency_check() == True
    _child = WorkflowNode(plugin=DummyProc(), parent=_root)
    _root.plugin.base_output_data_dim = ndim_parent_out
    _child.plugin.input_data_dim = ndim_plugin_in
    assert _child.consistency_check() == expected_check


def test_hash__returns_int():
    """Test that hash returns an integer."""
    obj = WorkflowNode(plugin=DummyLoader(), node_id=0)
    assert isinstance(hash(obj), int)


def test_hash__complex_comparison():
    """Test hash equality with parent and same node_id."""
    _parent = WorkflowNode(plugin=DummyLoader(), node_id=0)
    _child1 = WorkflowNode(plugin=DummyProc(), node_id=1, parent=_parent)
    _child2 = WorkflowNode(plugin=DummyProc(), node_id=1, parent=_parent)
    assert hash(_child1) == hash(_child2)


@pytest.mark.parametrize("plugin_class", [DummyLoader, DummyProc])
@pytest.mark.parametrize("node_id", [2, 3])
@pytest.mark.parametrize("parent", [0, 1])
@pytest.mark.parametrize("label", ["", "Dummy"])
@pytest.mark.parametrize("n_children", [0, 1])
def test_hash_differs_on_config_change(
    plugin_class, node_id, parent, label, n_children
):
    """Test that hash differs with various configuration changes."""
    _parent = WorkflowNode(plugin=DummyLoader(), node_id=0)
    _parent2 = WorkflowNode(plugin=DummyProc(), node_id=1)
    _item1 = WorkflowNode(plugin=DummyProc(), node_id=2, parent=_parent)
    _item2 = WorkflowNode(
        plugin=plugin_class(),
        node_id=node_id,
        parent=_parent if parent == 0 else _parent2,
    )
    _item2.plugin.set_param_value("label", label)
    if n_children == 1:
        _child = WorkflowNode(plugin=DummyProc(), node_id=4, parent=_item2)

    if (
        plugin_class == DummyProc
        and node_id == 2
        and parent == 0
        and label == ""
        and n_children == 0
    ):
        assert hash(_item1) == hash(_item2)
    else:
        assert hash(_item1) != hash(_item2)


# ---------------------
# - Integration tests -
# ---------------------
def test_delete_note_references():
    """Test delete_note_references with children."""
    nodes = create_node_tree()
    _root = nodes[0]
    print("\nRoot children", _root.children)
    _root.delete_node_references(recursive=True)
    for _id, _node in nodes.items():
        print(_id, _node.children)
        assert _node.parent is None
        assert _node.children == []


if __name__ == "__main__":
    pytest.main([__file__])

# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import unittest
from copy import copy

from pydidas.core import UserConfigError
from pydidas.workflow import GenericNode, GenericTree


class TestGenericTree(unittest.TestCase):
    def setUp(self):
        ...

    def tearDown(self):
        ...

    def create_node_tree(self, depth=3, width=3):
        root = GenericNode(node_id=0)
        _nodes = [[root]]
        _index = 1
        for _depth in range(depth):
            _tiernodes = []
            for _parent in _nodes[_depth]:
                for _ichild in range(width):
                    _node = GenericNode(node_id=_index)
                    _parent.add_child(_node)
                    _index += 1
                    _tiernodes.append(_node)
            _nodes.append(_tiernodes)
        return _nodes, _index

    def test_init__plain(self):
        tree = GenericTree()
        self.assertIsInstance(tree, GenericTree)

    def test_init__with_kwargs(self):
        _val1 = 12
        _val2 = "something"
        tree = GenericTree(test1=_val1, test2=_val2)
        self.assertEqual(tree._config["test1"], _val1)
        self.assertEqual(tree._config["test2"], _val2)

    def test_clear(self):
        tree = GenericTree()
        tree.nodes = dict(a=1, b="c")
        tree.node_ids = [0, 1]
        tree.root = 12
        tree.clear()
        self.assertEqual(tree.nodes, {})
        self.assertEqual(tree.node_ids, [])
        self.assertIsNone(tree.root)

    def test_verify_node_type__with_node(self):
        tree = GenericTree()
        node = GenericNode()
        tree.verify_node_type(node)

    def test_verify_node_type__wrong_object(self):
        tree = GenericTree()
        node = 12
        with self.assertRaises(TypeError):
            tree.verify_node_type(node)

    def test_set_root__empty_tree(self):
        tree = GenericTree()
        node = GenericNode(parent=GenericNode(), node_id=42)
        tree.set_root(node)
        self.assertEqual(tree.nodes[0], node)
        self.assertEqual(node.node_id, 0)

    def test_set_root__node_in_tree(self):
        tree = GenericTree()
        parent = GenericNode(node_id=0)
        node = GenericNode(parent=parent, node_id=42)
        child = GenericNode(parent=node, node_id=112)
        self.assertEqual(node.parent, parent)
        tree.set_root(node)
        self.assertEqual(tree.nodes[0], node)
        self.assertEqual(node.node_id, 0)
        self.assertEqual(node.parent, None)
        self.assertTrue(child in tree.nodes.values())

    def test_active_node_setter__none(self):
        tree = GenericTree()
        tree._config["active_node"] = 1
        tree.active_node_id = None
        self.assertIsNone(tree.active_node_id)

    def test_active_node_setter__wrong_id(self):
        tree = GenericTree()
        with self.assertRaises(ValueError):
            tree.active_node_id = 12

    def test_active_node_setter__correct_id(self):
        tree = GenericTree()
        _nodes, _n_nodes = self.create_node_tree(depth=3, width=2)
        tree.register_node(_nodes[0][0])
        _id = tree.node_ids[-1]
        tree.active_node_id = _id
        self.assertEqual(_id, tree.active_node_id)

    def test_get_new_nodeid__empty_tree(self):
        tree = GenericTree()
        self.assertEqual(tree.get_new_nodeid(), 0)

    def test_get_new_nodeid__single_node(self):
        _id = 3
        tree = GenericTree()
        tree.node_ids = [_id]
        self.assertEqual(tree.get_new_nodeid(), _id + 1)

    def test_get_new_nodeid__multiple_nodes(self):
        _id = 3
        tree = GenericTree()
        tree.node_ids = [_id - 1, _id]
        self.assertEqual(tree.get_new_nodeid(), _id + 1)

    def test_check_node_ids__no_ids(self):
        tree = GenericTree()
        node = GenericNode()
        tree._check_node_ids(node.get_recursive_ids())

    def test_check_node_ids__new_id_okay(self):
        tree = GenericTree()
        node = GenericNode(node_id=5)
        tree.node_ids = [0, 1, 2, 3, 4]
        tree._check_node_ids(node.get_recursive_ids())

    def test_check_node_ids__new_id_too_small(self):
        tree = GenericTree()
        node = GenericNode(node_id=5)
        tree.node_ids = [0, 1, 2, 3, 4, 6]
        with self.assertRaises(ValueError):
            tree._check_node_ids(node.get_recursive_ids())

    def test_check_node_ids__new_id_duplicate(self):
        tree = GenericTree()
        node = GenericNode(node_id=5)
        tree.node_ids = [0, 1, 2, 3, 4, 5, 6]
        with self.assertRaises(ValueError):
            tree._check_node_ids(node.get_recursive_ids())

    def test_check_node_ids__duplicate_in_node_tree(self):
        tree = GenericTree()
        node = GenericNode(node_id=7)
        node2 = GenericNode(parent=node, node_id=6)
        GenericNode(parent=node2, node_id=8)
        tree.node_ids = [0, 1, 2, 3, 4, 5, 6]
        with self.assertRaises(ValueError):
            tree._check_node_ids(node.get_recursive_ids())

    def test_register_node__wrong_type(self):
        tree = GenericTree()
        with self.assertRaises(TypeError):
            tree.register_node(12)

    def test_register_node__simple_node(self):
        tree = GenericTree()
        node = GenericNode()
        tree.register_node(node)
        self.assertTrue(node in tree.nodes.values())
        self.assertEqual(tree.active_node_id, tree.node_ids[-1])

    def test_register_node__with_new_nodeid(self):
        tree = GenericTree()
        node = GenericNode()
        tree.register_node(node, node_id=3)
        self.assertTrue(node in tree.nodes.values())
        self.assertEqual(tree.active_node_id, tree.node_ids[-1])

    def test_register_node__node_tree_with_new_nodeid(self):
        tree = GenericTree()
        node = GenericNode()
        node2 = GenericNode(parent=node)
        node3 = GenericNode(parent=node2)
        tree.register_node(node, node_id=3)
        for _node in [node, node2, node3]:
            self.assertTrue(_node in tree.nodes.values())
        self.assertEqual(tree.active_node_id, tree.node_ids[-1])

    def test_register_node__node_tree_with_existing_nodeids(self):
        tree = GenericTree()
        node = GenericNode(node_id=3)
        node2 = GenericNode(parent=node)
        node3 = GenericNode(parent=node2)
        tree.register_node(node, node_id=3)
        for _node in [node, node2, node3]:
            self.assertTrue(_node in tree.nodes.values())
        self.assertEqual(tree.active_node_id, tree.node_ids[-1])

    def test_get_node_by_id(self):
        _id = 3
        tree = GenericTree()
        node = GenericNode(node_id=_id)
        tree.register_node(node)
        _node = tree.get_node_by_id(_id)
        self.assertEqual(node, _node)

    def test_get_node_by_id__no_node(self):
        _id = 3
        tree = GenericTree()
        node = GenericNode(node_id=_id + 1)
        tree.register_node(node)
        with self.assertRaises(KeyError):
            tree.get_node_by_id(_id)

    def test_delete_node_by_id__simple(self):
        tree = GenericTree()
        node = GenericNode(node_id=1)
        tree.register_node(node)
        self.assertTrue(node in tree.nodes.values())
        tree.delete_node_by_id(1)
        self.assertFalse(node in tree.nodes.values())
        self.assertFalse(1 in tree.node_ids)
        self.assertIsNone(tree.active_node_id)

    def test_delete_node_by_id__root_node_no_child(self):
        tree = GenericTree()
        node = GenericNode(node_id=0)
        tree.register_node(node)
        self.assertTrue(node in tree.nodes.values())
        tree.delete_node_by_id(0)
        self.assertFalse(node in tree.nodes.values())
        self.assertIsNone(tree.root)

    def test_delete_node_by_id__root_node_single_child_recursive(self):
        tree = GenericTree()
        node = GenericNode(node_id=0)
        _ = GenericNode(parent=node)
        tree.register_node(node)
        tree.delete_node_by_id(0)
        self.assertFalse(node in tree.nodes.values())
        self.assertIsNone(tree.root)
        self.assertEqual(tree.nodes, {})

    def test_delete_node_by_id__root_node_single_child_keep_children(self):
        tree = GenericTree()
        node = GenericNode(node_id=0)
        child = GenericNode(parent=node)
        tree.register_node(node)
        tree.delete_node_by_id(0, recursive=False, keep_children=True)
        self.assertFalse(node in tree.nodes.values())
        self.assertIsNone(child.parent)
        self.assertEqual(tree.root, child)
        self.assertEqual(tree.nodes, {1: child})

    def test_delete_node_by_id__root_node_single_child_no_flag(self):
        tree = GenericTree()
        node = GenericNode(node_id=0)
        _ = GenericNode(parent=node)
        tree.register_node(node)
        with self.assertRaises(UserConfigError):
            tree.delete_node_by_id(0, recursive=False, keep_children=False)

    def test_delete_node_by_id__root_node_multiple_children_recursive(self):
        tree = GenericTree()
        node = GenericNode(node_id=0)
        _ = GenericNode(parent=node)
        _ = GenericNode(parent=node)
        tree.register_node(node)
        self.assertEqual(tree.root.n_children, 2)
        tree.delete_node_by_id(0)
        self.assertIsNone(tree.root)
        self.assertEqual(tree.nodes, {})

    def test_delete_node_by_id__root_node_multiple_children_not_recursive(self):
        tree = GenericTree()
        node = GenericNode(node_id=0)
        _ = GenericNode(parent=node)
        _ = GenericNode(parent=node)
        tree.register_node(node)
        self.assertEqual(tree.root.n_children, 2)
        with self.assertRaises(UserConfigError):
            tree.delete_node_by_id(0, recursive=False)

    def test_delete_node_by_id__in_tree(self):
        tree = GenericTree()
        node = GenericNode(node_id=1)
        node2 = GenericNode(parent=node, node_id=2)
        node3 = GenericNode(parent=node2, node_id=3)
        tree.register_node(node)
        tree.delete_node_by_id(2)
        self.assertTrue(node in tree.nodes.values())
        self.assertFalse(node2 in tree.nodes.values())
        self.assertFalse(node3 in tree.nodes.values())
        self.assertEqual(node._children, [])
        self.assertEqual(tree.active_node_id, 1)
        self.assertFalse(2 in tree.node_ids)

    def test_delete_node_by_id__delete_in_other_branch(self):
        tree = GenericTree()
        node = GenericNode(node_id=1)
        node2 = GenericNode(parent=node, node_id=2)
        node3 = GenericNode(parent=node, node_id=3)
        tree.register_node(node)
        _active_id = tree.active_node_id
        tree.delete_node_by_id(2)
        self.assertTrue(node in tree.nodes.values())
        self.assertFalse(node2 in tree.nodes.values())
        self.assertTrue(node3 in tree.nodes.values())
        self.assertEqual(tree.active_node_id, _active_id)
        self.assertFalse(2 in tree.node_ids)

    def test_all_leaves__empty_tree(self):
        tree = GenericTree()
        self.assertEqual(tree.get_all_leaves(), [])

    def test_all_leaves__single_node(self):
        tree = GenericTree()
        node = GenericNode(node_id=1)
        tree.register_node(node)
        self.assertEqual(tree.get_all_leaves(), [node])

    def test_all_leaves__tree(self):
        _depth = 3
        _width = 4
        tree = GenericTree()
        _nodes, _n_nodes = self.create_node_tree(depth=_depth, width=_width)
        tree.register_node(_nodes[0][0])
        _leaves = tree.get_all_leaves()
        for _node in _nodes[_depth]:
            self.assertTrue(_node in _leaves)

    def test_change_node_parent(self):
        tree = GenericTree()
        _nodes, _n_nodes = self.create_node_tree(depth=3, width=2)
        tree.register_node(_nodes[0][0])
        _child1 = tree.root.get_children()[0]
        _id1 = _child1.node_id
        _child2 = tree.root.get_children()[1]
        _id2 = _child2.node_id
        _original_ids = set(tree.node_ids)
        tree.change_node_parent(_child2.node_id, _child1.node_id)
        _new_ids = set(tree.node_ids)
        self.assertTrue(tree.tree_has_changed)
        self.assertTrue(_child2 in _child1.get_children())
        self.assertFalse(_child2 in tree.root.get_children())
        self.assertEqual(_child2.parent, _child1)
        self.assertEqual(_original_ids, _new_ids)
        self.assertEqual(_child1.node_id, _id1)
        self.assertEqual(_child2.node_id, _id2)

    def test_change_node_parent__swap_ids(self):
        tree = GenericTree()
        _nodes, _n_nodes = self.create_node_tree(depth=3, width=2)
        tree.register_node(_nodes[0][0])
        _child1 = tree.root.get_children()[0]
        _id1 = _child1.node_id
        _child2 = tree.root.get_children()[1]
        _id2 = _child2.node_id
        _original_ids = set(tree.node_ids)
        tree.change_node_parent(_child1.node_id, _child2.node_id)
        _new_ids = set(tree.node_ids)
        self.assertTrue(tree.tree_has_changed)
        self.assertTrue(_child1 in _child2.get_children())
        self.assertFalse(_child1 in tree.root.get_children())
        self.assertEqual(_child1.parent, _child2)
        self.assertEqual(_original_ids, _new_ids)
        self.assertEqual(_child1.node_id, _id2)
        self.assertEqual(_child2.node_id, _id1)

    def test_order_node_ids__empty_tree(self):
        tree = GenericTree()
        tree.order_node_ids()
        self.assertIsNone(tree.root)

    def test_order_node_ids__single_node(self):
        tree = GenericTree()
        _node = GenericNode()
        _node.node_id = 12
        tree.register_node(_node)
        self.assertEqual(tree.active_node, _node)
        tree.order_node_ids()
        self.assertEqual(tree.root, _node)
        self.assertEqual(tree.root.node_id, 0)
        self.assertEqual(tree.active_node, _node)

    def test_order_node_ids__full_tree(self):
        tree = GenericTree()
        _nodes, _n_nodes = self.create_node_tree(depth=3, width=2)
        tree.register_node(_nodes[0][0])
        _new_node_ids = []
        _new_nodes = {}
        for _id, _node in tree.nodes.items():
            _new_id = 2 * _id + 67
            _node.node_id = _new_id
            _new_nodes[_new_id] = _node
            _new_node_ids.append(_new_id)
        tree.node_ids = _new_node_ids
        tree.nodes = _new_nodes
        tree.active_node_id = _new_node_ids[len(_new_node_ids) // 2]
        _active_node = tree.active_node
        tree.order_node_ids()
        for _num, _ in enumerate(tree.node_ids):
            self.assertTrue(_num in tree.node_ids)
        self.assertEqual(tree.get_new_nodeid(), len(tree.node_ids))
        self.assertEqual(tree.active_node, _active_node)

    def test_copy__copy_full_tree(self):
        _depth = 3
        _width = 4
        tree = GenericTree()
        _nodes, _n_nodes = self.create_node_tree(depth=_depth, width=_width)
        tree.register_node(_nodes[0][0])
        _copy = copy(tree)
        for _node in tree.nodes.values():
            self.assertFalse(_node in _copy.nodes.values())
        for _node in _copy.root._children:
            self.assertTrue(_node in _copy.nodes.values())
        for key in set(tree.__dict__.keys()) - {"root", "nodes", "_starthash"}:
            self.assertEqual(getattr(tree, key), getattr(_copy, key))

    def test_copy(self):
        _depth = 3
        _width = 4
        tree = GenericTree()
        _nodes, _n_nodes = self.create_node_tree(depth=_depth, width=_width)
        tree.register_node(_nodes[0][0])
        _copy = tree.copy()
        for _node in tree.nodes.values():
            self.assertFalse(_node in _copy.nodes.values())

    def test_copy__no_nodes(self):
        tree = GenericTree()
        tree.dummy = 1234.522
        _copy = tree.copy()
        self.assertIsInstance(_copy, GenericTree)
        self.assertEqual(tree.dummy, _copy.dummy)

    def test_hash___empty_tree(self):
        tree = GenericTree()
        self.assertIsInstance(hash(tree), int)

    def test_hash___simple_tree(self):
        tree = GenericTree()
        tree2 = GenericTree()
        self.assertNotEqual(hash(tree), hash(tree2))

    def test_hash___full_tree(self):
        _depth = 3
        _width = 4
        tree = GenericTree()
        tree2 = GenericTree()
        _nodes, _n_nodes = self.create_node_tree(depth=_depth, width=_width)
        tree.register_node(_nodes[0][0])
        tree2.register_node(_nodes[0][0].copy())
        self.assertNotEqual(hash(tree), hash(tree2))


if __name__ == "__main__":
    unittest.main()

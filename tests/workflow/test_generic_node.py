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


import copy
import unittest
from unittest import mock

import numpy as np

from pydidas.core import UserConfigError
from pydidas.workflow import GenericNode


class TestGenericNode(unittest.TestCase):
    def setUp(self):
        ...

    def tearDown(self):
        ...

    def create_node_tree(self, depth=3, width=3):
        obj00 = GenericNode(node_id=0)
        _nodes = [[obj00]]
        _target_conns = []
        _index = 1
        for _depth in range(depth):
            _tiernodes = []
            for _parent in _nodes[_depth]:
                for _ichild in range(width):
                    _node = GenericNode(node_id=_index)
                    _parent.add_child(_node)
                    _index += 1
                    _target_conns.append([_parent.node_id, _node.node_id])
                    _tiernodes.append(_node)
            _nodes.append(_tiernodes)
        return _nodes, _target_conns, _index

    def test_node_id_property__get(self):
        obj = GenericNode()
        self.assertIsNone(obj.node_id)

    def test_node_id_property__get_int(self):
        _id = 12
        obj = GenericNode(node_id=_id)
        self.assertEqual(obj.node_id, _id)

    def test_node_id_property__set_int(self):
        _id = 12
        obj = GenericNode()
        obj.node_id = _id
        self.assertEqual(obj._node_id, _id)

    def test_parent_id_property__get_None(self):
        obj = GenericNode()
        self.assertIsNone(obj.parent_id)

    def test_parent_id_property__get_int(self):
        _parent = GenericNode()
        obj = GenericNode(parent=_parent)
        self.assertEqual(obj.parent_id, _parent.node_id)

    def test_node_id_property__set_None(self):
        obj = GenericNode()
        obj.node_id = None
        self.assertIsNone(obj._node_id)

    def test_node_id_property__set_wrong_type(self):
        obj = GenericNode()
        with self.assertRaises(TypeError):
            obj.node_id = [1, 2]

    def test_verify_type__with_node(self):
        obj = GenericNode()
        node2 = GenericNode()
        obj._verify_type(node2)

    def test_verify_type__allowNone_with_node(self):
        obj = GenericNode()
        node2 = GenericNode()
        obj._verify_type(node2, allowNone=True)

    def test_verify_type__allowNone_with_None(self):
        obj = GenericNode()
        obj._verify_type(None, allowNone=True)

    def test_verify_type__with_None(self):
        obj = GenericNode()
        with self.assertRaises(TypeError):
            obj._verify_type(None)

    def test_verify_type__with_wrong_type(self):
        obj = GenericNode()
        with self.assertRaises(TypeError):
            obj._verify_type(12)

    def test_init__plain(self):
        obj = GenericNode()
        self.assertIsInstance(obj, GenericNode)

    def test_init__with_parent(self):
        _parent = GenericNode()
        obj = GenericNode(parent=_parent)
        self.assertEqual(obj.parent, _parent)

    def test_init__with_parent_wrong_type(self):
        _parent = "Something"
        with self.assertRaises(TypeError):
            GenericNode(parent=_parent)

    def test_init__with_random_key(self):
        _testval = 1.23
        obj = GenericNode(testkey=_testval)
        self.assertTrue(hasattr(obj, "testkey"))
        self.assertEqual(obj.testkey, _testval)

    def test_init__with_parent_and_key(self):
        _parent = GenericNode()
        _testval = 1.23
        obj = GenericNode(parent=_parent, testkey=_testval, testkey2=_testval + 1)
        self.assertEqual(obj._parent, _parent)

    def test_is_leaf__no_children(self):
        obj = GenericNode()
        self.assertTrue(obj.is_leaf)

    def test_is_leaf__children(self):
        obj = GenericNode()
        obj._children = [1, 2, 3]
        self.assertFalse(obj.is_leaf)

    def test_n_children__empty(self):
        obj = GenericNode()
        self.assertEqual(obj.n_children, 0)

    def test_n_children__not_empty(self):
        _children = [1, 2, 3]
        obj = GenericNode()
        obj._children = _children
        self.assertEqual(obj.n_children, len(_children))

    def test_get_children(self):
        _children = [1, 2, 3]
        obj = GenericNode()
        obj._children = _children
        self.assertEqual(obj.get_children(), _children)

    def test_set_parent(self):
        _parent = GenericNode()
        obj = GenericNode()
        obj.parent = _parent
        self.assertEqual(obj.parent, _parent)

    def test_set_parent__none(self):
        _parent = GenericNode()
        obj = GenericNode(parent=_parent)
        obj.parent = None
        self.assertIsNone(obj.parent)
        self.assertFalse(obj in _parent._children)

    def test_set_parent__with_old_parent(self):
        _parent = GenericNode()
        obj = GenericNode(parent=_parent)
        self.assertEqual(obj.parent, _parent)
        _newparent = GenericNode()
        obj.parent = _newparent
        self.assertEqual(obj.parent, _newparent)
        self.assertFalse(obj in _parent._children)

    def test_get_recursive_connections(self):
        _nodes, _target_conns, _n_nodes = self.create_node_tree()
        root = _nodes[0][0]
        _conns = root.get_recursive_connections()
        for _conn in _conns:
            self.assertTrue(_conn in _target_conns)

    def test_get_recursive_connections__no_children(self):
        root = GenericNode()
        _conns = root.get_recursive_connections()
        self.assertEqual(_conns, [])

    def test_get_recursive_ids(self):
        _nodes, _target_conns, _n_nodes = self.create_node_tree()
        root = _nodes[0][0]
        _ids = root.get_recursive_ids()
        self.assertEqual(set(_ids), set(np.arange(_n_nodes)))

    def test_get_recursive_ids__no_children(self):
        root = GenericNode(node_id=0)
        _ids = root.get_recursive_ids()
        self.assertEqual(_ids, [0])

    def test_delete_node_references__no_children_not_recursive(self):
        root = GenericNode(node_id=0)
        node = GenericNode(node_id=1, parent=root)
        node.delete_node_references()
        self.assertFalse(node in root._children)

    def test_delete_node_references__only_self(self):
        root = GenericNode(node_id=0)
        root.delete_node_references()

    def test_delete_node_references__no_children_recursive(self):
        root = GenericNode(node_id=0)
        node = GenericNode(node_id=1, parent=root)
        node.delete_node_references(recursive=True)
        self.assertFalse(node in root._children)

    def test_delete_node_references__with_children_not_recursive(self):
        _nodes, _target_conns, _n_nodes = self.create_node_tree(3, 1)
        with self.assertRaises(RecursionError):
            _nodes[1][0].delete_node_references(recursive=False)

    def test_delete_node_references__with_children_recursive(self):
        _nodes, _target_conns, _n_nodes = self.create_node_tree(3, 1)
        _root = _nodes[0][0]
        _nodes[1][0].delete_node_references(recursive=True)
        self.assertFalse(_nodes[1][0] in _root._children)
        self.assertEqual(_nodes[1][0].n_children, 0)

    def test_connect_parent_to_children__no_parent_no_children(self):
        root = GenericNode(node_id=0)
        root._parent = mock.MagicMock()
        root.connect_parent_to_children()
        self.assertIsNone(root.parent)

    def test_connect_parent_to_children__no_parent(self):
        root = GenericNode(node_id=0)
        _child = GenericNode(node_id=1, parent=root)
        root.connect_parent_to_children()
        self.assertIsNone(_child.parent)
        self.assertEqual(root.get_children(), [])

    def test_connect_parent_to_children__no_parent_multie_children(self):
        root = GenericNode(node_id=0)
        _ = GenericNode(node_id=1, parent=root)
        _ = GenericNode(node_id=2, parent=root)
        with self.assertRaises(UserConfigError):
            root.connect_parent_to_children()

    def test_connect_parent_to_children__no_children(self):
        root = GenericNode(node_id=0)
        node = GenericNode(node_id=1, parent=root)
        node.connect_parent_to_children()
        self.assertFalse(node in root._children)

    def test_connect_parent_to_children__full_connection(self):
        root = GenericNode(node_id=0)
        node = GenericNode(node_id=1, parent=root)
        subnode1 = GenericNode(node_id=2, parent=node)
        subnode2 = GenericNode(node_id=3, parent=node)
        node.connect_parent_to_children()
        self.assertNotIn(node, root._children)
        self.assertEqual(node._children, [])
        self.assertIsNone(node.parent)
        for _node in [subnode1, subnode2]:
            self.assertIn(_node, root._children)
            self.assertEqual(_node.parent, root)

    def test_remove_child_reference__wrong_child(self):
        root = GenericNode(node_id=0)
        node = GenericNode(node_id=1)
        with self.assertRaises(ValueError):
            root.remove_child_reference(node)

    def test_remove_child_reference__child(self):
        root = GenericNode(node_id=0)
        node = GenericNode(node_id=1, parent=root)
        node2 = GenericNode(node_id=2, parent=root)
        root.remove_child_reference(node)
        self.assertTrue(node2 in root._children)
        self.assertFalse(node in root._children)

    def test_change_node_parent__same_parent(self):
        _nodes, _, _ = self.create_node_tree(depth=3, width=2)
        _root = _nodes[0][0]
        _child = _root.get_children()[0]
        _child.change_node_parent(_root)
        self.assertEqual(_child.parent, _root)
        self.assertTrue(_child in _root.get_children())

    def test_change_node_parent__self_parent(self):
        _nodes, _, _ = self.create_node_tree(depth=3, width=2)
        _root = _nodes[0][0]
        _child = _root.get_children()[0]
        _child.change_node_parent(_child)
        self.assertEqual(_child.parent, _root)
        self.assertTrue(_child in _root.get_children())

    def test_change_node_parent__new_parent_in_children(self):
        _nodes, _, _ = self.create_node_tree(depth=3, width=2)
        _root = _nodes[0][0]
        _child = _root.get_children()[0]
        _grandchild = _child.get_children()[0]
        with self.assertRaises(UserConfigError):
            _child.change_node_parent(_grandchild)

    def test_change_node_parent__simple_case(self):
        _nodes, _, _ = self.create_node_tree(depth=3, width=2)
        _root = _nodes[0][0]
        _child1 = _root.get_children()[0]
        _child2 = _root.get_children()[1]
        _child1.change_node_parent(_child2)
        self.assertEqual(_child1.parent, _child2)
        self.assertTrue(_child1 in _child2.get_children())
        self.assertFalse(_child1 in _root.get_children())

    def test_copy(self):
        root = GenericNode(node_id=0)
        GenericNode(node_id=1, parent=root)
        GenericNode(node_id=2, parent=root)
        root_copy = copy.copy(root)
        self.assertNotEqual(root, root_copy)
        self.assertNotEqual(root._children, root_copy._children)

    def test_copy__with_parent(self):
        root = GenericNode(node_id=0)
        node = GenericNode(node_id=1, parent=root)
        GenericNode(node_id=2, parent=root)
        node3 = GenericNode(node_id=2, parent=node)
        node_copy = copy.copy(node)
        self.assertNotEqual(node, node_copy)
        self.assertEqual(node._parent, node_copy._parent)
        self.assertFalse(node3 in node_copy._children)

    def test_hash__simple_node(self):
        node = GenericNode(node_id=0)
        node2 = GenericNode(node_id=0)
        self.assertEqual(hash(node), hash(node2))

    def test_hash__w_child(self):
        node = GenericNode(node_id=0)
        GenericNode(node_id=1, parent=node)
        node2 = GenericNode(node_id=0)
        self.assertNotEqual(hash(node), hash(node2))

    def test_hash__w_parent(self):
        node = GenericNode(node_id=1, parent=GenericNode(node_id=0))
        node2 = GenericNode(node_id=0)
        self.assertNotEqual(hash(node), hash(node2))


if __name__ == "__main__":
    unittest.main()

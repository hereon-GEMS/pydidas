# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Unit tests for pydidas modules."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import unittest

from pydidas.workflow_tree import GenericTree, GenericNode


class TestGenericTree(unittest.TestCase):

    def setUp(self):
        ...

    def tearDown(self):
        ...

    def create_node_tree(self, depth=3, width=3):
        root = GenericNode(node_id=0)
        _nodes =  [[root]]
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
        _val2 = 'something'
        tree = GenericTree(test1=_val1, test2=_val2)
        self.assertEqual(tree._config['test1'], _val1)
        self.assertEqual(tree._config['test2'], _val2)

    def test_clear(self):
        tree = GenericTree()
        tree.nodes = dict(a=1, b='c')
        tree.node_ids = [0, 1]
        tree.root = 12
        tree.clear()
        self.assertEqual(tree.nodes, {})
        self.assertEqual(tree.node_ids, [])
        self.assertIsNone(tree.root)

    def testverify_node_type__with_node(self):
        tree = GenericTree()
        node = GenericNode()
        tree.verify_node_type(node)

    def testverify_node_type__wrong_object(self):
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
        tree.node_ids = [_id -1,_id]
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

    def test_register_node__with_new_nodeid(self):
        tree = GenericTree()
        node = GenericNode()
        tree.register_node(node, node_id=3)
        self.assertTrue(node in tree.nodes.values())

    def test_register_node__node_tree_with_new_nodeid(self):
        tree = GenericTree()
        node = GenericNode()
        node2 = GenericNode(parent=node)
        node3 = GenericNode(parent=node2)
        tree.register_node(node, node_id=3)
        for _node in [node, node2, node3]:
            self.assertTrue(_node in tree.nodes.values())

    def test_register_node__node_tree_with_existing_nodeids(self):
        tree = GenericTree()
        node = GenericNode(node_id=3)
        node2 = GenericNode(parent=node)
        node3 = GenericNode(parent=node2)
        tree.register_node(node, node_id=3)
        for _node in [node, node2, node3]:
            self.assertTrue(_node in tree.nodes.values())
        tree = GenericTree()
        node = GenericNode(node_id=7)
        node2 = GenericNode(parent=node, node_id=6)

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

    def test__copy__(self):
        _depth = 3
        _width = 4
        tree = GenericTree()
        _nodes, _n_nodes = self.create_node_tree(depth=_depth, width=_width)
        tree.register_node(_nodes[0][0])
        _copy = tree.__copy__()
        for _node in tree.nodes.values():
            self.assertFalse(_node in _copy.nodes.values())
        for _node in _copy.root._children:
            self.assertTrue(_node in _copy.nodes.values())
        for key in set(tree.__dict__.keys()) - {'root', 'nodes'}:
            self.assertEqual(getattr(tree, key), getattr(_copy, key))

    def test_get_copy(self):
        _depth = 3
        _width = 4
        tree = GenericTree()
        _nodes, _n_nodes = self.create_node_tree(depth=_depth, width=_width)
        tree.register_node(_nodes[0][0])
        _copy = tree.get_copy()
        for _node in tree.nodes.values():
            self.assertFalse(_node in _copy.nodes.values())


if __name__ == '__main__':
    unittest.main()

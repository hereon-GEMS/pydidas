# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""Unit tests for pydidas modules."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import unittest
import random
import copy

import numpy as np

from pydidas.workflow_tree import WorkflowNode, WorkflowTree, GenericNode
from _plugins.dummy_loader import DummyLoader
from _plugins.dummy_proc import DummyProc

class TestWorkflowTree(unittest.TestCase):

    def setUp(self):
        self.tree = WorkflowTree()
        self.tree.clear()

    def tearDown(self):
        ...

    def create_node_tree(self, depth=3, width=3):
        obj00 = WorkflowNode(node_id=0, plugin=DummyLoader())
        _nodes =  [[obj00]]
        _index = 1
        for _depth in range(depth):
            _tiernodes = []
            for _parent in _nodes[_depth]:
                for _ichild in range(width):
                    _node = WorkflowNode(node_id=_index, plugin=DummyProc())
                    _parent.add_child(_node)
                    _index += 1
                    _tiernodes.append(_node)
            _nodes.append(_tiernodes)
        return _nodes, _index

    def test_create_and_add_node__wrong_plugin(self):
        with self.assertRaises(TypeError):
            self.tree.create_and_add_node(12)

    def test_create_and_add_node__empty_tree(self):
        self.tree.create_and_add_node(DummyLoader())
        self.assertEqual(len(self.tree.nodes), 1)
        self.assertIsInstance(self.tree.nodes[0], GenericNode)

    def test_create_and_add_node__in_tree_no_parent(self):
        self.tree.create_and_add_node(DummyLoader())
        self.tree.create_and_add_node(DummyProc())
        self.assertEqual(len(self.tree.nodes), 2)
        self.assertIsInstance(self.tree.nodes[1], GenericNode)
        self.assertEqual(self.tree.nodes[0].n_children, 1)

    def test_create_and_add_node__in_tree_with_parent(self):
        self.tree.create_and_add_node(DummyLoader())
        self.tree.create_and_add_node(DummyProc())
        self.tree.create_and_add_node(DummyProc(), parent=self.tree.nodes[0])
        self.assertEqual(len(self.tree.nodes), 3)
        self.assertIsInstance(self.tree.nodes[2], GenericNode)
        self.assertEqual(self.tree.nodes[0].n_children, 2)

    def test_create_and_add_node__in_tree_with_node_id(self):
        _id = 42
        self.tree.create_and_add_node(DummyLoader())
        self.tree.create_and_add_node(DummyProc())
        self.tree.create_and_add_node(DummyProc(), node_id=_id)
        self.assertEqual(len(self.tree.nodes), 3)
        self.assertIsInstance(self.tree.nodes[_id], GenericNode)
        self.assertEqual(self.tree.nodes[_id].node_id, _id)

    def test_execute_process(self):
        _depth = 3
        nodes, n_nodes = self.create_node_tree(depth=_depth)
        self.tree.register_node(nodes[0][0])
        self.tree.execute_process(0)
        for _node in nodes[_depth]:
            self.assertTrue(hasattr(_node, 'results'))
            self.assertTrue(hasattr(_node, 'result_kws'))
        for _d in range(_depth):
            for _node in nodes[_d]:
                self.assertFalse(hasattr(_node, 'results'))
                self.assertFalse(hasattr(_node, 'result_kws'))


if __name__ == '__main__':
    unittest.main()

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

import numpy as np

from pydidas.workflow import PluginPositionNode, GenericNode


class TestPluginPositionNode(unittest.TestCase):
    def setUp(self):
        ...

    def tearDown(self):
        ...

    def create_node_tree(self, depth=3, width=3):
        root = PluginPositionNode(node_id=0)
        _nodes = [[root]]
        _index = 1
        for _depth in range(depth):
            _tiernodes = []
            for _parent in _nodes[_depth]:
                for _ichild in range(width):
                    _node = PluginPositionNode(node_id=_index)
                    _parent.add_child(_node)
                    _index += 1
                    _tiernodes.append(_node)
            _nodes.append(_tiernodes)
        return _nodes, _index

    def get_pos_in_tree(self, index, width, depth):
        _num_per_row = width ** np.arange(depth + 1)
        _row_limits = np.concatenate((np.array((0,)), np.cumsum(_num_per_row)))
        _ntotal = _row_limits[-1]
        _row_of_index = np.zeros((_ntotal), dtype=np.int16)
        _pos_in_row_of_index = np.zeros((_ntotal), dtype=np.int16)
        for _row in range(depth + 1):
            _row_of_index[_row_limits[_row] : _row_limits[_row + 1]] = _row
        _pos_in_row_of_index = np.arange(_ntotal) - _row_limits[_row_of_index]
        return (_row_of_index[index], _pos_in_row_of_index[index])

    def test_init__plain(self):
        root = PluginPositionNode()
        self.assertIsInstance(root, PluginPositionNode)

    def test_init__with_parent(self):
        _parent = GenericNode()
        root = PluginPositionNode(parent=_parent, testkey=1)
        self.assertEqual(root._parent, _parent)

    def test_init__with_random_key(self):
        _testval = 1.23
        root = PluginPositionNode(testkey=_testval)
        self.assertTrue(hasattr(root, "testkey"))
        self.assertEqual(root.testkey, _testval)

    def test_width__no_children(self):
        root = PluginPositionNode()
        self.assertEqual(root.width, 1)

    def test_width__children_no_tree(self):
        root = PluginPositionNode()
        PluginPositionNode(parent=root)
        PluginPositionNode(parent=root)
        self.assertEqual(root.width, 2 * 1 + PluginPositionNode.PLUGIN_WIDTH_OFFSET)

    def test_width__children_tree(self):
        _depth = 3
        _width = 3
        _nodes, _n_nodes = self.create_node_tree(_depth, _width)
        _root = _nodes[0][0]
        _target = _width**_depth * 1 + PluginPositionNode.PLUGIN_WIDTH_OFFSET * (
            _width**_depth - 1
        )
        self.assertEqual(_root.width, _target)

    def test_height__no_children(self):
        root = PluginPositionNode()
        self.assertEqual(root.height, 1)

    def test_height__children_no_tree(self):
        root = PluginPositionNode()
        PluginPositionNode(parent=root)
        PluginPositionNode(parent=root)
        self.assertEqual(root.height, 2 * 1 + PluginPositionNode.PLUGIN_HEIGHT_OFFSET)

    def test_height__children_tree(self):
        _childdepth = 3
        _nodes, _n_nodes = self.create_node_tree(_childdepth)
        _root = _nodes[0][0]
        _target = (
            _childdepth + 1
        ) * 1 + PluginPositionNode.PLUGIN_HEIGHT_OFFSET * _childdepth
        self.assertAlmostEqual(_root.height, _target, 4)

    def test_get_relative_positions__no_children(self):
        root = PluginPositionNode(node_id=0)
        _pos = root.get_relative_positions()
        self.assertEqual(_pos[0], [0, 0])

    def test_get_relative_positions__with_linear_children(self):
        _childdepth = 3
        _width = 1
        _nodes, _n_nodes = self.create_node_tree(_childdepth, _width)
        root = _nodes[0][0]
        _pos = root.get_relative_positions()
        for _node_id in range(_childdepth + 1):
            _ypos = np.round(
                _node_id * (1 + PluginPositionNode.PLUGIN_HEIGHT_OFFSET), 3
            )
            self.assertEqual(_pos[_node_id], [0, _ypos])

    def test_get_relative_positions__with_tree_children(self):
        def row_width(n):
            return n * 1 + (n - 1) * PluginPositionNode.PLUGIN_WIDTH_OFFSET

        _childdepth = 3
        _width = 2
        _nodes, _n_nodes = self.create_node_tree(_childdepth, _width)
        root = _nodes[0][0]
        _pos = root.get_relative_positions()
        _num_per_row = _width ** np.arange(_childdepth + 1)
        _row_limits = np.concatenate((np.array((0,)), np.cumsum(_num_per_row)))
        _ntotal = _row_limits[-1]
        for _node_id in range(_ntotal):
            iy, ix = self.get_pos_in_tree(_node_id, _width, _childdepth)
            _ypos = np.round(iy * (1 + PluginPositionNode.PLUGIN_HEIGHT_OFFSET), 3)
            _deltax = (row_width(_width**_childdepth) - row_width(_width ** (iy))) / 2
            _xpos = np.round(
                _deltax + ix * (1 + PluginPositionNode.PLUGIN_WIDTH_OFFSET), 3
            )
            if iy in [0, _childdepth]:
                self.assertEqual(_pos[_node_id], [_xpos, _ypos])


if __name__ == "__main__":
    unittest.main()

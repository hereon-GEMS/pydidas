# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
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
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import unittest

import numpy as np

from pydidas.core.constants import gui_constants
from pydidas.workflow import PluginPositionNode, GenericNode


generic_width = gui_constants.GENERIC_PLUGIN_WIDGET_WIDTH
generic_height = gui_constants.GENERIC_PLUGIN_WIDGET_HEIGHT
child_spacing_y = gui_constants.GENERIC_PLUGIN_WIDGET_Y_OFFSET
child_spacing_x = gui_constants.GENERIC_PLUGIN_WIDGET_X_OFFSET


class TestPluginPositionNode(unittest.TestCase):

    def setUp(self):
        ...

    def tearDown(self):
        ...

    def create_node_tree(self, depth=3, width=3):
        root = PluginPositionNode(node_id=0)
        _nodes =  [[root]]
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
            _row_of_index[_row_limits[_row]:_row_limits[_row + 1]] = _row
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
        self.assertTrue(hasattr(root, 'testkey'))
        self.assertEqual(root.testkey, _testval)

    def test_width__no_children(self):
        root = PluginPositionNode()
        self.assertEqual(root.width, generic_width)

    def test_width__children_no_tree(self):
        root = PluginPositionNode()
        PluginPositionNode(parent=root)
        PluginPositionNode(parent=root)
        self.assertEqual(root.width, 2 * generic_width + child_spacing_x)

    def test_width__children_tree(self):
        _depth = 3
        _width = 3
        _nodes, _n_nodes = self.create_node_tree(_depth, _width)
        _root = _nodes[0][0]
        _target = (_width ** _depth * generic_width
                   + child_spacing_x * (_width ** _depth - 1))
        self.assertEqual(_root.width, _target)

    def test_height__no_children(self):
        root = PluginPositionNode()
        self.assertEqual(root.height, generic_height)

    def test_height__children_no_tree(self):
        root = PluginPositionNode()
        PluginPositionNode(parent=root)
        PluginPositionNode(parent=root)
        self.assertEqual(root.height, 2 * generic_height + child_spacing_y)

    def test_height__children_tree(self):
        _childdepth = 3
        _nodes, _n_nodes = self.create_node_tree(_childdepth)
        _root = _nodes[0][0]
        _target = ((_childdepth + 1 ) * generic_height
                   + child_spacing_y * _childdepth)
        self.assertEqual(_root.height, _target)

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
            _ypos = _node_id * (generic_height + child_spacing_y)
            self.assertEqual(_pos[_node_id], [0, _ypos])

    def test_get_relative_positions__with_tree_children(self):
        _childdepth = 3
        _width = 2
        _nodes, _n_nodes = self.create_node_tree(_childdepth, _width)
        root = _nodes[0][0]
        _pos = root.get_relative_positions()
        _num_per_row = _width ** np.arange(_childdepth + 1)
        _row_limits = np.concatenate((np.array((0,)), np.cumsum(_num_per_row)))
        _ntotal = _row_limits[-1]
        row_width = lambda n: n * generic_width + (n - 1) * child_spacing_x
        for _node_id in range(_ntotal):
            iy, ix = self.get_pos_in_tree(_node_id, _width, _childdepth)
            _ypos = iy  * (generic_height + child_spacing_y)
            _deltax = (row_width(_width ** _childdepth)
                       - row_width(_width ** (iy))) // 2
            _xpos = _deltax + ix * (generic_width + child_spacing_x)
            if iy in [0, _childdepth]:
                self.assertEqual(_pos[_node_id], [_xpos, _ypos])

    def test_make_grid_positions_positive__all_positive_pos(self):
        _nodes, _n_nodes = self.create_node_tree(3, 3)
        root = _nodes[0][0]
        _pos = root.get_relative_positions()
        _newpos = _pos.copy()
        root.make_grid_positions_positive(_newpos)
        self.assertEqual(_pos, _newpos)

    def test_make_grid_positions_positive__with_negative_pos(self):
        _nodes, _n_nodes = self.create_node_tree(3, 3)
        root = _nodes[0][0]
        _pos = root.get_relative_positions()
        _newpos = {}
        for key, val in _pos.items():
            _newpos[key] = (val[0] - 123, val[1] - 5678)
        root.make_grid_positions_positive(_newpos)
        self.assertEqual(_pos, _newpos)

    def test_make_grid_positions_positive__with_positive_offset(self):
        _nodes, _n_nodes = self.create_node_tree(3, 3)
        root = _nodes[0][0]
        _pos = root.get_relative_positions()
        _newpos = {}
        for key, val in _pos.items():
            _newpos[key] = (val[0] - 123, val[1] + 5678)
        root.make_grid_positions_positive(_newpos)
        self.assertEqual(_pos, _newpos)


if __name__ == '__main__':
    unittest.main()

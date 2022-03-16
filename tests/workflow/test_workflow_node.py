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
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import unittest

from pydidas.workflow import WorkflowNode
from pydidas.unittest_objects import DummyLoader, DummyProc


class TestWorkflowNode(unittest.TestCase):

    def setUp(self):
        ...

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

    def test_node_id_property__get(self):
        obj = WorkflowNode(plugin=DummyLoader())
        self.assertIsNone(obj.node_id)

    def test_node_id_property__get_int(self):
        _id = 12
        obj = WorkflowNode(plugin=DummyLoader(), node_id=_id)
        self.assertEqual(obj.node_id, _id)

    def test_node_id_property__set_int(self):
        _id = 12
        obj = WorkflowNode(plugin=DummyLoader())
        obj.node_id = _id
        self.assertEqual(obj._node_id, _id)
        self.assertEqual(obj.plugin.node_id, _id)

    def test_result_shape__not_set(self):
        obj = WorkflowNode(plugin=DummyLoader())
        self.assertIsNone(obj.result_shape)

    def test_result_shape(self):
        obj = WorkflowNode(plugin=DummyLoader())
        obj.update_plugin_result_data_shape()
        _shape = obj.result_shape
        self.assertEqual(_shape, obj.plugin.result_shape)

    def test_update_plugin_result_data_shape(self):
        _shape = (-1, 12, 42)
        obj = WorkflowNode(plugin=DummyProc())
        obj.plugin._config['input_shape'] = _shape
        obj.update_plugin_result_data_shape()
        self.assertEqual(obj.result_shape, _shape)

    def test_propagate_shapes_and_global_config(self):
        _depth = 3
        nodes, n_nodes = self.create_node_tree(depth=_depth)
        obj = nodes[0][0]
        obj.propagate_shapes_and_global_config()
        _shape = obj.result_shape
        for _d in range(_depth):
            for _node in nodes[_d]:
                self.assertEqual(_node.result_shape, _shape)

    def test_dump(self):
        obj = WorkflowNode(plugin=DummyLoader())
        _dump = obj.dump()
        self.assertIsInstance(_dump, dict)
        for key in ('node_id', 'parent', 'children', 'plugin_class',
                    'plugin_params'):
            self.assertTrue(key in _dump.keys())

    def test_execute_plugin_chain(self):
        _depth = 3
        nodes, n_nodes = self.create_node_tree(depth=_depth)
        obj = nodes[0][0]
        obj.execute_plugin_chain(0)
        for _node in nodes[_depth]:
            self.assertIsNotNone(_node.results)
            self.assertIsNotNone(_node.result_kws)
        for _d in range(_depth):
            for _node in nodes[_d]:
                self.assertIsNone(_node.results)
                self.assertIsNone(_node.result_kws)

    def test_execute_plugin_chain__with_force_store(self):
        _depth = 3
        nodes, n_nodes = self.create_node_tree(depth=_depth)
        obj = nodes[0][0]
        obj.execute_plugin_chain(0, force_store_results=True)
        for _d in range(_depth + 1):
            for _node in nodes[_d]:
                self.assertIsNotNone(_node.results)
                self.assertIsNotNone(_node.result_kws)

    def test_execute_plugin__simple(self):
        obj = WorkflowNode(plugin=DummyLoader())
        _res = obj.execute_plugin(0)
        self.assertIsInstance(_res[1], dict)

    def test_execute_plugin__single_in_tree(self):
        nodes, n_nodes = self.create_node_tree()
        obj = nodes[1][1]
        _res = obj.execute_plugin(0)
        self.assertIsInstance(_res[1], dict)

    def test_prepare_execution(self):
        _depth = 3
        nodes, n_nodes = self.create_node_tree(depth=_depth)
        obj = nodes[0][0]
        obj.prepare_execution()
        for _d in range(_depth + 1):
            for _node in nodes[_d]:
                self.assertTrue(_node.plugin._preexecuted)

    def test_confirm_plugin_existance_and_type__no_plugin(self):
        with self.assertRaises(KeyError):
            WorkflowNode()

    def test_confirm_plugin_existance_and_type__wrong_plugin(self):
        with self.assertRaises(TypeError):
            WorkflowNode(plugin=12)

    def test_confirm_plugin_existance_and_type__correct_plugin(self):
        obj = WorkflowNode(plugin=DummyLoader())
        self.assertIsInstance(obj, WorkflowNode)

    def test_hash__simple(self):
        obj = WorkflowNode(plugin=DummyLoader(), node_id=0)
        self.assertIsInstance(hash(obj), int)

    def test_hash__simple_comparison(self):
        obj = WorkflowNode(plugin=DummyLoader(), node_id=0)
        obj2 = WorkflowNode(plugin=DummyLoader(), node_id=0)
        self.assertEqual(hash(obj), hash(obj2))

    def test_hash__complex_comparison(self):
        _parent = WorkflowNode(plugin=DummyLoader(), node_id=0)
        obj = WorkflowNode(plugin=DummyProc(), node_id=1, parent=_parent)
        obj2 = WorkflowNode(plugin=DummyProc(), node_id=1, parent=_parent)
        self.assertEqual(hash(obj), hash(obj2))

    def test_hash__comparison_w_child(self):
        _parent = WorkflowNode(plugin=DummyLoader(), node_id=0)
        obj = WorkflowNode(plugin=DummyProc(), node_id=1, parent=_parent)
        obj2 = WorkflowNode(plugin=DummyProc(), node_id=1, parent=_parent)
        _ = WorkflowNode(plugin=DummyProc(), node_id=1, parent=obj)
        self.assertNotEqual(hash(obj), hash(obj2))

    def test_hash__comparison_w_different_node_id(self):
        _parent = WorkflowNode(plugin=DummyLoader(), node_id=0)
        obj = WorkflowNode(plugin=DummyProc(), node_id=1, parent=_parent)
        obj2 = WorkflowNode(plugin=DummyProc(), node_id=2, parent=_parent)
        self.assertNotEqual(hash(obj), hash(obj2))

    def test_hash__comparison_w_different_parent(self):
        _parent = WorkflowNode(plugin=DummyLoader(), node_id=0)
        _parent2 = WorkflowNode(plugin=DummyProc(), node_id=0)
        obj = WorkflowNode(plugin=DummyProc(), node_id=1, parent=_parent)
        obj2 = WorkflowNode(plugin=DummyProc(), node_id=1, parent=_parent2)
        self.assertNotEqual(hash(obj), hash(obj2))

    def test_hash__comparison_w_different_plugin(self):
        _parent = WorkflowNode(plugin=DummyLoader(), node_id=0)
        obj = WorkflowNode(plugin=DummyProc(), node_id=1, parent=_parent)
        obj2 = WorkflowNode(plugin=DummyLoader(), node_id=2, parent=_parent)
        self.assertNotEqual(hash(obj), hash(obj2))

    def test_hash__comparison_w_different_plugin_param(self):
        _parent = WorkflowNode(plugin=DummyLoader(), node_id=0)
        obj = WorkflowNode(plugin=DummyProc(), node_id=1, parent=_parent)
        obj.plugin.set_param_value('label', 'Test')
        obj2 = WorkflowNode(plugin=DummyProc(), node_id=2, parent=_parent)
        self.assertNotEqual(hash(obj), hash(obj2))


if __name__ == '__main__':
    unittest.main()

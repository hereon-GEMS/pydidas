# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import unittest

import numpy as np
from pydidas.contexts import DiffractionExperimentContext
from pydidas.unittest_objects import DummyLoader, DummyProc
from pydidas.workflow import WorkflowNode


EXP = DiffractionExperimentContext()


class TestWorkflowNode(unittest.TestCase):
    def setUp(self): ...

    def tearDown(self): ...

    def create_node_tree(self, depth=3, width=3):
        obj00 = WorkflowNode(node_id=0, plugin=DummyLoader())
        _nodes = [[obj00]]
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

    def test_init__plugin_node_id(self):
        _node_id = 42
        obj = WorkflowNode(plugin=DummyLoader(), node_id=_node_id)
        self.assertEqual(obj.plugin.node_id, _node_id)

    def test_copy(self):
        _node_id = 42
        obj = WorkflowNode(plugin=DummyLoader(), node_id=_node_id)
        obj.plugin.set_param_value("binning", 3)
        new = obj.copy()
        self.assertEqual(new.plugin.node_id, _node_id)
        self.assertEqual(obj.plugin.node_id, _node_id)

    def test_copy__with_EXP_property(self):
        _node_id = 42
        obj = WorkflowNode(plugin=DummyLoader(), node_id=_node_id)
        obj.plugin._EXP = EXP
        new = obj.copy()
        self.assertEqual(new.plugin.node_id, _node_id)
        self.assertEqual(obj.plugin.node_id, _node_id)
        self.assertEqual(obj.plugin._EXP, EXP)
        self.assertEqual(new.plugin._EXP, EXP)

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
        obj.plugin.set_param_value("keep_results", True)
        obj.execute_plugin(0)
        self.assertEqual(obj.result_shape, (10, 10))

    def test_dump(self):
        obj = WorkflowNode(plugin=DummyLoader())
        _dump = obj.dump()
        self.assertIsInstance(_dump, dict)
        for key in ("node_id", "parent", "children", "plugin_class", "plugin_params"):
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

    def test_execute_plugin_chain__with_store_input_data(self):
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

    def test_execute_plugin__array_input(self):
        _input = np.random.random((10, 10))
        obj = WorkflowNode(plugin=DummyProc())
        _res = obj.execute_plugin(_input)
        self.assertIsInstance(_res[0], np.ndarray)
        self.assertEqual(_input.shape, _res[0].shape)

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
                self.assertTrue(_node.plugin._pre_executed)

    def test_confirm_plugin_existance_and_type__no_plugin(self):
        with self.assertRaises(KeyError):
            WorkflowNode()

    def test_confirm_plugin_existance_and_type__wrong_plugin(self):
        with self.assertRaises(TypeError):
            WorkflowNode(plugin=12)

    def test_confirm_plugin_existance_and_type__correct_plugin(self):
        obj = WorkflowNode(plugin=DummyLoader())
        self.assertIsInstance(obj, WorkflowNode)

    def test_consistency_check__no_parent(self):
        obj = WorkflowNode(plugin=DummyLoader())
        self.assertTrue(obj.consistency_check())

    def test_consistency_check__parent_out_any(self):
        obj = WorkflowNode(plugin=DummyLoader())
        obj2 = WorkflowNode(plugin=DummyProc(), parent=obj)
        obj.plugin.output_data_dim = -1
        obj2.plugin.input_data_dim = 2
        self.assertTrue(obj2.consistency_check())

    def test_consistency_check__plugin_in_any(self):
        obj = WorkflowNode(plugin=DummyLoader())
        obj2 = WorkflowNode(plugin=DummyProc(), parent=obj)
        obj.plugin.input_data_dim = 2
        obj2.plugin.input_data_dim = -1
        self.assertTrue(obj2.consistency_check())

    def test_consistency_check__eq_dims(self):
        obj = WorkflowNode(plugin=DummyLoader())
        obj2 = WorkflowNode(plugin=DummyProc(), parent=obj)
        obj.plugin.input_data_dim = 2
        obj2.plugin.input_data_dim = 2
        self.assertTrue(obj2.consistency_check())

    def test_consistency_check__neq_dims(self):
        obj = WorkflowNode(plugin=DummyLoader())
        obj2 = WorkflowNode(plugin=DummyProc(), parent=obj)
        obj.plugin.input_data_dim = 2
        obj2.plugin.input_data_dim = 1
        self.assertFalse(obj2.consistency_check())

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
        obj.plugin.set_param_value("label", "Test")
        obj2 = WorkflowNode(plugin=DummyProc(), node_id=2, parent=_parent)
        self.assertNotEqual(hash(obj), hash(obj2))


if __name__ == "__main__":
    unittest.main()

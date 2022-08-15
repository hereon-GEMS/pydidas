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
__maintainer__ = "Malte Storm"
__status__ = "Development"


import unittest
import tempfile
import shutil
import os
import copy
import pickle

import numpy as np

from pydidas import unittest_objects
from pydidas.core import UserConfigError, Dataset
from pydidas.workflow import WorkflowNode, WorkflowTree, GenericNode
from pydidas.workflow.workflow_tree import _WorkflowTree
from pydidas.plugins import PluginCollection


COLL = PluginCollection()
_PLUGIN_PATHS = COLL.get_all_registered_paths()


class TestWorkflowTree(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        _path = os.path.dirname(unittest_objects.__file__)
        if _path not in _PLUGIN_PATHS:
            COLL.find_and_register_plugins(_path)

    def setUp(self):
        self.tree = WorkflowTree()
        self.tree.clear()
        self._tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self._tmpdir)
        # PluginCollection._reset_instance()

    @classmethod
    def tearDownClass(cls):
        COLL.clear_collection(True)
        COLL.find_and_register_plugins(*_PLUGIN_PATHS)

    def create_node_tree(self, depth=3, width=3):
        obj00 = WorkflowNode(node_id=0, plugin=unittest_objects.DummyLoader())
        _nodes = [[obj00]]
        _index = 1
        for _depth in range(depth):
            _tiernodes = []
            for _parent in _nodes[_depth]:
                for _ichild in range(width):
                    _node = WorkflowNode(
                        node_id=_index, plugin=unittest_objects.DummyProc()
                    )
                    _parent.add_child(_node)
                    _index += 1
                    _tiernodes.append(_node)
            _nodes.append(_tiernodes)
        return _nodes, _index

    def test_get_all_result_shapes__no_nodes(self):
        with self.assertRaises(UserConfigError):
            self.tree.get_all_result_shapes()

    def test_get_all_result_shapes__single_node(self):
        self.tree.create_and_add_node(unittest_objects.DummyLoader())
        _shapes = self.tree.get_all_result_shapes()
        _dummy = unittest_objects.DummyLoader()
        _dummy.calculate_result_shape()
        self.assertEqual(_shapes[0], _dummy.result_shape)

    def test_get_all_result_shapes__tree(self):
        _dummy = unittest_objects.DummyLoader()
        _dummy.calculate_result_shape()
        _shape = _dummy.result_shape
        self.tree.create_and_add_node(unittest_objects.DummyLoader())
        self.tree.create_and_add_node(
            unittest_objects.DummyProc(), parent=self.tree.root, node_id=2
        )
        self.tree.create_and_add_node(
            unittest_objects.DummyProc(), parent=self.tree.root, node_id=3
        )
        self.tree.prepare_execution()
        _shapes = self.tree.get_all_result_shapes()
        self.assertEqual(_shapes[2], _shape)
        self.assertEqual(_shapes[3], _shape)

    def test_get_all_result_shapes__tree_with_keep_results(self):
        _dummy = unittest_objects.DummyLoader()
        _dummy.calculate_result_shape()
        _shape = _dummy.result_shape
        self.tree.create_and_add_node(unittest_objects.DummyLoader())
        self.tree.create_and_add_node(unittest_objects.DummyProc())
        self.tree.create_and_add_node(unittest_objects.DummyProc())
        self.tree.nodes[1].plugin.set_param_value("keep_results", True)
        _shapes = self.tree.get_all_result_shapes()
        self.assertEqual(list(_shapes.keys()), [1, 2])
        self.assertEqual(_shapes[1], _shape)
        self.assertEqual(_shapes[2], _shape)

    def test_export_to_file(self):
        _fname = os.path.join(self._tmpdir, "export.yaml")
        _nodes, _index = self.create_node_tree()
        self.tree.register_node(_nodes[0][0])
        self.tree.export_to_file(_fname)
        with open(_fname, "r") as f:
            content = f.read()
        for node_id in self.tree.nodes:
            self.assertTrue(content.find(f"node_id: {node_id}") > 0)

    def test_import_from_file(self):
        tree = WorkflowTree()
        _nodes, _index = self.create_node_tree()
        tree.register_node(_nodes[0][0])
        _fname = os.path.join(self._tmpdir, "export.yaml")
        tree.export_to_file(_fname)
        self.tree.import_from_file(_fname)
        for node_id in tree.nodes:
            self.assertTrue(node_id in self.tree.nodes)
            self.assertEqual(
                tree.nodes[node_id].plugin.__class__,
                self.tree.nodes[node_id].plugin.__class__,
            )

    def test_execute_single_plugin__no_node(self):
        _depth = 3
        _data = np.random.random((20, 20))
        nodes, n_nodes = self.create_node_tree(depth=_depth)
        self.tree.register_node(nodes[0][0])
        with self.assertRaises(KeyError):
            self.tree.execute_single_plugin(114, _data)

    def test_execute_single_plugin__existing_node(self):
        _depth = 3
        _data = np.random.random((20, 20))
        _offset = 0.4
        nodes, n_nodes = self.create_node_tree(depth=_depth)
        self.tree.register_node(nodes[0][0])
        _newdata, kwargs = self.tree.execute_single_plugin(
            n_nodes - 2, _data, offset=_offset
        )
        self.assertTrue((abs(_newdata - _offset - _data) < 1e-15).all())

    def test_execute_process(self):
        _depth = 3
        nodes, n_nodes = self.create_node_tree(depth=_depth)
        self.tree.register_node(nodes[0][0])
        self.tree.execute_process(0)
        for _node in nodes[_depth]:
            self.assertIsNotNone(_node.results)
            self.assertIsNotNone(_node.result_kws)
            self.assertTrue(_node.plugin._executed)
        for _d in range(_depth):
            for _node in nodes[_d]:
                self.assertIsNone(_node.results)
                self.assertIsNone(_node.result_kws)

    def test_execute_process_and_get_results(self):
        _depth = 3
        nodes, n_nodes = self.create_node_tree(depth=_depth)
        self.tree.register_node(nodes[0][0])
        _res = self.tree.execute_process_and_get_results(0)
        for _leaf in self.tree.get_all_leaves():
            _id = _leaf.node_id
            self.assertIsInstance(_res[_id], Dataset)

    def test_execute_process_and_get_results__linear_w_keep_results(self):
        self.tree.create_and_add_node(unittest_objects.DummyLoader())
        self.tree.create_and_add_node(unittest_objects.DummyProc())
        self.tree.create_and_add_node(unittest_objects.DummyProc())
        self.tree.nodes[1].plugin.set_param_value("keep_results", True)
        _res = self.tree.execute_process_and_get_results(0)
        self.assertIsInstance(_res[1], Dataset)
        self.assertIsInstance(_res[2], Dataset)

    def test_prepare_execution(self):
        _depth = 3
        nodes, n_nodes = self.create_node_tree(depth=_depth)
        self.tree.register_node(nodes[0][0])
        self.tree.prepare_execution()
        for _node in nodes[_depth]:
            self.assertTrue(_node.plugin._preexecuted)

    def test_create_and_add_node__wrong_plugin(self):
        with self.assertRaises(TypeError):
            self.tree.create_and_add_node(12)

    def test_create_and_add_node__empty_tree(self):
        _node = self.tree.create_and_add_node(unittest_objects.DummyLoader())
        self.assertEqual(len(self.tree.nodes), 1)
        self.assertIsInstance(self.tree.nodes[0], GenericNode)
        self.assertEqual(_node, 0)

    def test_create_and_add_node__in_tree_no_parent(self):
        self.tree.create_and_add_node(unittest_objects.DummyLoader())
        _node = self.tree.create_and_add_node(unittest_objects.DummyProc())
        self.assertEqual(len(self.tree.nodes), 2)
        self.assertIsInstance(self.tree.nodes[1], GenericNode)
        self.assertEqual(self.tree.nodes[0].n_children, 1)
        self.assertEqual(_node, 1)

    def test_create_and_add_node__in_tree_with_parent(self):
        self.tree.create_and_add_node(unittest_objects.DummyLoader())
        self.tree.create_and_add_node(unittest_objects.DummyProc())
        self.tree.create_and_add_node(
            unittest_objects.DummyProc(), parent=self.tree.nodes[0]
        )
        self.assertEqual(len(self.tree.nodes), 3)
        self.assertIsInstance(self.tree.nodes[2], GenericNode)
        self.assertEqual(self.tree.nodes[0].n_children, 2)

    def test_create_and_add_node__with_int_parent(self):
        _node = self.tree.create_and_add_node(unittest_objects.DummyLoader())
        _node2 = self.tree.create_and_add_node(
            unittest_objects.DummyProc(), parent=_node
        )
        self.assertIsInstance(self.tree.nodes[1], GenericNode)
        self.assertEqual(self.tree.nodes[0].n_children, 1)
        self.assertEqual(_node, 0)
        self.assertEqual(_node2, 1)

    def test_create_and_add_node__in_tree_with_node_id(self):
        _id = 42
        self.tree.create_and_add_node(unittest_objects.DummyLoader())
        self.tree.create_and_add_node(unittest_objects.DummyProc())
        self.tree.create_and_add_node(unittest_objects.DummyProc(), node_id=_id)
        self.assertEqual(len(self.tree.nodes), 3)
        self.assertIsInstance(self.tree.nodes[_id], GenericNode)
        self.assertEqual(self.tree.nodes[_id].node_id, _id)

    def test_tree_copy_with_plugins(self):
        self.tree.create_and_add_node(unittest_objects.DummyLoader())
        self.tree.create_and_add_node(unittest_objects.DummyProc())
        self.tree.create_and_add_node(
            unittest_objects.DummyProc(), parent=self.tree.root
        )
        tree2 = copy.copy(self.tree)
        self.assertIsInstance(tree2, _WorkflowTree)
        for _node in tree2.nodes.values():
            self.assertIsInstance(_node, WorkflowNode)
        for _node in tree2.root._children:
            self.assertTrue(_node in tree2.nodes.values())
        for key in set(self.tree.__dict__.keys()) - {"root", "nodes"}:
            self.assertEqual(getattr(self.tree, key), getattr(tree2, key))

    def test_tree_pickling(self):
        self.tree.create_and_add_node(unittest_objects.DummyLoader())
        self.tree.create_and_add_node(unittest_objects.DummyProc())
        self.tree.create_and_add_node(unittest_objects.DummyProc())
        tree2 = pickle.loads(pickle.dumps(self.tree))
        self.assertIsInstance(tree2, _WorkflowTree)
        for _node in tree2.nodes.values():
            self.assertIsInstance(_node, WorkflowNode)

    def test_export_to_string(self):
        self.tree.create_and_add_node(unittest_objects.DummyLoader())
        self.tree.create_and_add_node(unittest_objects.DummyProc())
        self.tree.create_and_add_node(unittest_objects.DummyProc())
        _str = self.tree.export_to_string()
        self.assertIsInstance(_str, str)

    def test_restore_from_list_of_nodes(self):
        tree = WorkflowTree()
        _nodes, _index = self.create_node_tree()
        tree.set_root(_nodes[0][0])
        _dump = [node.dump() for node in tree.nodes.values()]
        self.tree.restore_from_list_of_nodes(_dump)
        for _id, _node in tree.nodes.items():
            self.assertTrue(_id in self.tree.nodes.keys())
            self.assertIsInstance(
                self.tree.nodes[_id].plugin, tree.nodes[_id].plugin.__class__
            )

    def test_restore_from_list_of_nodes__wrong_type(self):
        with self.assertRaises(TypeError):
            self.tree.restore_from_list_of_nodes({0: 0, 1: 1})

    def test_restore_from_string(self):
        self.tree.create_and_add_node(unittest_objects.DummyLoader())
        self.tree.create_and_add_node(unittest_objects.DummyProc())
        self.tree.create_and_add_node(unittest_objects.DummyProc())
        _str = self.tree.export_to_string()
        tree = WorkflowTree()
        tree.restore_from_string(_str)
        for _id, _node in tree.nodes.items():
            self.assertTrue(_id in self.tree.nodes.keys())
            self.assertIsInstance(
                self.tree.nodes[_id].plugin, tree.nodes[_id].plugin.__class__
            )

    def test_restore_from_string__empty(self):
        self.tree.create_and_add_node(unittest_objects.DummyLoader())
        self.tree.create_and_add_node(unittest_objects.DummyProc())
        self.tree.create_and_add_node(unittest_objects.DummyProc())
        self.tree.restore_from_string("")
        self.assertEqual(self.tree.nodes, dict())

    def test_restore_from_string__empty_list(self):
        self.tree.create_and_add_node(unittest_objects.DummyLoader())
        self.tree.create_and_add_node(unittest_objects.DummyProc())
        self.tree.create_and_add_node(unittest_objects.DummyProc())
        self.tree.restore_from_string("[]")
        self.assertEqual(self.tree.nodes, dict())

    def test_get_complete_plugin_metadata__empty_tree(self):
        _meta = self.tree.get_complete_plugin_metadata()
        self.assertEqual(list(_meta["shapes"].keys()), [])
        self.assertIsInstance(_meta, dict)
        for _key in ["shapes", "labels", "names", "data_labels", "result_titles"]:
            self.assertIn(_key, _meta)

    def test_get_complete_plugin_metadata__populated_tree(self):
        self.tree.create_and_add_node(unittest_objects.DummyLoader())
        self.tree.create_and_add_node(unittest_objects.DummyProc())
        self.tree.create_and_add_node(unittest_objects.DummyProc())
        _meta = self.tree.get_complete_plugin_metadata()
        self.assertEqual(_meta["shapes"].keys(), self.tree.nodes.keys())
        for _key, _node in self.tree.nodes.items():
            self.assertEqual(_node.result_shape, _meta["shapes"][_key])

    def test_get_complete_plugin_metadata__changed_tree_w_o_update(self):
        _shape = (123, 456)
        self.tree.create_and_add_node(unittest_objects.DummyLoader())
        self.tree.create_and_add_node(unittest_objects.DummyProc())
        self.tree.create_and_add_node(unittest_objects.DummyProc())
        _ = self.tree.get_complete_plugin_metadata()
        self.tree.nodes[1]._result_shape = _shape
        _meta_new = self.tree.get_complete_plugin_metadata()
        self.assertEqual(_shape, _meta_new["shapes"][1])

    def test_get_complete_plugin_metadata__changed_tree_w_force_update(self):
        _shape = (123, 456)
        self.tree.create_and_add_node(unittest_objects.DummyLoader())
        self.tree.create_and_add_node(unittest_objects.DummyProc())
        self.tree.create_and_add_node(unittest_objects.DummyProc())
        _meta = self.tree.get_complete_plugin_metadata()
        self.tree.nodes[1]._result_shape = _shape
        _meta_new = self.tree.get_complete_plugin_metadata(force_update=True)
        self.assertEqual(_meta_new["shapes"][1], _meta["shapes"][1])

    def test_get_complete_plugin_metadata__changed_tree_w_tree_changed_flag(self):
        _shape = (123, 456)
        self.tree.create_and_add_node(unittest_objects.DummyLoader())
        self.tree.create_and_add_node(unittest_objects.DummyProc())
        self.tree.create_and_add_node(unittest_objects.DummyProc())
        _meta = self.tree.get_complete_plugin_metadata()
        self.tree.nodes[1]._result_shape = _shape
        self.tree._tree_changed_flag = True
        _meta_new = self.tree.get_complete_plugin_metadata()
        self.assertEqual(_meta_new["shapes"][1], _meta["shapes"][1])

    def test_hash___empty_tree(self):
        tree = WorkflowTree()
        self.assertIsInstance(hash(tree), int)

    def test_hash___simple_tree(self):
        tree = WorkflowTree()
        tree2 = WorkflowTree()
        self.assertEqual(hash(tree), hash(tree2))

    def test_hash___full_tree(self):
        tree = _WorkflowTree()
        tree.create_and_add_node(unittest_objects.DummyLoader())
        tree.create_and_add_node(unittest_objects.DummyProc())
        tree.create_and_add_node(unittest_objects.DummyProc())
        tree2 = _WorkflowTree()
        tree2.create_and_add_node(unittest_objects.DummyLoader())
        tree2.create_and_add_node(unittest_objects.DummyProc())
        tree2.create_and_add_node(unittest_objects.DummyProc())
        self.assertNotEqual(hash(tree), hash(tree2))

    def test_hash___full_tree_w_different_plugin_param(self):
        tree = _WorkflowTree()
        tree.create_and_add_node(unittest_objects.DummyLoader())
        tree.create_and_add_node(unittest_objects.DummyProc())
        tree.create_and_add_node(unittest_objects.DummyProc())
        tree2 = _WorkflowTree()
        tree2.create_and_add_node(unittest_objects.DummyLoader())
        tree2.create_and_add_node(unittest_objects.DummyProc())
        tree2.create_and_add_node(unittest_objects.DummyProc())
        tree2.root.plugin.set_param_value("image_height", 127)
        self.assertNotEqual(hash(tree), hash(tree2))


if __name__ == "__main__":
    unittest.main()

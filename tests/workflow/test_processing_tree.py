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


import copy
import pickle
import shutil
import tempfile
import unittest
from pathlib import Path

import numpy as np

from pydidas import unittest_objects
from pydidas.core import Dataset, Parameter, UserConfigError
from pydidas.plugins import PluginCollection
from pydidas.workflow import GenericNode, ProcessingTree, WorkflowNode


COLL = PluginCollection()
_PLUGIN_PATHS = COLL.registered_paths


class TestProcessingTree(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.__original_plugin_paths = COLL.registered_paths[:]
        _path = Path(unittest_objects.__file__).parent
        if _path not in COLL.registered_paths:
            COLL.find_and_register_plugins(_path)

    def setUp(self):
        self._curr_tree = ProcessingTree()
        self._tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self._tmpdir)

    @classmethod
    def tearDownClass(cls):
        COLL.unregister_plugin_path(Path(unittest_objects.__file__).parent)

    def create_node_tree(self, depth=3, width=3):
        obj00 = WorkflowNode(node_id=0, plugin=self.get_dummy_loader_plugin())
        _nodes = [[obj00]]
        _index = 1
        for _depth in range(depth):
            _tiernodes = []
            for _parent in _nodes[_depth]:
                for _ichild in range(width):
                    _node = WorkflowNode(
                        node_id=_index, plugin=self.get_dummy_proc_plugin()
                    )
                    _parent.add_child(_node)
                    _index += 1
                    _tiernodes.append(_node)
            _nodes.append(_tiernodes)
        return _nodes, _index

    def get_dummy_loader_plugin(self):
        return COLL.get_plugin_by_name("DummyLoader")()

    def get_dummy_proc_plugin(self):
        return COLL.get_plugin_by_name("DummyProc")()

    def test_active_plugin_header__no_nodes(self):
        self._curr_tree = ProcessingTree()
        self.assertEqual(self._curr_tree.active_plugin_header, "")

    def test_active_plugin_header__no_active_node(self):
        _nodes, _index = self.create_node_tree()

        self._curr_tree.register_node(_nodes[0][0])
        self._curr_tree.active_node_id = None
        self.assertEqual(self._curr_tree.active_plugin_header, "")

    def test_active_plugin_header__w_active_node(self):
        _nodes, _index = self.create_node_tree()
        _root = _nodes[0][0]
        self._curr_tree = ProcessingTree()
        self._curr_tree.register_node(_root)
        self._curr_tree.active_node_id = 0
        self.assertEqual(
            self._curr_tree.active_plugin_header, "#000 [Dummy loader Plugin]"
        )

    def test_get_all_result_shapes__no_nodes(self):
        with self.assertRaises(UserConfigError):
            self._curr_tree.get_all_result_shapes()

    def test_get_all_result_shapes__single_node(self):
        self._curr_tree.create_and_add_node(self.get_dummy_loader_plugin())
        _shapes = self._curr_tree.get_all_result_shapes()
        _dummy = self.get_dummy_loader_plugin()
        _dummy.calculate_result_shape()
        self.assertEqual(_shapes[0], _dummy.result_shape)

    def test_get_all_result_shapes__tree(self):
        _dummy = self.get_dummy_loader_plugin()
        _dummy.calculate_result_shape()
        _shape = _dummy.result_shape

        self._curr_tree.create_and_add_node(self.get_dummy_loader_plugin())
        self._curr_tree.create_and_add_node(
            self.get_dummy_proc_plugin(), parent=self._curr_tree.root, node_id=2
        )
        self._curr_tree.create_and_add_node(
            self.get_dummy_proc_plugin(), parent=self._curr_tree.root, node_id=3
        )
        self._curr_tree.prepare_execution()
        _shapes = self._curr_tree.get_all_result_shapes()
        self.assertEqual(_shapes[2], _shape)
        self.assertEqual(_shapes[3], _shape)

    def test_get_all_result_shapes__tree_with_keep_results(self):
        _dummy = self.get_dummy_loader_plugin()
        _dummy.calculate_result_shape()
        _shape = _dummy.result_shape
        self._curr_tree.create_and_add_node(self.get_dummy_loader_plugin())
        self._curr_tree.create_and_add_node(self.get_dummy_proc_plugin())
        self._curr_tree.create_and_add_node(self.get_dummy_proc_plugin())
        self._curr_tree.nodes[1].plugin.set_param_value("keep_results", True)
        _shapes = self._curr_tree.get_all_result_shapes()
        self.assertEqual(list(_shapes.keys()), [1, 2])
        self.assertEqual(_shapes[1], _shape)
        self.assertEqual(_shapes[2], _shape)

    def test_export_to_file(self):
        _fname = self._tmpdir.joinpath("export.yaml")
        _nodes, _index = self.create_node_tree()
        self._curr_tree.register_node(_nodes[0][0])
        self._curr_tree.export_to_file(_fname)
        with open(_fname, "r") as f:
            content = f.read()
        for node_id in self._curr_tree.nodes:
            self.assertTrue(content.find(f"node_id: {node_id}") > 0)

    def test_import_from_file(self):
        tree = ProcessingTree()
        _nodes, _index = self.create_node_tree()
        tree.register_node(_nodes[0][0])
        _fname = self._tmpdir.joinpath("export.yaml")
        tree.export_to_file(_fname)
        self._curr_tree.import_from_file(_fname)
        for node_id in tree.nodes:
            self.assertTrue(node_id in self._curr_tree.nodes)
            self.assertEqual(
                tree.nodes[node_id].plugin.__class__,
                self._curr_tree.nodes[node_id].plugin.__class__,
            )

    def test_execute_single_plugin__no_node(self):
        _depth = 3
        _data = np.random.random((20, 20))
        nodes, n_nodes = self.create_node_tree(depth=_depth)
        self._curr_tree.register_node(nodes[0][0])
        with self.assertRaises(KeyError):
            self._curr_tree.execute_single_plugin(114, _data)

    def test_execute_single_plugin__existing_node(self):
        _depth = 3
        _data = np.random.random((20, 20))
        _offset = 0.4
        nodes, n_nodes = self.create_node_tree(depth=_depth)
        self._curr_tree.register_node(nodes[0][0])
        _newdata, kwargs = self._curr_tree.execute_single_plugin(
            n_nodes - 2, _data, offset=_offset
        )
        self.assertTrue((abs(_newdata - _offset - _data) < 1e-15).all())

    def test_execute_process(self):
        _depth = 3
        nodes, n_nodes = self.create_node_tree(depth=_depth)
        self._curr_tree.register_node(nodes[0][0])
        self._curr_tree.execute_process(0)
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
        self._curr_tree.register_node(nodes[0][0])
        _res = self._curr_tree.execute_process_and_get_results(0)
        for _leaf in self._curr_tree.get_all_leaves():
            _id = _leaf.node_id
            self.assertIsInstance(_res[_id], Dataset)

    def test_execute_process_and_get_results__linear_w_keep_results(self):
        self._curr_tree.create_and_add_node(self.get_dummy_loader_plugin())
        self._curr_tree.create_and_add_node(self.get_dummy_proc_plugin())
        self._curr_tree.create_and_add_node(self.get_dummy_proc_plugin())
        self._curr_tree.nodes[1].plugin.set_param_value("keep_results", True)
        _res = self._curr_tree.execute_process_and_get_results(0)
        self.assertIsInstance(_res[1], Dataset)
        self.assertIsInstance(_res[2], Dataset)

    def test_prepare_execution(self):
        _depth = 3
        nodes, n_nodes = self.create_node_tree(depth=_depth)
        self._curr_tree.register_node(nodes[0][0])
        self._curr_tree.prepare_execution()
        for _node in nodes[_depth]:
            self.assertTrue(_node.plugin._preexecuted)

    def test_create_and_add_node__wrong_plugin(self):
        with self.assertRaises(TypeError):
            self._curr_tree.create_and_add_node(12)

    def test_create_and_add_node__empty_tree(self):
        _node = self._curr_tree.create_and_add_node(self.get_dummy_loader_plugin())
        self.assertEqual(len(self._curr_tree.nodes), 1)
        self.assertIsInstance(self._curr_tree.nodes[0], GenericNode)
        self.assertEqual(_node, 0)

    def test_create_and_add_node__in_tree_no_parent(self):
        self._curr_tree.create_and_add_node(self.get_dummy_loader_plugin())
        _node = self._curr_tree.create_and_add_node(self.get_dummy_proc_plugin())
        self.assertEqual(len(self._curr_tree.nodes), 2)
        self.assertIsInstance(self._curr_tree.nodes[1], GenericNode)
        self.assertEqual(self._curr_tree.nodes[0].n_children, 1)
        self.assertEqual(_node, 1)

    def test_create_and_add_node__in_tree_with_parent(self):
        self._curr_tree.create_and_add_node(self.get_dummy_loader_plugin())
        self._curr_tree.create_and_add_node(self.get_dummy_proc_plugin())
        self._curr_tree.create_and_add_node(
            self.get_dummy_proc_plugin(), parent=self._curr_tree.nodes[0]
        )
        self.assertEqual(len(self._curr_tree.nodes), 3)
        self.assertIsInstance(self._curr_tree.nodes[2], GenericNode)
        self.assertEqual(self._curr_tree.nodes[0].n_children, 2)

    def test_create_and_add_node__with_int_parent(self):
        _node = self._curr_tree.create_and_add_node(self.get_dummy_loader_plugin())
        _node2 = self._curr_tree.create_and_add_node(
            self.get_dummy_proc_plugin(), parent=_node
        )
        self.assertIsInstance(self._curr_tree.nodes[1], GenericNode)
        self.assertEqual(self._curr_tree.nodes[0].n_children, 1)
        self.assertEqual(_node, 0)
        self.assertEqual(_node2, 1)

    def test_create_and_add_node__in_tree_with_node_id(self):
        _id = 42

        self._curr_tree.create_and_add_node(self.get_dummy_loader_plugin())
        self._curr_tree.create_and_add_node(self.get_dummy_proc_plugin())
        self._curr_tree.create_and_add_node(self.get_dummy_proc_plugin(), node_id=_id)
        self.assertEqual(len(self._curr_tree.nodes), 3)
        self.assertIsInstance(self._curr_tree.nodes[_id], GenericNode)
        self.assertEqual(self._curr_tree.nodes[_id].node_id, _id)

    def test_replace_node_plugin(self):
        _orig_plugin = self.get_dummy_proc_plugin()
        _new_plugin = self.get_dummy_proc_plugin()
        _new_plugin.add_param(Parameter("test", int, 1))
        self._curr_tree.create_and_add_node(self.get_dummy_loader_plugin())
        self._curr_tree.create_and_add_node(_orig_plugin)
        self._curr_tree.reset_tree_changed_flag()
        _hash1 = hash(self._curr_tree)
        self._curr_tree.replace_node_plugin(1, _new_plugin)
        self.assertEqual(self._curr_tree.nodes[1].plugin, _new_plugin)
        self.assertTrue(self._curr_tree.tree_has_changed)
        self.assertNotEqual(_hash1, hash(self._curr_tree))

    def test_tree_copy_with_plugins(self):
        self._curr_tree.create_and_add_node(self.get_dummy_loader_plugin())
        self._curr_tree.create_and_add_node(self.get_dummy_proc_plugin())
        self._curr_tree.create_and_add_node(
            self.get_dummy_proc_plugin(), parent=self._curr_tree.root
        )
        tree2 = copy.copy(self._curr_tree)
        self.assertIsInstance(tree2, ProcessingTree)
        for _node in tree2.nodes.values():
            self.assertIsInstance(_node, WorkflowNode)
        for _node in tree2.root._children:
            self.assertTrue(_node in tree2.nodes.values())
        for key in set(self._curr_tree.__dict__.keys()) - {
            "root",
            "nodes",
            "_starthash",
        }:
            self.assertEqual(getattr(self._curr_tree, key), getattr(tree2, key))
        for _id, _node in self._curr_tree.nodes.items():
            self.assertEqual(_id, _node.node_id)
            self.assertEqual(_id, _node.plugin.node_id)
        for _id, _node in tree2.nodes.items():
            self.assertEqual(_id, _node.node_id)
            self.assertEqual(_id, _node.plugin.node_id)

    def test_tree_pickling(self):
        self._curr_tree.create_and_add_node(self.get_dummy_loader_plugin())
        self._curr_tree.create_and_add_node(self.get_dummy_proc_plugin())
        self._curr_tree.create_and_add_node(self.get_dummy_proc_plugin())
        tree2 = pickle.loads(pickle.dumps(self._curr_tree))
        self.assertIsInstance(tree2, ProcessingTree)
        for _node in tree2.nodes.values():
            self.assertIsInstance(_node, WorkflowNode)

    def test_export_to_string(self):
        self._curr_tree.create_and_add_node(self.get_dummy_loader_plugin())
        self._curr_tree.create_and_add_node(self.get_dummy_proc_plugin())
        self._curr_tree.create_and_add_node(self.get_dummy_proc_plugin())
        _str = self._curr_tree.export_to_string()
        self.assertIsInstance(_str, str)

    def test_restore_from_list_of_nodes(self):
        tree = ProcessingTree()
        _nodes, _index = self.create_node_tree()
        tree.set_root(_nodes[0][0])
        _dump = [node.dump() for node in tree.nodes.values()]
        self._curr_tree.restore_from_list_of_nodes(_dump)
        for _id, _node in tree.nodes.items():
            self.assertTrue(_id in self._curr_tree.nodes.keys())
            self.assertIsInstance(
                self._curr_tree.nodes[_id].plugin, tree.nodes[_id].plugin.__class__
            )
            self.assertEqual(_node.node_id, _id)
            self.assertEqual(_node.plugin.node_id, _id)

    def test_restore_from_list_of_nodes__wrong_type(self):
        with self.assertRaises(TypeError):
            self._curr_tree.restore_from_list_of_nodes({0: 0, 1: 1})

    def test_restore_from_string(self):
        self._curr_tree.create_and_add_node(self.get_dummy_loader_plugin())
        self._curr_tree.create_and_add_node(self.get_dummy_proc_plugin())
        self._curr_tree.create_and_add_node(self.get_dummy_proc_plugin())
        _str = self._curr_tree.export_to_string()
        tree = ProcessingTree()
        tree.restore_from_string(_str)
        for _id, _node in tree.nodes.items():
            self.assertTrue(_id in self._curr_tree.nodes.keys())
            self.assertIsInstance(
                self._curr_tree.nodes[_id].plugin, tree.nodes[_id].plugin.__class__
            )

    def test_update_from_tree(self):
        _nodes, _index = self.create_node_tree()
        self._curr_tree.set_root(_nodes[0][0])
        _new_tree = ProcessingTree()
        _new_tree.create_and_add_node(self.get_dummy_loader_plugin())
        _new_tree.create_and_add_node(self.get_dummy_proc_plugin())
        _new_tree.create_and_add_node(self.get_dummy_proc_plugin(), node_id=42)
        self._curr_tree.update_from_tree(_new_tree)
        for _id, _node in self._curr_tree.nodes.items():
            self.assertEqual(set(self._curr_tree.node_ids), set(_new_tree.node_ids))
            self.assertIsInstance(
                self._curr_tree.nodes[_id].plugin, _new_tree.nodes[_id].plugin.__class__
            )

    def test_restore_from_string__empty(self):
        with self.assertRaises(UserConfigError):
            self._curr_tree.restore_from_string("")

    def test_restore_from_string__empty_list(self):
        self._curr_tree.create_and_add_node(self.get_dummy_loader_plugin())
        self._curr_tree.restore_from_string("[]")
        self.assertEqual(self._curr_tree.nodes, dict())

    def test_get_complete_plugin_metadata__empty_tree(self):
        _meta = self._curr_tree.get_complete_plugin_metadata()
        self.assertEqual(list(_meta["shapes"].keys()), [])
        self.assertIsInstance(_meta, dict)
        for _key in ["shapes", "labels", "names", "data_labels", "result_titles"]:
            self.assertIn(_key, _meta)

    def test_get_complete_plugin_metadata__populated_tree(self):
        _nodes, _index = self.create_node_tree(width=1, depth=3)
        self._curr_tree.set_root(_nodes[0][0])
        _meta = self._curr_tree.get_complete_plugin_metadata()
        self.assertEqual(_meta["shapes"].keys(), self._curr_tree.nodes.keys())
        for _key, _node in self._curr_tree.nodes.items():
            self.assertEqual(_node.result_shape, _meta["shapes"][_key])

    def test_get_complete_plugin_metadata__changed_tree_w_o_update(self):
        _shape = (123, 456)
        self._curr_tree.create_and_add_node(self.get_dummy_loader_plugin())
        self._curr_tree.create_and_add_node(self.get_dummy_proc_plugin())
        self._curr_tree.create_and_add_node(
            unittest_objects.DummyProcNewDataset(output_shape=_shape),
            parent=self._curr_tree.root,
        )
        _ = self._curr_tree.get_complete_plugin_metadata()
        _meta_new = self._curr_tree.get_complete_plugin_metadata()
        self.assertEqual(_shape, _meta_new["shapes"][2])

    def test_get_complete_plugin_metadata__changed_tree_w_force_update(self):
        _shape = (123, 456)
        _nodes, _index = self.create_node_tree(width=1, depth=3)
        self._curr_tree.set_root(_nodes[0][0])
        _meta = self._curr_tree.get_complete_plugin_metadata()
        self._curr_tree.nodes[1]._result_shape = _shape
        _meta_new = self._curr_tree.get_complete_plugin_metadata(force_update=True)
        self.assertEqual(_meta_new["shapes"][1], _meta["shapes"][1])

    def test_get_complete_plugin_metadata__changed_tree_w_tree_changed_flag(self):
        _shape = (123, 456)
        _nodes, _index = self.create_node_tree(width=1, depth=3)
        self._curr_tree.set_root(_nodes[0][0])
        _meta = self._curr_tree.get_complete_plugin_metadata()
        self._curr_tree.nodes[1]._result_shape = _shape
        self._curr_tree._config["tree_changed"] = True
        _meta_new = self._curr_tree.get_complete_plugin_metadata()
        self.assertEqual(_meta_new["shapes"][1], _meta["shapes"][1])

    def test_hash__empty_tree(self):
        self.assertIsInstance(hash(self._curr_tree), int)

    def test_hash__full_tree(self):
        _nodes, _index = self.create_node_tree(width=1, depth=3)
        self._curr_tree.set_root(_nodes[0][0])
        tree2 = ProcessingTree()
        tree2.create_and_add_node(self.get_dummy_loader_plugin())
        tree2.create_and_add_node(self.get_dummy_proc_plugin())
        tree2.create_and_add_node(self.get_dummy_proc_plugin())
        self.assertNotEqual(hash(self._curr_tree), hash(tree2))

    def test_register_node(self):
        tree = ProcessingTree()
        node = WorkflowNode(plugin=self.get_dummy_loader_plugin())
        tree.register_node(node)
        self.assertEqual(node.node_id, 0)
        self.assertEqual(node.plugin.node_id, 0)

    def test_register_node__with_children(self):
        tree = ProcessingTree()
        nodes = [WorkflowNode(plugin=self.get_dummy_loader_plugin())]
        nodes.append(WorkflowNode(plugin=self.get_dummy_proc_plugin(), parent=nodes[0]))
        nodes.append(WorkflowNode(plugin=self.get_dummy_proc_plugin(), parent=nodes[0]))
        tree.register_node(nodes[0])
        for _i in range(2):
            self.assertEqual(nodes[_i].node_id, _i)
            self.assertEqual(nodes[_i].plugin.node_id, _i)

    def test_set_root(self):
        tree = ProcessingTree()
        node = WorkflowNode(plugin=self.get_dummy_loader_plugin())
        tree.set_root(node)
        self.assertEqual(node.node_id, 0)
        self.assertEqual(node.plugin.node_id, 0)

    def test_get_current_results__empty_tree(self):
        self.assertEqual(self._curr_tree.get_current_results(), dict())

    def test_get_current_results__populated_tree_no_processing(self):
        _nodes, _index = self.create_node_tree(width=1, depth=3)
        self._curr_tree.set_root(_nodes[0][0])
        self.assertEqual(self._curr_tree.get_current_results(), dict())

    def test_get_current_results__linear_tree(self):
        _nodes, _index = self.create_node_tree(width=1, depth=4)
        self._curr_tree.set_root(_nodes[0][0])
        self._curr_tree.execute_process(0)
        _res = self._curr_tree.get_current_results()
        self.assertEqual(len(_res), 1)
        for _key, _val in _res.items():
            self.assertIsInstance(_val, Dataset)

    def test_get_current_results__linear_tree_w_always_store_results(self):
        _nodes, _index = self.create_node_tree(width=1, depth=4)
        self._curr_tree.set_root(_nodes[0][0])
        self._curr_tree.nodes[1].plugin.set_param_value("keep_results", True)
        self._curr_tree.execute_process(0)
        _res = self._curr_tree.get_current_results()
        self.assertEqual(len(_res), 2)
        for _key, _val in _res.items():
            self.assertIsInstance(_val, Dataset)

    def test_get_current_results__branching_tree(self):
        _nodes, _index = self.create_node_tree(width=2, depth=2)
        self._curr_tree.set_root(_nodes[0][0])
        self._curr_tree.nodes[1].plugin.set_param_value("keep_results", True)
        self._curr_tree.execute_process(0)
        _res = self._curr_tree.get_current_results()
        self.assertEqual(len(_res), 5)
        for _key, _val in _res.items():
            self.assertIsInstance(_val, Dataset)


if __name__ == "__main__":
    unittest.main()

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


import os
import shutil
import tempfile
import unittest

import yaml

import pydidas
from pydidas.core import UserConfigError
from pydidas.workflow.workflow_tree import WorkflowTree, _WorkflowTree
from pydidas.workflow.workflow_tree_io import WorkflowTreeIoMeta
from pydidas.workflow.workflow_tree_io.workflow_tree_io_yaml import WorkflowTreeIoYaml


PLUGIN_COLL = pydidas.plugins.PluginCollection()


class TestWorkflowTreeIoYaml(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._path = tempfile.mkdtemp()
        cls._filename = os.path.join(cls._path, "test.yaml")
        cls.create_test_tree()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._path)

    @classmethod
    def create_test_tree(cls):
        _pluginclass = PLUGIN_COLL.get_plugin_by_name("PyFAIazimuthalIntegration")
        _plugin = _pluginclass()
        cls.TREE = WorkflowTree()
        cls.TREE.clear()
        cls.TREE.create_and_add_node(_plugin)
        cls.TREE.create_and_add_node(_plugin)
        cls.TREE.create_and_add_node(_plugin, parent=cls.TREE.nodes[0])

    def create_correct_export(self):
        with open(self._filename, "w") as _f:
            _dump = {
                "nodes": self.TREE.export_to_list_of_nodes(),
                "version": pydidas.VERSION,
            }
            yaml.safe_dump(_dump, _f)

    def test_init(self):
        obj = WorkflowTreeIoYaml()
        self.assertIsInstance(obj, WorkflowTreeIoYaml)

    def test_export_to_file(self):
        WorkflowTreeIoYaml.export_to_file(self._filename, self.TREE, overwrite=True)
        with open(self._filename, "r") as f:
            _save = yaml.safe_load(f)
        self.assertIn("version", _save)
        self.assertIn("nodes", _save)
        self.assertEqual(_save["version"], pydidas.VERSION)
        # assert does not raise an error
        _new = _WorkflowTree()
        _new.restore_from_list_of_nodes(_save["nodes"])

    def test_import_from_file__w_version(self):
        self.create_correct_export()
        _new = WorkflowTreeIoYaml.import_from_file(self._filename)
        self.assertEqual(set(_new.nodes), set(self.TREE.nodes))
        for _id, _node in _new.nodes.items():
            self.assertEqual(
                set(_node.plugin.params), set(self.TREE.nodes[_id].plugin.params)
            )

    def test_import_from_file__w_version_and_error(self):
        with open(self._filename, "w") as _f:
            _dump = {"nodes": "np.ndarrray((12))", "version": pydidas.VERSION}
            yaml.safe_dump(_dump, _f)
        with self.assertRaises(UserConfigError):
            WorkflowTreeIoYaml.import_from_file(self._filename)

    def test_import_from_file__old_version_no_error(self):
        with open(self._filename, "w") as _f:
            _dump = {
                "nodes": self.TREE.export_to_list_of_nodes(),
                "version": "0.0.0",
            }
            yaml.safe_dump(_dump, _f)
        _new = WorkflowTreeIoYaml.import_from_file(self._filename)
        self.assertEqual(set(_new.nodes), set(self.TREE.nodes))
        for _id, _node in _new.nodes.items():
            self.assertEqual(
                set(_node.plugin.params), set(self.TREE.nodes[_id].plugin.params)
            )

    def test_import_from_file__old_version_w_error(self):
        with open(self._filename, "w") as _f:
            _dump = {"nodes": "dummy incorrect string", "version": "0.0.0"}
            yaml.safe_dump(_dump, _f)
        with self.assertRaises(UserConfigError):
            WorkflowTreeIoYaml.import_from_file(self._filename)

    def test_export_to_file__existing_file_no_overwrite(self):
        with open(self._filename, "w") as f:
            f.write("test")
        with self.assertRaises(FileExistsError):
            WorkflowTreeIoYaml.export_to_file(self._filename, self.TREE)

    def test_export_to_file__existing_file__overwrite(self):
        with open(self._filename, "w") as f:
            f.write("test")
        WorkflowTreeIoYaml.export_to_file(self._filename, self.TREE, overwrite=True)
        # assert does not raise an error

    def test__meta_import_from_file(self):
        WorkflowTreeIoMeta.register_class(WorkflowTreeIoYaml, update_registry=True)
        self.create_correct_export()
        _new = WorkflowTreeIoMeta.import_from_file(self._filename)
        self.assertEqual(set(_new.nodes), set(self.TREE.nodes))
        for _id, _node in _new.nodes.items():
            self.assertEqual(
                set(_node.plugin.params), set(self.TREE.nodes[_id].plugin.params)
            )


if __name__ == "__main__":
    unittest.main()

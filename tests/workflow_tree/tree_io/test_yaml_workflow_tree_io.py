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
import tempfile
import shutil
import os

import yaml

from pydidas.workflow_tree.tree_io.yaml_workflow_tree_io import (
    YamlWorkflowTreeIo)
import pydidas

PLUGIN_COLL = pydidas.plugins.PluginCollection()

class TestYamlWorkflowTreeIo(unittest.TestCase):

    def setUp(self):
        self._path = tempfile.mkdtemp()
        self._filename = os.path.join(self._path, 'test.yaml')
        self.TREE = pydidas.workflow_tree.WorkflowTree()

    def tearDown(self):
        shutil.rmtree(self._path)

    def create_test_tree(self):

        _pluginclass = PLUGIN_COLL.get_plugin_by_name('PyFAIazimuthalIntegration')
        _plugin = _pluginclass()
        self.TREE.clear()
        self.TREE.create_and_add_node(_plugin)
        self.TREE.create_and_add_node(_plugin)
        self.TREE.create_and_add_node(_plugin, parent=self.TREE.nodes[0])

        class _Tree:
            def __init__(self):
                TREE = pydidas.workflow_tree.WorkflowTree()
                self.nodes = {node.node_id: node.get_copy() for node in
                              TREE.nodes.values()}
        _tree = _Tree()
        return _tree

    def test_init(self):
        obj = YamlWorkflowTreeIo()
        self.assertIsInstance(obj, YamlWorkflowTreeIo)

    def test_import_from_file(self):
        _tree = self.create_test_tree()
        with open(self._filename, 'w') as _f:
            _dump = [node.dump() for node in _tree.nodes.values()]
            yaml.safe_dump(_dump, _f)
        _new = YamlWorkflowTreeIo.import_from_file(self._filename)
        self.assertEqual(set(_new.nodes), set(_tree.nodes))
        for _node in _new.nodes:
            self.assertEqual(set(_new.nodes), set(_tree.nodes))

    def test_export_to_file(self):
        YamlWorkflowTreeIo.export_to_file(self._filename, self.TREE)
        # assert does not raise an error

    def test_export_to_file__existing_file_no_overwrite(self):
        with open(self._filename, 'w') as f:
            f.write('test')
        with self.assertRaises(FileExistsError):
            YamlWorkflowTreeIo.export_to_file(self._filename, self.TREE)

    def test_export_to_file__existing_file__overwrite(self):
        with open(self._filename, 'w') as f:
            f.write('test')
        YamlWorkflowTreeIo.export_to_file(self._filename, self.TREE,
                                          overwrite=True)
        # assert does not raise an error


if __name__ == "__main__":
    unittest.main()

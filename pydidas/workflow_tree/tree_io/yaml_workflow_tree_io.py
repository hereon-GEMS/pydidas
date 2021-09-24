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
"""
Module with the WorkflowTreeExporterBase class which exporters should inherit
from.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['YamlWorkflowTreeIo']


import yaml

from pydidas.config import YAML_EXTENSIONS
from .workflow_tree_io_base import WorkflowTreeIoBase


class YamlWorkflowTreeIo(WorkflowTreeIoBase):
    """
    Base class for WorkflowTree exporters.
    """
    extensions = YAML_EXTENSIONS

    @classmethod
    def export_to_file(cls, filename, tree, **kwargs):
        """
        Write the content to a file.

        This method needs to be implemented by the concrete subclass.

        Parameters
        ----------
        filename : str
            The filename of the file to be written.
        content : type
            The content in any format.
        """
        cls.check_for_existing_file(filename, **kwargs)
        _dump = [node.dump() for node in tree.nodes.values()]
        with open(filename, 'w') as _file:
            yaml.safe_dump(_dump, _file)

    @classmethod
    def import_from_file(cls, filename):
        """
        Restore the content from a file

        This method needs to be implemented by the concrete subclass.

        Parameters
        ----------
        filename : str
            The filename of the file to be written.

        Returns
        -------
        pydidas.workflow_tree.WorkflowTree
            The restored WorkflowTree.
        """
        from ..workflow_tree import _WorkflowTree
        from ..workflow_node import WorkflowNode
        from ...plugins import PluginCollection
        plugins = PluginCollection()

        with open(filename, 'r') as _file:
            _restoration = yaml.safe_load(_file)

        # Create all nodes first, then add connections in a second step:
        _new_nodes = {}
        for _info in _restoration:
            _plugin =  plugins.get_plugin_by_name(_info['plugin_class'])()
            _node = WorkflowNode(node_id=_info['node_id'], plugin=_plugin)
            for key, val in _info['plugin_params']:
                _node.plugin.set_param_value(key, val)
            _new_nodes[_info['node_id']] = _node
        for _info in _restoration:
            _node_id = _info['node_id']
            if _info['parent'] is not None:
                _new_nodes[_node_id].parent = _new_nodes[_info['parent']]
        _tree = _WorkflowTree()
        _tree.set_root(_new_nodes[0])
        return _tree

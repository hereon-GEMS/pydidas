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
Module with the WorkflowTree class which is a subclasses GenericTree
with additional support for plugins and a plugin chain.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['WorkflowTree']

from .generic_tree import GenericTree
from .workflow_node import WorkflowNode
from ..core import SingletonFactory


class _WorkflowTree(GenericTree):
    """
    The WorkflowTree is a subclassed GenericTree with support for running
    a plugin chain.
    """

    def create_and_add_node(self, plugin, parent=None, node_id=None):
        """
        Create a new node and add it to the tree.

        If the tree is empty, the new node is set as root node. If no parent
        is given, the node will be created as child of the latest node in
        the tree.

        Parameters
        ----------
        plugin : pydidas.Plugin
            The plugin to be added to the tree.
        parent : Union[WorkflowNode, None], optional
            The parent node of the newly created node. If None, this will
            select the latest node in the tree. The default is None.
        node_id : Union[int, None], optional
            The node ID of the newly created node, used for referencing the
            node in the WorkflowTree. If not specified(ie. None), the
            WorkflowTree will create a new node ID. The default is None.
        """
        _node = WorkflowNode(plugin=plugin, parent=parent,
                             node_id=node_id)
        if len(self.node_ids) == 0:
            self.set_root(_node)
            return
        if not parent:
            parent = self.nodes[self.node_ids[-1]]
            parent.add_child(_node)
        self.register_node(_node, node_id)

    def execute_process(self, arg, **kwargs):
        """
        Execute the process defined in the WorkflowTree for dat analysis.

        Parameters
        ----------
        arg : object
            Any argument that need to be passed to the plugin chain.
        **kwargs : dict
            Any keyword arguments which need to be passed to the plugin chain.
        """
        self.nodes[0].prepare_execution()
        self.nodes[0].execute_plugin_chain(arg, **kwargs)

    def execute_single_plugin(self, node_id, arg, **kwargs):
        """
        Execute a single node Plugin and get the return.

        Parameters
        ----------
        node_id : int
            The ID of the node in the tree.
        arg : object
            The input argument for the Plugin.
        **kwargs : dict
            Any keyword arguments for the Plugin execution.

        Raises
        ------
        KeyError
            If the node ID is not registered.

        Returns
        -------
        res : object
            The return value of the Plugin. Depending on the plugin, it can
            be a single value or an array.
        kwargs : dict
            The (updated) kwargs dictionary.
        """
        if not node_id in self.nodes:
            raise KeyError(f'The node ID "{node_id}" is not in use.')
        self.nodes[node_id].prepare_execution()
        _res, _kwargs = self.nodes[node_id].execute_plugin(arg, **kwargs)
        return _res, kwargs

WorkflowTree = SingletonFactory(_WorkflowTree)

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

"""
Module with the WorkflowTree class which is a subclasses GenericTree
with additional support for plugins and a plugin chain.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['WorkflowTree']

import ast
from numbers import Integral

from ..core import SingletonFactory, AppConfigError
from ..plugins import PluginCollection
from .generic_tree import GenericTree
from .workflow_node import WorkflowNode
from .workflow_tree_io import WorkflowTreeIoMeta


PLUGINS = PluginCollection()


class _WorkflowTree(GenericTree):
    """
    The _WorkflowTree is a subclassed GenericTree with support for
    running a plugin chain.

    Access within pydidas should not be direct but through the WorkflowTree
    singleton instance. Therefore, the _WorkflowTree class is not directly
    accessible in the pydidas namespace upon import and must be manually
    accessed.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._preexecuted = False

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
        parent : Union[WorkflowNode, int, None], optional
            The parent node of the newly created node. If an integer, this will
            be interpreted as the node_id of the parent and the respective
            parent will be selected. If None, this will select the latest node
            in the tree. The default is None.
        node_id : Union[int, None], optional
            The node ID of the newly created node, used for referencing the
            node in the WorkflowTree. If not specified(ie. None), the
            WorkflowTree will create a new node ID. The default is None.

        Returns
        -------
        node_id : int
            The node ID of the added node.
        """
        if isinstance(parent, Integral):
            parent = self.nodes[parent]
        _node = WorkflowNode(plugin=plugin, parent=parent, node_id=node_id)
        if len(self.node_ids) == 0:
            self.set_root(_node)
            return 0
        if not parent:
            _prospective_parent = self.nodes[self.node_ids[-1]]
            _prospective_parent.add_child(_node)
        self.register_node(_node, node_id)
        return self.node_ids[-1]

    def execute_process_and_get_results(self, arg, **kwargs):
        """
        Execute the WorkflowTree process and get the results.

        Parameters
        ----------
        arg : object
            Any argument that need to be passed to the plugin chain.
        **kwargs : dict
            Any keyword arguments which need to be passed to the plugin chain.

        Returns
        -------
        results : dict
            A dictionary with results in the form of entries with node_id keys
            and results items.
        """
        self.execute_process(arg, **kwargs)
        _leaves = self.get_all_leaves()
        _results = {}
        for _leaf in _leaves:
            if _leaf.results is not None:
                _results[_leaf.node_id] = _leaf.results
        return _results

    def execute_process(self, arg, **kwargs):
        """
        Execute the process defined in the WorkflowTree for data analysis.

        Parameters
        ----------
        arg : object
            Any argument that need to be passed to the plugin chain.
        **kwargs : dict
            Any keyword arguments which need to be passed to the plugin chain.
        """
        if not self._preexecuted:
            self.prepare_execution()
        self.root.execute_plugin_chain(arg, **kwargs)

    def prepare_execution(self):
        """
        Prepare the execution of the WorkflowTree by running all the nodes'
        prepare_execution methods.
        """
        self.root.propagate_shapes_and_global_config()
        self.root.prepare_execution()
        self._preexecuted = True
        self.reset_tree_changed_flag()

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
        self.root.propagate_shapes_and_global_config()
        self.nodes[node_id].prepare_execution()
        _res, _kwargs = self.nodes[node_id].execute_plugin(arg, **kwargs)
        return _res, kwargs

    def import_from_file(self, filename):
        """
        Import the WorkflowTree from a configuration file.

        Parameters
        ----------
        filename : Union[str, pathlib.Path]
            The filename which holds the WorkflowTree configuration.
        """
        _new_tree = WorkflowTreeIoMeta.import_from_file(filename)
        for _att in ['root', 'node_ids', 'nodes']:
            setattr(self, _att, getattr(_new_tree, _att))
        self._tree_changed_flag = True

    def export_to_file(self, filename, **kwargs):
        """
        Export the WorkflowTree to a file using any of the registered
        exporters.

        Parameters
        ----------
        filename : Union[str, pathlib.Path]
            The filename of the file with the export.
        """
        WorkflowTreeIoMeta.export_to_file(filename, self, **kwargs)

    def export_to_string(self):
        """
        Export the Tree to a simplified string representation.

        Returns
        -------
        str
            The string representation.
        """
        return str([node.dump() for node in self.nodes.values()])

    def restore_from_string(self, string):
        """
        Restore the WorkflowTree from a string representation.

        This method will accept string representations written with the
        "export_to_string" method.

        Parameters
        ----------
        string : str
            The representation.
        """
        try:
            _nodes = ast.literal_eval(string)
        except SyntaxError:
            _nodes = []
        self.restore_from_list_of_nodes(_nodes)

    def restore_from_list_of_nodes(self, list_of_nodes):
        """
        Restore the WorkflowTree from a list of Nodes with the required
        information.

        Parameters
        ----------
        list_of_nodes : list
            A list of nodes with a dictionary entry for each node holding all
            the required information (plugin_class, node_id and plugin
            Parameters).
        """
        if not isinstance(list_of_nodes, (list, tuple)):
            raise TypeError('Nodes must be supplied as a list.')
        _new_nodes = {}
        for _item in list_of_nodes:
            _plugin =  PLUGINS.get_plugin_by_name(_item['plugin_class'])()
            _node = WorkflowNode(node_id=_item['node_id'], plugin=_plugin)
            for key, val in _item['plugin_params']:
                _node.plugin.set_param_value(key, val)
            _new_nodes[_item['node_id']] = _node
        for _item in list_of_nodes:
            _node_id = _item['node_id']
            if _item['parent'] is not None:
                _new_nodes[_node_id].parent = _new_nodes[_item['parent']]
        if 0 in _new_nodes:
            self.set_root(_new_nodes[0])
        else:
            self.clear()
        self._tree_changed_flag = True

    def get_all_result_shapes(self, force_update=False):
        """
        Get the shapes of all leaves in form of a dictionary.

        Parameter
        ---------
        force_update : bool, optional
            Keyword to enforce a new calculation of the result shapes. The
            default is False.

        Raises
        ------
        AppConfigError
            If the WorkflowTree has no nodes.

        Returns
        -------
        shapes : dict
            A dict with entries of type {node_id: shape} with
            node_ids of type int and shapes of type tuple.
        """
        if self.root is None:
            raise AppConfigError('The WorkflowTree has no nodes.')
        _leaves = self.get_all_leaves()
        _shapes = [_leaf.result_shape for _leaf in _leaves]
        if None in _shapes or self._tree_changed_flag or force_update:
            self.root.propagate_shapes_and_global_config()
            self.reset_tree_changed_flag()
        _shapes = {_leaf.node_id: _leaf.result_shape
                   for _leaf in _leaves
                   if _leaf.plugin.output_data_dim is not None}
        for _id, _shape in _shapes.items():
            if -1 in _shape:
                _plugin_cls = self.get_node_by_id(_id).plugin.__class__
                _error = ('Cannot determine the shape of the output for node '
                          f'"{_id}" (type {_plugin_cls}).')
                raise AppConfigError(_error)
        return _shapes


WorkflowTree = SingletonFactory(_WorkflowTree)

# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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

"""
Module with the ProcessingTree class which is a subclasses GenericTree
with additional support for plugins and a plugin chain.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ProcessingTree"]


import ast
from numbers import Integral
from pathlib import Path
from typing import Self

from pydidas.core import UserConfigError
from pydidas.plugins import BasePlugin, OutputPlugin, PluginCollection
from pydidas.workflow.generic_tree import GenericTree
from pydidas.workflow.processing_tree_io import ProcessingTreeIoMeta
from pydidas.workflow.workflow_node import WorkflowNode


PLUGINS = PluginCollection()


class ProcessingTree(GenericTree):
    """
    ProcessingTree is a subclassed GenericTree with support for running a plugin chain.

    Access to ProcessingTrees within pydidas should not normally be through direct
    class instances but through the WorkflowTree singleton instance.
    """

    def __init__(self, **kwargs: dict):
        super().__init__(**kwargs)
        self._pre_executed = False
        PLUGINS.sig_updated_plugins.connect(self.clear)

    @property
    def active_plugin_header(self) -> str:
        """
        Get the header description of the active plugin.

        Returns
        -------
        str
            The description. If no active plugin has been selected, an empty string
            will be returned.
        """
        if self.active_node is None:
            return ""
        return f"#{self.active_node_id:03d} [{self.active_node.plugin.plugin_name}]"

    def create_and_add_node(
        self,
        plugin: BasePlugin,
        parent: WorkflowNode | int | None = None,
        node_id: int | None = None,
    ) -> int:
        """
        Create a new node and add it to the tree.

        If the tree is empty, the new node is set as root node. If no parent
        is given, the node will be created as child of the latest node in
        the tree.

        Parameters
        ----------
        plugin : pydidas.Plugin
            The plugin to be added to the tree.
        parent : WorkflowNode | int | None, optional
            The parent node of the newly created node. If an integer, this will
            be interpreted as the node_id of the parent and the respective
            parent will be selected. If None, this will select the latest node
            in the tree. The default is None.
        node_id : int | None, optional
            The node ID of the newly created node, used for referencing the
            node in the WorkflowTree. If not specified (i.e. None), the
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

    def set_root(self, node: WorkflowNode):
        """
        Set the tree root node.

        Note that this method will remove any references to the old parent in
        the node!

        Parameters
        ----------
        node : WorkflowNode
            The node to become the new root node
        """
        GenericTree.set_root(self, node)
        self.root.plugin.node_id = 0

    def replace_node_plugin(self, node_id: int, new_plugin: BasePlugin):
        """
        Replace the plugin of the selected node with the new Plugin.

        Parameters
        ----------
        node_id : int
            The node ID of the node to be replaced.
        new_plugin : pydidas.plugins.BasePlugin
            The instance of the new Plugin.
        """
        new_plugin.node_id = node_id
        self.nodes[node_id].plugin = new_plugin
        self._config["tree_changed"] = True

    def get_consistent_and_inconsistent_nodes(self) -> (list, list):
        """
        Get the consistency flags for all plugins in the WorkflowTree.

        Returns
        -------
        list
            The IDs of consistent nodes
        list
            The IDs of nodes with inconsistent data.
        """
        _consistent = []
        _inconsistent = []
        for _id in self.node_ids:
            if self.nodes[_id].consistency_check():
                _consistent.append(_id)
            else:
                _inconsistent.append(_id)
        return _consistent, _inconsistent

    def execute_process_and_get_results(self, arg: object, **kwargs: dict) -> dict:
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
        return self.get_current_results()

    def execute_process(self, arg: object, **kwargs: dict):
        """
        Execute the process defined in the WorkflowTree for data analysis.

        Parameters
        ----------
        arg : object
            Any argument that need to be passed to the plugin chain.
        **kwargs : dict
            Any keyword arguments which need to be passed to the plugin chain.
        """
        self.prepare_execution(**kwargs)
        self.root.execute_plugin_chain(arg, global_index=arg, **kwargs)

    def prepare_execution(self, **kwargs: dict):
        """
        Prepare the execution of the ProcessingTree.

        This method calls all the nodes' prepare_execution methods.
        If the tree has not changed, it will skip this method unless the forced
        keyword is set to True.

        Parameters
        ----------
        **kwargs : dict, optional
            Optional keyword arguments. Supported keywords are:

            forced : bool, optional
                Flag to force running the prepare_execution method. The default
                is False.
            test : bool, optional
                Flag to run the prepare_execution method in test mode. The default
                is False.
        """
        _forced = kwargs.get("forced", False)
        _test_mode = kwargs.get("test", False)
        if self.root is None:
            raise UserConfigError("The ProcessingTree has no nodes.")
        if self._pre_executed and not self.tree_has_changed and not _forced:
            return
        self.root.prepare_execution(test=_test_mode)
        self._pre_executed = True
        self.reset_tree_changed_flag()

    def execute_single_plugin(
        self, node_id: int, arg: object, **kwargs: dict
    ) -> (object, dict):
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
        if node_id not in self.nodes:
            raise KeyError(f'The node ID "{node_id}" is not in use.')
        self.nodes[node_id].prepare_execution()
        _res, _kwargs = self.nodes[node_id].execute_plugin(arg, **kwargs)
        return _res, kwargs

    def import_from_file(self, filename: Path | str):
        """
        Import the ProcessingTree from a configuration file.

        Parameters
        ----------
        filename : Path | str
            The filename which holds the ProcessingTree configuration.
        """
        _new_tree = ProcessingTreeIoMeta.import_from_file(filename)
        for _att in ["root", "node_ids", "nodes"]:
            setattr(self, _att, getattr(_new_tree, _att))
        self._config["tree_changed"] = True

    def export_to_file(self, filename: Path | str, **kwargs: dict):
        """
        Export the WorkflowTree to a file using any of the registered exporters.

        Parameters
        ----------
        filename : Path | str
            The filename of the file with the export.
        """
        ProcessingTreeIoMeta.export_to_file(filename, self, **kwargs)

    def export_to_string(self) -> str:
        """
        Export the Tree to a simplified string representation.

        Returns
        -------
        str
            The string representation.
        """
        return str(self.export_to_list_of_nodes())

    def export_to_list_of_nodes(self) -> list[dict]:
        """
        Export the Tree to a representation of all nodes in form of dictionaries.

        Returns
        -------
        list[dict]
            The list with a dictionary entry for each node.
        """
        return [node.dump() for node in self.nodes.values()]

    def restore_from_string(self, string: str):
        """
        Restore the ProcessingTree from a string representation.

        This method will accept string representations written with the
        "export_to_string" method.

        Parameters
        ----------
        string : str
            The representation.
        """
        try:
            _nodes = ast.literal_eval(string)
        except SyntaxError as _syntax_error:
            _nodes = []
            raise UserConfigError(
                "Could not interpret the given string representation of the "
                "Workflow to be restored. The ProcessingTree has been reset."
            ) from _syntax_error
        self.restore_from_list_of_nodes(_nodes)
        self._config["tree_changed"] = True

    def update_from_tree(self, tree: Self):
        """
        Update this tree from another ProcessingTree instance.

        The main use of this method is to keep the referenced ProcessingTree object
        alive while updating it.

        Parameters
        ----------
        tree : ProcessingTree
            A different ProcessingTree.
        """
        self.restore_from_string(tree.export_to_string())

    def restore_from_list_of_nodes(self, list_of_nodes: list | tuple):
        """
        Restore the ProcessingTree from a list of Nodes with the required
        information.

        Parameters
        ----------
        list_of_nodes : list | tuple
            A list of nodes with a dictionary entry for each node holding all
            the required information (plugin_class, node_id and plugin
            Parameters).
        """
        if not isinstance(list_of_nodes, (list, tuple)):
            raise TypeError("Nodes must be supplied as a list.")
        _new_nodes = {}
        for _item in list_of_nodes:
            _plugin = PLUGINS.get_plugin_by_name(_item["plugin_class"])()
            _plugin.node_id = _item["node_id"]
            _node = WorkflowNode(node_id=_item["node_id"], plugin=_plugin)
            for key, val in _item["plugin_params"]:
                _node.plugin.set_param_value(key, val)
            _new_nodes[_item["node_id"]] = _node
        for _item in list_of_nodes:
            _node_id = _item["node_id"]
            if _item["parent"] is not None:
                _new_nodes[_node_id].parent = _new_nodes[_item["parent"]]
        if 0 in _new_nodes:
            self.set_root(_new_nodes[0])
        else:
            self.clear()
        self._config["tree_changed"] = True

    def get_current_results(self) -> dict:
        """
        Get the results of the current WorkflowTree.

        Returns
        -------
        results : dict
            A dictionary with the results of the current WorkflowTree.
        """
        _results = {}
        for _node in self.get_all_nodes_with_results():
            if _node.results is not None:
                _results[_node.node_id] = _node.results
        return _results

    def get_all_result_shapes(self) -> dict:
        """
        Get the shapes of all leaves in form of a dictionary.

        Raises
        ------
        UserConfigError
            If the ProcessingTree has no nodes.

        Returns
        -------
        shapes : dict
            A dict with entries of type {node_id: shape} with
            node_ids of type int and shapes of type tuple.
        """
        if self.root is None:
            raise UserConfigError("The ProcessingTree has no nodes.")
        _nodes_w_results = self.get_all_nodes_with_results()
        _shapes = [
            _node.result_shape
            for _node in _nodes_w_results
            if _node.result_shape is not None
        ]
        if None in _shapes or self.tree_has_changed:
            self.reset_tree_changed_flag()
        _shapes = {
            _node.node_id: _node.result_shape
            for _node in _nodes_w_results
            if _node.plugin.output_data_dim is not None
            and _node.result_shape is not None
        }
        for _id, _shape in _shapes.items():
            if -1 in _shape:
                raise UserConfigError(
                    "Cannot determine the shape of the output for node "
                    f"#{_id} (type {type(self.nodes[_id].plugin).__name__})."
                )
        return _shapes

    def get_all_nodes_with_results(self) -> list[WorkflowNode]:
        """
        Get all tree nodes which have results associated with them.

        These are all leaf nodes in addition to all nodes which have been flagged
        with the "keep data" flag.

        Returns
        -------
        list[WorkflowNode]
            A list of all nodes which are leaves or which have been flagged.
        """
        _nodes_w_results = [
            _node
            for _node in self.nodes.values()
            if (
                (_node.is_leaf or _node.plugin.get_param_value("keep_results"))
                and not isinstance(_node.plugin, OutputPlugin)
            )
        ]
        return _nodes_w_results

    def get_complete_plugin_metadata(self) -> dict:
        """
        Get the metadata (e.g. shapes, labels, names) for all the tree's plugins.

        Note that the shapes are only available after running the plugin chain at
        least once. Otherwise, the shapes will be set to None.

        Returns
        -------
        dict
            The dictionary with the metadata.
        """
        _meta = {
            "shapes": {},
            "labels": {},
            "names": {},
            "data_labels": {},
            "result_titles": {},
        }
        if self.root is None:
            return _meta
        _shapes = [_node.result_shape for _node in self.nodes.values()]
        if None in _shapes or self.tree_has_changed:
            self.reset_tree_changed_flag()
        for _node_id, _node in self.nodes.items():
            if _node.plugin.output_data_dim is None or _node.result_shape is None:
                continue
            _label = _node.plugin.get_param_value("label")
            _plugin_name = _node.plugin.__class__.plugin_name
            _meta["shapes"][_node_id] = _node.result_shape
            _meta["labels"][_node_id] = _label
            _meta["names"][_node_id] = _plugin_name
            _meta["data_labels"][_node_id] = _node.plugin.result_data_label
            _meta["result_titles"][_node_id] = _node.plugin.result_title
        return _meta

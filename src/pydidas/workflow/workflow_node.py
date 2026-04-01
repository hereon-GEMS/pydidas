# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
Module with the WorkflowNode class which is a subclasses GenericNode
with additional support for plugins and a plugin chain.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["WorkflowNode"]


from copy import deepcopy
from numbers import Integral, Real
from typing import Any, Self

from pydidas.core import Dataset
from pydidas.core.utils import TimerSaveRuntime
from pydidas.plugins import BasePlugin
from pydidas.workflow.generic_node import GenericNode


class WorkflowNode(GenericNode):
    """
    A subclassed GenericNode wit han added plugin attribute.

    The WorkflowNode allows executing plugins individually or in a full workflow
    chain through the WorkflowTree.
    """

    kwargs_for_copy_creation = ["plugin", "node_id"]

    def __init__(self, **kwargs: Any):
        self.__preprocess_kwargs(kwargs)
        super().__init__(**kwargs)
        self.results = None
        self.result_kws = None
        self.runtime = -1

    def __preprocess_kwargs(self, kwargs: dict) -> None:
        """
        Store and remove the node_id key from the calling kwargs.

        The node ID key must be set after the plugin has been stored to
        force syncing of Plugin node ID and WorkflowNode node ID.

        Parameters
        ----------
        kwargs : dict
            The calling keyword arguments from init.
        """
        self._node_id: int | None = None
        self._plugin: BasePlugin | None = None
        self.plugin = kwargs.pop("plugin", None)
        self.node_id = kwargs.get("node_id", None)
        if self.plugin is None:
            raise KeyError(
                "No plugin has been supplied for the WorkflowNode. "
                "The node has not been created."
            )

    @property
    def plugin(self) -> BasePlugin:
        """
        Get the plugin of the node.

        Returns
        -------
        BasePlugin
            The plugin of the node.
        """
        return self._plugin

    @plugin.setter
    def plugin(self, new_plugin: BasePlugin):
        """
        Set the plugin of the node.
        """
        if new_plugin is None:
            self._plugin = None
            return
        if not isinstance(new_plugin, BasePlugin):
            raise TypeError("Plugin must be an instance of BasePlugin (or subclass).")
        self._plugin = new_plugin
        self._plugin.node_id = self.node_id

    @property
    def node_id(self) -> int | None:
        """
        Get the node_id.

        Note: This property needs to be reimplemented to allow a subclassed
        node_id.setter in the WorkflowNode.

        Returns
        -------
        node_id : int | None
            The node_id.
        """
        return self._node_id

    @node_id.setter
    def node_id(self, new_id: int | None):
        """
        Set the node_id.

        Parameters
        ----------
        new_id : int | None
            The new node ID.

        Raises
        ------
        TypeError
            If the type of the new ID is not int or None.
        """
        if not (new_id is None or isinstance(new_id, Integral)):
            raise TypeError(
                "The new node_id is not of a correct type and has not been set."
            )
        self._node_id = new_id
        if self.plugin:
            self.plugin.node_id = new_id

    def consistency_check(self) -> bool:
        """
        Property to determine if the data is consistent.

        Returns
        -------
        bool
            Flag whether the parent's output is consistent with this node's input
            dimensionality.
        """
        if self.parent is None:
            return True
        _parent_out = self.parent.plugin.output_data_dim
        _plugin_in = self.plugin.input_data_dim
        return self.parent.consistency_check() and (
            _parent_out == _plugin_in or _parent_out == -1 or _plugin_in == -1
        )

    def prepare_execution(self, **kwargs: Any) -> None:
        """
        Prepare the execution of the plugin chain.

        This method recursively calls the pre_execute methods of all (child)
        plugins.

        Parameters
        ----------
        **kwargs : Any
            Any keyword arguments that need to be passed to the plugin.
            Supported keywords are:

            test : bool, optional
                Flag to indicate that the plugin should be executed in test
                mode. This flag will prevent the plugin from storing any
                data to the file system.
        """
        _test_mode = kwargs.get("test", False)
        self.results = None
        self.plugin.test_mode = _test_mode
        self.plugin.pre_execute()
        for _child in self._children:
            _child.prepare_execution(**kwargs)

    def execute_plugin(
        self, arg: Dataset | int, **kwargs: Any
    ) -> tuple[Dataset | float, dict]:
        """
        Execute the plugin associated with the node.

        Parameters
        ----------
        arg : Dataset or int
            The argument which needs to be passed to the plugin.
        **kwargs : Any
            Any keyword arguments that need to be passed to the plugin.

        Returns
        -------
        results : Dataset or float
            The result of the plugin.execute method.
        kwargs : dict
            Any keywords required for calling the next plugin.
        """
        with TimerSaveRuntime() as _runtime:
            if kwargs.get("store_input_data", False):
                self.plugin.store_input_data_copy(arg, **kwargs)
            _results, kwargs = self.plugin.execute(arg, **kwargs)
        self._store_results_if_required(_results, kwargs)
        self.runtime = _runtime()
        return _results, kwargs

    def execute_plugin_chain(self, arg: Dataset | int, **kwargs: Any) -> None:
        """
        Execute the full plugin chain recursively.

        This method will call the plugin.execute method and pass the results
        to the node's children and call their execute_plugin_chain methods.
        Note: No result callback is intended. It is assumed that plugin chains
        are responsible for saving their own data at the end of processing.

        Uses copy-on-write strategy for multi-child nodes to minimize memory
        usage by sharing data between siblings until a mutation is detected.

        Parameters
        ----------
        arg : Dataset or int
            The argument which needs to be passed to the plugin.
        **kwargs : Any
            Any keyword arguments that need to be passed to the plugin.
        """
        res, reskws = self.execute_plugin(arg, **kwargs)
        if not self.children:
            return
        if self.n_children == 1:
            # Single child path: pass directly without deep copying kwargs
            self._children[0].execute_plugin_chain(
                res, **self._get_deep_copy_of_kwargs(reskws)
            )
        else:
            # Multi-child path: use copy-on-write strategy
            for _child in self.children:
                _child_kwargs = self._get_deep_copy_of_kwargs(reskws)
                _child_data = res.copy()
                _child.execute_plugin_chain(_child_data, **_child_kwargs)

    def _store_results_if_required(self, results: Dataset, reskws: dict) -> None:
        """
        Store the results of the plugin if required.

        Parameters
        ----------
        results : Dataset
            The result of the plugin execution.
        reskws : dict
            The keyword arguments as returned from the plugin execution
        """
        if self.plugin.output_data_dim is None:
            return
        if (
            self.is_leaf
            or self.plugin.get_param_value("keep_results")
            or reskws.get("force_store_results", False)
        ):
            self.results = results
            if self.is_leaf:
                self.result_kws = reskws
            else:
                self.result_kws = self._get_deep_copy_of_kwargs(reskws)

    @staticmethod
    def _get_deep_copy_of_kwargs(kwargs: dict) -> dict:
        """
        Get a recursive deep copy of the kwargs.

        Parameters
        ----------
        kwargs : dict
            The input dictionary.

        Returns
        -------
        kwargs_copy : dict
            A recursive deep copy of the kwargs dict.
        """
        _kwargs_copy = {
            deepcopy(_key): deepcopy(_value) for _key, _value in kwargs.items()
        }
        return _kwargs_copy

    def dump(self) -> dict:
        """
        Dump the node to a savable format.

        The dump includes information about the parent and child nodes but
        not the nodes itself. References to the nodeIDs are stored to allow
        reconstruction of the tree.
        Note: This dump is *not* recursive and will only save references to
        the child layer of the node.

        Returns
        -------
        dict
            The dict with all required information about the node.
        """
        _parent = None if self.parent is None else self.parent.node_id
        _children = [child.node_id for child in self._children]
        return {
            "node_id": self.node_id,
            "parent": _parent,
            "children": _children,
            "plugin_class": self.plugin.__class__.__name__,
            "plugin_params": [
                p.export_refkey_and_value() for p in self.plugin.params.values()
            ],
        }

    @property
    def result_shape(self) -> tuple[int, ...] | None:
        """
        Get the result shape of the plugin if it has already been calculated.

        Returns
        -------
        tuple[int, ...] or None
            Returns the shape of the Plugin's results, if it has been
            calculated. Else, returns None.
        """
        if isinstance(self.results, Dataset):
            return self.results.shape
        if isinstance(self.results, Real):
            return (1,)
        return None

    def __hash__(self) -> int:
        """
        Get the hash value for the WorkflowNode.

        The hash value is calculated by using the plugin, the number of
        children and the parent.

        Returns
        -------
        int
            The hash value.
        """
        _hashables = [len(self._children), self._parent, self._node_id, self.plugin]
        _hashes = tuple(hash(_item) for _item in _hashables)
        return hash(_hashes)

    def __copy__(self) -> "WorkflowNode":
        """
        Return a copy of the WorkflowNode instance.

        Returns
        -------
        WorkflowNode
            The WorkflowNode instance copy.
        """
        _copy: Self = super().__copy__()
        _copy.plugin.node_id = _copy.node_id
        return _copy

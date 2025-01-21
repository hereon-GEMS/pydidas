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
Module with the GenericTree class which can be used for managing items in a
tree-like structure.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["GenericTree"]


import copy
import time
import warnings
from typing import Self, Union

from qtpy import QtCore

from pydidas.core import UserConfigError
from pydidas.core.utils import get_random_string
from pydidas.workflow.generic_node import GenericNode


class GenericTree:
    """
    A generic tree used for organising items.
    """

    def __init__(self, **kwargs: dict):
        self.root = None
        self.node_ids = []
        self.nodes = {}
        self._config = {"tree_changed": False, "active_node_id": None} | kwargs
        self._starthash = hash((get_random_string(12), time.time()))

    @property
    def tree_has_changed(self) -> bool:
        """
        Get a flag which tells whether the Tree has changed since the last flag reset.

        Returns
        -------
        bool
            The has changed flag.
        """
        return self._config["tree_changed"]

    @property
    def active_node(self) -> Union[GenericNode, None]:
        """
        Get the active node.

        If no node has been selected or the tree is empty, None will be returned.

        Returns
        -------
        Union[pydidas.workflow.GenericNode, None]
            The active node.
        """
        if self.active_node_id is None or self.root is None:
            return None
        return self.nodes[self.active_node_id]

    @property
    def active_node_id(self) -> int:
        """
        Get the active node ID.

        Returns
        -------
        Union[int, None]
            The id of the active node.
        """
        return self._config["active_node_id"]

    @active_node_id.setter
    def active_node_id(self, new_id: Union[None, int]):
        """
        Set the active node ID.

        Parameters
        ----------
        new_id : Union[None, int]
            Set the active node property of the tree. The new node id must be either
            None or included in the tree's ids.

        Raises
        ------
        ValueError
            If new_id is not inluded in the tree's node ids.
        """
        if new_id is None or new_id in self.node_ids:
            self._config["active_node_id"] = new_id
            return
        raise ValueError(
            f"The given node ID '{new_id}' is not included in the stored node ids."
        )

    def reset_tree_changed_flag(self):
        """Reset the "has changed" flag for this Tree."""
        self._config["tree_changed"] = False

    def set_root(self, node: GenericNode):
        """
        Set the tree root node.

        Note that this method will remove any references to the old parent in
        the node!

        Parameters
        ----------
        node : GenericNode
            The node to become the new root node
        """
        self.verify_node_type(node)
        self.clear()
        node.parent = None
        node.node_id = 0
        self.register_node(node)

    @staticmethod
    def verify_node_type(node):
        """
        Check that the node is a GenericNode.

        Parameters
        ----------
        node : object
            The object to be checked.

        Raises
        ------
        TypeError
            If the node is not a GenericNode.
        """
        if not isinstance(node, GenericNode):
            raise TypeError(
                "Can only register GenericNodes (or subclasses) in the tree."
            )

    def clear(self):
        """Clear all items from the tree."""
        self.nodes = {}
        self.node_ids = []
        self._config["active_node_id"] = None
        self._config["tree_changed"] = True
        self._starthash = hash((get_random_string(12), time.time()))
        self.root = None

    def register_node(
        self,
        node: GenericNode,
        node_id: Union[None, int] = None,
        check_ids: bool = True,
    ):
        """
        Register a node with the tree.

        This method will register a node with the tree. It will add the node
        to the managed nodes and it will check any supplied node_ids for
        consistency with the node_id namespace. If no node_id is supplied,
        a new one will be generated.
        Note: Creation of new node_ids should be left to the tree. While
        it is not possible to create duplicates, it is possible to
        create unused "gaps" in the node_ids. This is not an issue by itself
        but not good practice.

        Parameters
        ----------
        node : GenericNode
            The node object to be registered.
        node_id : Union[None, int}, optional
            A supplied node_id. If None, the tree will select the next
            suitable node_id automatically. The default is None.
        check_ids : bool, optional
            Keyword to enable/disable node_id checking. By default, this should always
            be on if called by the user. If node trees are added to the GenericTree,
            the check will only be performed once for the newly added node and not
            again during registering of its children. The default is True.
        """
        self.verify_node_type(node)
        _ids = node.get_recursive_ids()
        if check_ids:
            self._check_node_ids(_ids)
        if self.root is None:
            self.root = node
        if node_id is None and node.node_id is None:
            node.node_id = self.get_new_nodeid()
        elif node_id is not None:
            node.node_id = node_id
        self.node_ids.append(node.node_id)
        self.nodes[node.node_id] = node
        self._config["active_node_id"] = node.node_id
        for _child in node.get_children():
            self.register_node(_child, _child.node_id, check_ids=False)
        self._config["tree_changed"] = True

    def _check_node_ids(self, node_ids: Union[list, tuple, set]):
        """
        Check the compatibility of a node's (and its children) ID with the tree.

        Parameters
        ----------
        node_ids : Union[list, tuple, set]
            A list (or other iterable) of all the node ids.

        Raises
        ------
        ValueError
            Raises ValueError if the node_id is already in use.
        ValueError
            Raises ValueError if the node_id of the new node is not larger
            than the last registered node.
        """
        for _id in node_ids:
            if _id in self.node_ids:
                raise ValueError(
                    "Duplicate node ID detected. Tree node has not been registered!"
                )
            if _id is not None and self.node_ids and _id < max(self.node_ids):
                raise ValueError(
                    "Attempt to reuse a discarded node ID detected"
                    f" (node_id = {_id}). Please choose another node_id. "
                    "Tree node has not been registered!"
                )

    def get_new_nodeid(self) -> int:
        """
        Get a new integer node id.

        This method returns the next unused integer node id. Note that
        node ids will not be re-used, i.e. the number of nodes is ultimately
        limited by the integer namespace.

        Returns
        -------
        int
            The new node id.
        """
        if len(self.node_ids) == 0:
            return 0
        return max(self.node_ids) + 1

    def get_node_by_id(self, node_id: int) -> GenericNode:
        """
        Get the node from the node_id.

        Parameters
        ----------
        node_id : int
            The node_id of the registered node.

        Returns
        -------
        GenericNode
            The node object registered as node_id.
        """
        return self.nodes[node_id]

    def delete_node_by_id(
        self, node_id: int, recursive: bool = True, keep_children: bool = False
    ):
        """
        Remove a node from the tree and delete its object.

        This method deletes a node from the tree. With the optional recursive
        keyword, node children will be deleted as well. With the keep_children keyword,
        children will be connected to the node's parent. Note that 'recursive' and
        'keep_children' are mutually exclusive.

        Note: If you deselect the recursive option but the node has children,
        a RecursionError will be raised by the node itself upon the
        deletion request.

        Parameters
        ----------
        node_id : int
            The id of the node to be deleted.
        recursive : bool, optional
            Keyword to toggle deletion of the node's children as well.
            The default is True.
        keep_children : bool, optional
            Keyword to keep the nodes children (and connect them to the node's parent).
            The default is False.
        """
        if recursive and keep_children:
            raise ValueError(
                "Conflicting selection of *recursive* and *keep_children* arguments."
            )
        if not recursive and not keep_children and self.nodes[node_id].n_children > 0:
            raise UserConfigError(
                "Cannot delete a node with children without either the *recursive* or "
                "the *keep_children* flag set."
            )
        if self.nodes[node_id] == self.root:
            if self.root.n_children == 0 or recursive:
                self.root = None
            elif self.root.n_children == 1 and keep_children:
                self.root = self.root.get_children()[0]
            else:
                raise UserConfigError(
                    "Cannot delete the root node of the tree because it has multiple "
                    "children which would become separate roots. Please make sure that "
                    "the root node only has one child before deleting it."
                )
        _subtree_ids = self.nodes[node_id].get_recursive_ids()
        if self.active_node_id in _subtree_ids:
            _parent_id = (
                None
                if self.nodes[node_id].parent is None
                else self.nodes[node_id].parent.node_id
            )
            self.active_node_id = _parent_id
        if keep_children:
            self.nodes[node_id].connect_parent_to_children()
            del self.nodes[node_id]
            self.node_ids.remove(node_id)
        else:
            self.nodes[node_id].delete_node_references(recursive=recursive)
            for _id in _subtree_ids:
                del self.nodes[_id]
                self.node_ids.remove(_id)
        self._config["tree_changed"] = True

    def change_node_parent(self, node_id: int, new_parent_id: int):
        """
        Change the parent of the selected node.

        Parameters
        ----------
        node_id : int
            The id of the selected node.
        new_parent_id : int
            The id of the selected node's new parent.
        """
        _new_parent = self.nodes[new_parent_id]
        self.nodes[node_id].change_node_parent(_new_parent)
        if new_parent_id > node_id:
            _active_node = self.nodes[node_id]
            _active_node.node_id = new_parent_id
            _new_parent.node_id = node_id
            self.nodes[new_parent_id] = _active_node
            self.nodes[node_id] = _new_parent
        self._config["tree_changed"] = True

    def order_node_ids(self):
        """Order the node ids of all of the tree's nodes."""
        _root = self.root
        _active_node = self.active_node
        if _root is None:
            return
        for _node in self.nodes.values():
            _node.node_id = None
        self.clear()
        self.set_root(_root)
        if _active_node is not None:
            self.active_node_id = _active_node.node_id

    def get_all_leaves(self) -> list:
        """
        Get all tree nodes which are leaves.

        Returns
        -------
        list
            A list of all leaf nodes.
        """
        _leaves = []
        for _node in self.nodes.values():
            if _node.is_leaf:
                _leaves.append(_node)
        return _leaves

    def copy(self) -> Self:
        """
        Get a copy of the WorkflowTree.

        While this is method is not really useful in the main application
        (due to the fact that the WorkflowTree is a Singleton), it is required
        to pass working copies of the Tree to other processes in
        multiprocessing.

        Returns
        -------
        pydidas.workflow.WorkflowTree
            A new instance of the WorkflowTree
        """
        return copy.copy(self)

    deepcopy = copy

    def __copy__(self) -> Self:
        """
        Get a copy of the GenericTree.

        Returns
        -------
        pydidas.workflow.GenericTree
            A new instance of the GenericTree
        """
        _copy = type(self.__class__.__name__, (self.__class__,), {})()
        _copy.__dict__.update(
            {
                _key: copy.deepcopy(_value)
                for _key, _value in self.__dict__.items()
                if not (
                    isinstance(_value, (QtCore.SignalInstance, QtCore.QMetaObject))
                    or _key in ["nodes", "root"]
                )
            }
        )
        if self.root is None:
            _copy.nodes = {}
            _copy.root = None
        if self.root is not None:
            _copy.set_root(copy.deepcopy(self.root))
        return _copy

    def __deepcopy__(self, memo: dict) -> Self:
        """
        Get a deep copy of the GenericTree.

        Note: The implementation of copy and deepcopy is the same for Trees.

        Parameters
        ----------
        memo : dict
            copy.deepcopy's dict of already copied values.

        Returns
        -------
        pydidas.workflow.GenericTree
            A new instance of the GenericTree
        """
        return self.__copy__()

    def __hash__(self) -> int:
        """
        Get the hash value for the GenericTree.

        The hash value is calculated by using all nodes' IDs and node hashes and a
        unique starting value which is different for each GenericTree.

        Returns
        -------
        int
            The hash value.
        """
        _node_keys = []
        _node_vals = []
        for _key, _val in self.nodes.items():
            try:
                _hash = hash(_key)
                _node_keys.append(_hash)
            except TypeError:
                warnings.warn(f'Could not hash the dictionary key "{_key}".')
            try:
                _hash = hash(_val)
                _node_vals.append(_hash)
            except TypeError:
                warnings.warn(f'Could not hash the dictionary value "{_val}".')
        return hash((tuple(_node_keys), tuple(_node_vals), self._starthash))

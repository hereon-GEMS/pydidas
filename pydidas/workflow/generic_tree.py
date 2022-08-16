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
Module with the GenericTree class which can be used for managing items in a
tree-like structure.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["GenericTree"]

import copy
import time
import warnings

from ..core.utils import get_random_string
from .generic_node import GenericNode


class GenericTree:
    """
    A generic tree used for organising items.
    """

    def __init__(self, **kwargs):
        """
        Setup method.

        Parameters
        ----------
        **kwargs : dict
            Arbitrary keyword arguments. These will be stored internally
            in an self._config dictionary.
        """
        self.root = None
        self.node_ids = []
        self.nodes = {}
        self._config = kwargs if kwargs else {}
        self._tree_changed_flag = False
        self._starthash = hash((get_random_string(12), time.time()))

    @property
    def tree_has_changed(self):
        """
        Get a flag which tells whether the Tree has changed since the last
        flag reset.

        Returns
        -------
        bool
            The has changed flag.
        """
        return self._tree_changed_flag

    def reset_tree_changed_flag(self):
        """
        Reset the "has changed" flag for this Tree.
        """
        self._tree_changed_flag = False

    def set_root(self, node):
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
        Check that the node is a GenericNode

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
                "Can only register GenericNodes (or subclasses" " in the tree."
            )

    def clear(self):
        """
        Clear all items from the tree.
        """
        self.nodes = {}
        self.node_ids = []
        self.root = None

    def register_node(self, node, node_id=None, check_ids=True):
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
        node : object
            The node object to be registered.
        node_id : int, optional
            A supplied node_id. If None, the tree will select the next
            suitable node_id automatically. The default is None.
        check_ids : bool, optional
            Keyword to enable/disable node_id checking. By default, this should
            always be on if called by the user. If node trees are added to the
            GenericTree, the check will only be performed once for the newly
            added node and not again during registering of its children.
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
        for _child in node.get_children():
            self.register_node(_child, _child.node_id, check_ids=False)
        self._tree_changed_flag = True

    def _check_node_ids(self, node_ids):
        """
        Check the node_ids of a node (and its children) and verify they are
        compatible with the tree.

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
                    "Duplicate node ID detected. Tree node has " "not been registered!"
                )
            if _id is not None and self.node_ids and _id < max(self.node_ids):
                raise ValueError(
                    "Attempt to reuse a discarded node ID detected"
                    f" (node_id = {_id}). Please choose another node_id. "
                    "Tree node has not been registered!"
                )

    def get_new_nodeid(self):
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
        i = self.node_ids[-1]
        return i + 1

    def get_node_by_id(self, node_id):
        """
        Get the node from the node_id

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

    def delete_node_by_id(self, node_id, recursive=True):
        """
        Remove a node from the tree and delete its object.

        This method deletes a node from the tree. With the optional recursive
        keyword, node children will be deleted as well.
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
        """
        ids = self.nodes[node_id].get_recursive_ids()
        self.nodes[node_id].remove_node_from_tree(recursive=recursive)
        for _id in ids:
            del self.nodes[_id]
            self.node_ids.remove(_id)
        self._tree_changed_flag = True

    def change_node_parent(self, node_id, new_parent_id):
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
        self._tree_changed_flag = True

    def get_all_leaves(self):
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

    def get_copy(self):
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
        return self.__copy__()

    def __copy__(self):
        """
        Get a copy of the GenericTree.

        Returns
        -------
        pydidas.workflow.GenericTree
            A new instance of the GenericTree
        """
        cls = self.__class__
        _copy = cls.__new__(cls)
        for key, val in self.__dict__.items():
            _copy.__dict__[key] = copy.deepcopy(val)
        _copy.clear()
        if self.root is not None:
            _copy.register_node(copy.deepcopy(self.root))
        return _copy

    def __deepcopy__(self):
        """
        Get a deep copy of the GenericTree.

        Note: The implementation of copy and deepcopy is the same for Trees.

        Returns
        -------
        pydidas.workflow.GenericTree
            A new instance of the GenericTree
        """
        return self.__copy__()

    def __hash__(self):
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

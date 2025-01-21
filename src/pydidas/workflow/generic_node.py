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
Module with the GenericNode class used for managing items in a tree-like
structure.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["GenericNode"]

import copy
from numbers import Integral
from typing import List, Self, Union

from qtpy import QtCore

from pydidas.core import UserConfigError


class GenericNode:
    """The GenericNode class is used by trees to manage connections between items."""

    kwargs_for_copy_creation = []

    @staticmethod
    def _verify_type(item: object, allowNone: bool = False):
        """
        Check that an item is of type class and raise a TypeError if not.

        Parameters
        ----------
        item : object
            Any object that needs to be checked for its type.
        allowNone : bool, optional
            Keyword which allows "None" items. The default is False.

        Raises
        ------
        TypeError
            If the item is not an instance of its own class.
        """
        if allowNone and item is None:
            return
        if not isinstance(item, GenericNode):
            raise TypeError(
                "Cannot add objects which are not of type GenericNode (or subclasses)."
            )

    def __init__(self, **kwargs: dict):
        """
        Set up the generic node.

        Any keywords will be stored as class attributes. This behaviour is motivated
        by the requirements of subclasses with specific calling arguments.

        Parameters
        ----------
        **kwargs : dict
            Any keywords required for this node.
        """
        self._parent = None
        self._node_id = None
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)
        self._children = []

    def add_child(self, child: Self):
        """
        Add a child to the node.

        This method will add the reference to a child to the current node.

        Parameters
        ----------
        child : object
            The child object to be registered.
        """
        self._verify_type(child)
        if child not in self._children:
            self._children.append(child)
        child.parent = self

    @property
    def node_id(self) -> Union[None, int]:
        """
        Get the node_id.

        Returns
        -------
        node_id : Union[None, int]
            The node_id.
        """
        return self._node_id

    @node_id.setter
    def node_id(self, new_id: Union[None, int]):
        """
        Set the node_id.

        Parameters
        ----------
        new_id : Union[None, int]
            The new node ID.

        Raises
        ------
        TypeError
            If the type of the new ID is not int or None.
        """
        if new_id is None or isinstance(new_id, Integral):
            self._node_id = new_id
            return
        raise TypeError(
            "The new node_id is not of a correct type and has not been set."
        )

    @property
    def parent_id(self) -> Union[None, int]:
        """
        Get the parent's node ID.

        Returns
        -------
        Union[None, int]
            The parent's nodeID or None if parent is None
        """
        if self.parent is None:
            return None
        return self.parent.node_id

    @property
    def is_leaf(self) -> bool:
        """
        Check if node has children.

        This method will check if the node has children and return the
        result.

        Returns
        -------
        bool
            True if the node has no children, else False.
        """
        if len(self._children) > 0:
            return False
        return True

    @property
    def n_children(self) -> int:
        """
        Get the number of children.

        This property will return the number of children registered in the
        node.

        Returns
        -------
        int
            The number of children.
        """
        return len(self._children)

    @property
    def parent(self) -> Union[None, Self]:
        """
        Get the node's parent.

        Returns
        -------
        parent : Union[GenericNode, None]
            The parent node.
        """
        return self._parent

    @parent.setter
    def parent(self, parent: Union[None, Self]):
        """
        Set the node's parent.

        This method will store a reference to the parent object in the node.

        Parameters
        ----------
        parent : pydidas.workflow.GenericNode
            The parent object
        """
        if parent == self._parent:
            return
        self._verify_type(parent, allowNone=True)
        if self.parent is not None:
            self.parent.remove_child_reference(self)
        self._parent = parent
        if parent is not None:
            parent.add_child(self)

    @property
    def children(self) -> list[Self]:
        """
        Get the list of children.

        Returns
        -------
        list
            The list of children.
        """
        return self._children

    @property
    def children_ids(self) -> list[int]:
        """
        Get the list of children IDs.

        Returns
        -------
        list[int]
            The list of children IDs.
        """
        return [_child.node_id for _child in self._children]

    def get_children(self) -> list:
        """
        Get the child objects.

        This method will return the child objects themselves.

        Returns
        -------
        list
            A list with the children.
        """
        return self._children

    def get_recursive_connections(self) -> List[int]:
        """
        Get recursive connections between the node and all children.

        This method returns the recursive connection between a node and
        its children (and all further descendants) in the form of a list of
        entries with node_ids of parent and child.

        Returns
        -------
        conns : list
            A list with entries in the form of [parent.node_id, child.node_id]
            for all descendants from the current node.
        """
        conns = []
        for child in self._children:
            conns.append([self.node_id, child.node_id])
            conns += child.get_recursive_connections()
        return conns

    def get_recursive_ids(self) -> List[int]:
        """
        Get the node ids of the node and all children in its branch.

        This method will return a list of all node_ids for the current node
        and all its children (recursively) to be able to select the complete
        branch for an operation.

        Returns
        -------
        res : list
            A list of all node_ids for the node and all children on its branch.
        """
        res = [self.node_id]
        for child in self._children:
            res += child.get_recursive_ids()
        return res

    def delete_node_references(self, recursive: bool = True):
        """
        Delete all references to the node from its parent and children.

        If the node has a parent, the reference to itself is removed from the
        parent. If the node has children, references to these children are
        removed as well. Using the recursive keyword, this will be done for
        the whole branch of nodes starting with itself.

        Parameters
        ----------
        recursive : bool, optional
            Keyword to toggle recursive delete of the node's children as well.
            The default is True.

        Raises
        ------
        RecursionError
            If the node has children but recursive is False, a recursion
            error will be raised. This will prevent the children to become
            separated from the tree structure.
        """
        if not self.is_leaf and not recursive:
            raise RecursionError(
                "Node children detected but deletion is not recursive."
            )
        self.parent = None
        for _child in self._children:
            _child.delete_node_references(recursive)

    def connect_parent_to_children(self):
        """
        Connect the node's parent to the node's children.

        Raises
        ------
        UserConfigError
            If the node does not have a parent and multiple children.
        """
        if self.parent is None and len(self._children) > 1:
            raise UserConfigError(
                "Cannot delete the node and connect its parent and children because "
                "the node does not have a parent and the new tree would have multiple "
                "roots."
            )
        if self.parent is None:
            for _child in self._children:
                _child.parent = None
            return
        while self.n_children:
            self.parent.add_child(self.children[0])
        self._children = []
        self.parent = None

    def remove_child_reference(self, child: Self):
        """
        Remove reference to an object from the node.

        This method will remove the reference to the child but not delete
        the child itself.
        Note: This method's main use is to allow children to un-register
        themselves from their parents before deletion and should not be called
        by the user.

        Parameters
        ----------
        child : GenericNode
            The child instance.

        Raises
        ------
        ValueError
            If the referenced child is not included in the node's children.
        """
        if child not in self._children:
            raise ValueError("Instance is not a child!")
        self._children.remove(child)

    def change_node_parent(self, new_parent: Self):
        """
        Change the parent of the selected node.

        Parameters
        ----------
        new_parent : Union[pydidas.workflow.GenericNode, None]
            The new parent of the node.
        """
        if new_parent in [self._parent, self]:
            return
        self._verify_type(new_parent, allowNone=False)
        if new_parent.node_id in self.get_recursive_ids():
            raise UserConfigError(
                "Cannot change the node parent because the new parent node "
                "is a child of the current node."
            )
        if self._parent is not None:
            self._parent.remove_child_reference(self)
        self._parent = new_parent
        new_parent.add_child(self)

    def copy(self) -> Self:
        """
        Get a copy of the Node.

        Returns
        -------
        pydidas.workflow.GenericNode
            The node's copy.
        """
        return copy.copy(self)

    deepcopy = copy

    def __copy__(self) -> Self:
        """
        Copy the generic node including any children.

        Returns
        -------
        GenericNode
            The copy.
        """
        kwargs = {arg: getattr(self, arg) for arg in self.kwargs_for_copy_creation}
        _copy = self.__class__(**kwargs)
        _copy.__dict__ = {
            _key: copy.copy(_value)
            for _key, _value in self.__dict__.items()
            if not (
                isinstance(_value, (QtCore.SignalInstance, QtCore.QMetaObject))
                or _key in ["_children", "_parent"]
            )
        }
        _copy._children = []
        _copy._parent = None
        if self.parent is not None:
            self.parent.add_child(_copy)
        for _child in self._children:
            _child_copy = copy.copy(_child)
            _copy.add_child(_child_copy)
        return _copy

    def __deepcopy__(self, memo: dict) -> Self:
        """
        Overwrite generic deepcopy with copy.
        """
        return self.__copy__()

    def __hash__(self) -> int:
        """
        Get a hash value for the GenericNode.

        The hash is determined by the node ID, the parent and the number of
        children (but not by the children themselves to prevent circular
        recursion).

        Returns
        -------
        int
            The hash value.
        """
        return hash(
            (hash(len(self._children)), hash(self._parent), hash(self._node_id))
        )

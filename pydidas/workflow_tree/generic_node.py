#!/usr/bin/env python

# MIT License
#
# Copyright (c) 2021 Malte Storm, Helmholtz-Zentrum Hereon.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Module with the generic node class used for managing workflows."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['GenericNode']

class GenericNode:
    """
    The GenericNode class is used by trees to manage connections between
    items.
    """
    def __init__(self, **kwargs):
        """
        Setup the generic node.

        Any keywords will be stored as class attributes. This behaviour is
        motivated by the requirements of subclasses with specific calling
        arguments.

        Parameters
        ----------
        **kwargs : type
            Any keywords required for this node.

        Returns
        -------
        None.
        """
        self._parent = None
        self.node_id = None
        if 'parent' in kwargs.keys():
            self._parent = kwargs['parent']
            del kwargs['parent']
        for key in kwargs:
            setattr(self, key, kwargs[key])
        self._children = []

    def add_child(self, child):
        """
        Add a child to the node.

        This method will add the reference to a child to the current node.

        Parameters
        ----------
        child : object
            The child object to be registered.

        Returns
        -------
        None.
        """
        child._parent = self
        if child not in self._children:
            self._children.append(child)

    def remove_child_reference(self, child):
        """
        Remove reference to an object from the node.

        This method will remove the reference to the child but not delete
        the child itself.
        Note: This method's main use is to allow children to un-register
        themselves from their parents before deletion.

        Parameters
        ----------
        child : TYPE
            DESCRIPTION.

        Raises
        ------
        ValueError
            DESCRIPTION.

        Returns
        -------
        None.
        """
        if child not in self._children:
            raise ValueError('Instance is not a child!')
        self._children.remove(child)

    def is_leaf(self):
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

    def num_children(self):
        """
        Get the number of children.

        This method will return the number of children registered in the node.

        Returns
        -------
        int
            The number of children.
        """
        return len(self._children)

    def get_children(self):
        """
        Get the child objects.

        This method will return the child objects themselves.

        Returns
        -------
        list
            A list with the children.
        """
        return self._children

    @property
    def n_child(self):
        """
        Get the number of children.

        This property is similar to the num_children method.

        Returns
        -------
        int
            The number of children.
        """
        return len(self._children)

    def set_parent(self, parent):
        """
        Set the nodes parent.

        This method will store a reference to the parent object in the node.

        Parameters
        ----------
        parent : object
            The parent object

        Returns
        -------
        None.
        """
        self._parent = parent

    def get_recursive_connections(self):
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

    def get_recursive_ids(self):
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

    def delete_node(self, recursive=True):
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

        Returns
        -------
        None.
        """
        if not self.is_leaf() and not recursive:
            raise RecursionError('Node children detected but deletion'
                                 'is not recursive.')
        if self._parent is not None:
            self._parent.remove_child_reference(self)
        if self.is_leaf():
            return
        for child in self.get_children():
            child.delete_node(recursive)
        self._children = []

# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""Module with the generic tree class used for managing workflows."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['GenericTree']

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
            in an self.options dictionary.

        """
        self.root = None
        self.node_ids = []
        self.nodes = {}
        self.options = kwargs if kwargs else {}

    def clear(self):
        """
        Clear all items from the tree.
        """
        self.nodes = {}
        self.node_ids = []
        self.root = None

    def set_root(self, *args):
        """
        Set the tree root node.

        Abstract set root method which needs to be implemented by subclasses.

        Raises
        ------
        NotImplementedError
            This abstract method is not implemented in the base class.
        """
        raise NotImplementedError()

    def add_node(self, *args, **kwargs):
        """
        Add a node to the tree.

        This abstract method needs to be implemented by the subclasses.

        Raises
        ------
        NotImplementedError
            This abstract method is not implemented in the base class.
        """
        raise NotImplementedError()

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
        if not self.node_ids:
            return 0
        i = self.node_ids[-1]
        return i + 1

    def register_node(self, node, node_id=None):
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

        Raises
        ------
        ValueError
            Raises ValueError if the node_id is already in use.
        ValueError
            Raises ValueError if the node_id of the new node is not larger
            than the last registered node.
        """
        if node_id in self.node_ids:
            raise ValueError('Duplicate node ID detected. Tree node has not'
                             'been registered!')
        if self.node_ids and node_id < self.node_ids[-1]:
            raise ValueError('Attempt to reuse a discarded node ID detected'
                             f' (node_id = {node_id}). Please choose another'
                             'node_id. Tree node has not been registered!')
        if node_id is None:
            node.node_id = self.get_new_nodeid()
        else:
            node.node_id = node_id
        self.node_ids.append(node.node_id)
        self.nodes[node.node_id] = node

    def find_node_by_id(self, node_id):
        """
        Get the node from the node_id

        Parameters
        ----------
        node_id : int
            The node_id of the registered node.

        Raises
        ------
        TypeError
            Raises TypeError if no nodes have been registered.
        ValueError
            Raises ValueError if the node_id has not been registered.

        Returns
        -------
        object
            The node object registered as node_id.

        """
        if not self.nodes:
            raise TypeError('No nodes detected in Tree')
        if not node_id in self.node_ids:
            raise ValueError(f'No node ID "{node_id}" has been registerd in'
                             'the tree.')
        return self.nodes[node_id]

    def delete_node(self, node_id, recursive=True):
        """
        Delete a node.

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

        Raises
        ------
        KeyError
            If the node_id is not found.
        """
        if node_id not in self.node_ids:
            raise KeyError('Selected node not found.')
        ids = self.nodes[node_id].get_recursive_ids()
        self.nodes[node_id].delete_node(node_id, recursive=recursive)
        for _id in ids:
            del self.nodes[_id]

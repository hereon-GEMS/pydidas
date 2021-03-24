# -*- coding: utf-8 -*-
"""
Created on Fri Mar 19 14:14:15 2021

@author: ogurreck
"""

class GenericNode:
    def __init__(self, **kwargs):
        self._parent = None
        if 'parent' in kwargs.keys():
            self._parent = kwargs['parent']
            del kwargs['parent']

        for key in kwargs:
            setattr(self, key)

        self._children = []

    def add_child(self, child):
        child._parent = self
        self._children.append(child)

    def remove_child_reference(self, child):
        if child not in self._children:
            raise ValueError('Instance is not a child!')
        self._children.remove(child)

    def is_leaf(self):
        if len(self._children) > 0:
            return False
        return True

    def num_children(self):
        return len(self._children)

    def get_children(self):
        return self._children

    @property
    def n_child(self):
        return len(self._children)

    def set_parent(self, parent):
        self._parent = parent

    def delete_node(self, recursive=True):
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


class GenericTree:
    def __init__(self, **kwargs):
        self.root = None
        self.node_ids = []
        self.nodes = {}

    def clear(self):
        raise NotImplementedError()

    def set_root(self, *args):
        raise NotImplementedError()

    def add_node(self, *args, **kwargs):
        raise NotImplementedError()

    def get_new_nodeid(self):
        if not self.node_ids:
            return 0
        else:
            i = self.node_ids[-1]
            return i+1

    def register_node(self, node, node_id=None):
        if node_id in self.node_ids:
            raise ValueError('Duplicate node ID detected. Tree node has not'
                             'been registered!')
        if not node_id:
            node.node_id = self.get_new_nodeid()
        self.node_ids.append(node.node_id)
        self.nodes[node.node_id] = node

    def find_node_by_id(self, node_id):
        if not self.nodes:
            raise TypeError('No nodes detected in Tree')
        return self.nodes[node_id]

    def delete_node(self, node_id, recursive=True):
        if node_id not in self.node_ids:
            raise KeyError('Selected node not found.')
        ids = self.nodes[node_id].get_recursive_ids()
        self.nodes[node_id].delete_node(node_id)
        for _id in ids:
            del self.nodes[_id]




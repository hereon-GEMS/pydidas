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

    def set_parent(self, parent):
        self._parent = parent

    def delete_node(self, recursive=True):
        if self.is_leaf():
            return
        if not self.is_leaf() and not recursive:
            raise RecursionError('Node children detected but deletion'
                                 'is not recursive.')
        for child in self.get_children():
            child.delete_node(recursive)
        self._children = []
        self._parent.remove_child_reference(self)

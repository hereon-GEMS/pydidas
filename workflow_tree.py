# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 11:39:13 2021

@author: ogurreck
"""
from copy import copy
from plugin_workflow_gui.generic_tree import GenericNode

class WorkflowNode(GenericNode):
    def __init__(self, **kwargs):
        """name=None, parent=None, node_id=None, plugin=None"""
        super().__init__(**kwargs)
        node_id = self.node_id if hasattr(self, 'node_id') else None
        if node_id and node_id in WorkflowTree().node_ids:
            raise ValueError('Duplicate node ID detected. Tree node has not'
                             'been created!')
        WorkflowTree().register_node(self, node_id)
        self._children = []

    def get_recursive_ids(self):
        res = [self.node_id]
        if not self.is_leaf():
            for child in self._children:
                res += child.get_recursive_ids()
        return res

    # def get_parent(self):
    #     return self._parent

    # def find_attribute_match(self, attr, val):
    #     res = []
    #     if hasattr(self, attr) and self.__dict__[attr] == val:
    #         res += [self.plugin]
    #     for _child in self._children:
    #         res += _child.find_attribute_match(attr, val)
    #     return res

    # def find_plugin_match(self, plugin_cls):
    #     res = []
    #     if self.plugin.__class__  == plugin_cls:
    #         res += [self.plugin]
    #     for _child in self._children:
    #         res += _child.find_plugin_match(plugin_cls)
    #     return res

    def execute_plugin(self, data, **kwargs):
        return self.plugin.execute(data, **kwargs)

    def execute_plugin_chain(self, data, **kwargs):
        res, reskws = self.plugin.execute(copy(data), **copy(kwargs))
        for _child in self._children:
            _child.execute_plugin_chain(res, **reskws)

    def delete_node(self, recursive=True):
        if self.is_leaf():
            self.plugin = None
            return
        if not self.is_leaf() and not recursive:
            raise RecursionError('Node children detected but deletion'
                                 'is not recursive.')
        for child in self.get_children():
            child.delete_node(recursive)
        self._children = []
        self._parent.remove_child_reference(self)


class _WorkflowTree:
    def __init__(self):
        self.nodes = {}
        self.node_ids = []

    def clear(self):
        self.nodes = {}
        self.node_ids = []

    def set_root(self, name, plugin):
        self.nodes = {0: WorkflowNode(name, plugin=plugin)}
        self.node_ids = [0]

    def add_node(self, name, plugin, parent=None, node_id=None):
        if not len(self.node_ids):
            self.set_root(name, plugin)
            return
        _node = WorkflowNode(name, parent, node_id, plugin)
        if not parent:
            parent = self.nodes[self.node_ids[-2]]
            parent.add_child(_node)

    def find_nodes_by_plugin_key(self, key, value):
        res = []
        for node_id in self.nodes:
            _plugin= self.nodes[node_id].plugin
            print(node_id, _plugin)
            if hasattr(_plugin, key) and getattr(_plugin, key) == value:
                res.append(node_id)
        return res

    def get_new_nodeid(self):
        if not self.node_ids:
            self.node_ids = [0]
            return 0
        else:
            i = self.node_ids[-1]
            self.node_ids.append(i+1)
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

    def execute_process(self, data, **kwargs):
        self.nodes[0].execute_plugin_chain(data, **kwargs)


class _WorkflowTreeFactory:
    def __init__(self):
        self._instance = None

    def __call__(self):
        if not self._instance:
            self._instance = _WorkflowTree()
        return self._instance

WorkflowTree = _WorkflowTreeFactory()
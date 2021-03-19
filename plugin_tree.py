# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 11:39:13 2021

@author: ogurreck
"""

class WorkflowNode:
    def __init__(self, name=None, parent=None, node_id=None, plugin=None):
        self.name = name
        self._parent = parent
        if node_id and node_id in PluginTree().node_ids:
            raise ValueError('Duplicate node ID detected. Tree node has not'
                             'been created!')
        PluginTree().register_node(self, node_id)
        self.plugin = plugin
        self._children = []

    def add_child(self, child):
        child._parent = self
        self._children.append(child)

    def is_leaf(self):
        if len(self._children) > 0:
            return False
        return True

    @property
    def num_children(self):
        return len(self._children)

    @property
    def get_children(self):
        return self._children

    @property
    def get_parent(self):
        return self._parent

    def find_attribute_match(self, attr, val):
        res = []
        if hasattr(self, attr) and self.__dict__[attr] == val:
            res += [self.plugin]
        for _child in self._children:
            res += _child.find_attribute_match(attr, val)
        return res

    def find_Workflow_match(self, plugin_cls):
        res = []
        if self.plugin.__class__  == plugin_cls:
            res += [self.plugin]
        for _child in self._children:
            res += _child.find_Workflow_match(plugin_cls)
        return res

    def execute_Workflow(self, *args, **kwargs):
        res = self.plugin.execute(*args, **kwargs)
        for _child in self._children:
            _child.plugin.execute(res)


class _WorkflowTree:
    def __init__(self):
        self.nodes = {}
        self.node_ids = []

    def set_root(self, name, node):
        self.node.node_id = 0
        self.nodes = {0: node}
        self.node_ids = [0]

    def find_by_name(self, name):
        res = []
        if len(self.nodes):
            for p in self.nodes:
                pass
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


class _WorkflowTreeFactory:
    def __init__(self):
        self._instance = None

    def __call__(self):
        if not self._instance:
            self._instance = _WorkflowTree()
        return self._instance

PluginTree = _WorkflowTreeFactory()
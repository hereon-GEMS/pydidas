# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 11:39:13 2021

@author: ogurreck
"""
from copy import copy
from plugin_workflow_gui.workflow_tree.generic_tree import GenericNode, GenericTree

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
        for child in self._children:
            res += child.get_recursive_ids()
        return res

    def execute_plugin(self, data, **kwargs):
        return self.plugin.execute(data, **kwargs)

    def execute_plugin_chain(self, data, **kwargs):
        res, reskws = self.plugin.execute(copy(data), **copy(kwargs))
        for _child in self._children:
            _child.execute_plugin_chain(res, **reskws)


class _WorkflowTree(GenericTree):
    def __init__(self):
        super().__init__()

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
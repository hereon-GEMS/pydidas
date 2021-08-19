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

from copy import copy

from .generic_tree import GenericTree
from .generic_node import GenericNode

__all__ = ['WorkflowNode', 'WorkflowTree']

class WorkflowNode(GenericNode):
    """
    """
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

    def set_root(self, name, plugin):
        self.nodes = {0: WorkflowNode(name, plugin=plugin)}
        self.node_ids = [0]

    def add_node(self, name, plugin, parent=None, node_id=None):
        if len(self.node_ids) == 0:
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

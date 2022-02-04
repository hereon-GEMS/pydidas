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
Module with the WorkflowTreeEditManager which interfaces the WorkflowTree
with the editing Canvas.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['WorkflowTreeEditManager']

import time
from functools import partial

from PyQt5 import QtCore
import numpy as np

from ...core.constants import gui_constants
from ...core import SingletonFactory
from ...plugins import PluginCollection
from ...widgets.workflow_edit import PluginInWorkflowBox
from ...workflow import WorkflowTree, PluginPositionNode

PLUGIN_COLLECTION = PluginCollection()
TREE = WorkflowTree()


class _WorkflowTreeEditManager(QtCore.QObject):
    """
    Manage the editing of the workflow tree.

    The _WorkflowTreeEditManager is designed as Singleton to manage editing
    the WorkflowTree, plugin parameters and the corresponding plugins' QT
    widgets. It is responsible for creating widgets and placing them correctly
    on the canvas of the workflow editor. Most method names correspond to
    similar methods in WorkflowTreeEditManager class. This class should only
    be used by the WorkflowTreeEditManager to manage the widget aspect.
    """
    plugin_to_edit = QtCore.Signal(int)
    plugin_to_delete = QtCore.Signal(int)
    pos_x_min = 5
    pos_y_min = 5

    def __init__(self, qt_canvas=None):
        """
        Setup the instance.

        Parameters
        ----------
        qt_canvas : QtWidget, optional
            The QtWidget which acts as canvas for the plugin workflow tree.
            The default is None.
        """
        super().__init__()
        self.root = None
        self.qt_canvas= qt_canvas
        self.active_node_id = None
        self._node_positions = {}
        self._node_widgets = {}
        self._nodes = {}

    def update_qt_canvas(self, qt_canvas):
        """
        Store references to the QT items.

        This method stores internal references to the canvas and main window.
        Because the class is designed as singleton, this information will
        typically not be available at instantiation and needs to be supplied
        at runtime.

        Parameters
        ----------
        qt_canvas : QtWidget
            The QtWidget which acts as canvas for the plugin workflow tree.
            The default is None.
        """
        if qt_canvas:
            self.qt_canvas = qt_canvas

    def add_new_plugin_node(self, name, title=None):
        """
        Add a new plugin node to the workflow.

        Add a new plugin node to the workflow. The plugin type is determined
        by the name. An optional title can be used as name for the plugin
        widget but the title will be determined automatically from the plugin
        name if not selected.
        New plugins will always be created as children of the active plugin
        and it is the users responsibility to select the correct parent
        prior to calling this method.

        Parameters
        ----------
        name : str
            The name of the plugin.
        title : str, optional
            The title of the plugin widget. If None, this will default to the
            widget name. The default is None.

        Raises
        ------
        AttributeError
            AttributeError is raised if the Qt drawing Canvas for the plugins
            has not been defined yet.
        """
        _plugin = PLUGIN_COLLECTION.get_plugin_by_plugin_name(name)()
        _parent = TREE.nodes.get(self.active_node_id, None)
        TREE.create_and_add_node(_plugin, parent=_parent)
        _node_id = TREE.node_ids[-1]
        self.__create_position_node(_node_id)
        self.__create_widget(title if title else name, _node_id)
        self.set_active_node(_node_id)
        if not self.qt_canvas:
            raise Warning('No QtCanvas defined. Nodes added but cannot be '
                          'displayed')
        self.update_node_positions()

    def __create_position_node(self, node_id):
        """
        Create a new PluginPositionNode with the current node ID.

        Parameters
        ----------
        node_id : int
            The node ID.
        """
        _parent = self._nodes.get(self.active_node_id, None)
        _node = PluginPositionNode(parent=_parent, node_id=node_id)
        self._nodes[node_id] = _node
        if self.root is None:
            self.root = _node

    def __create_widget(self, title, node_id):
        """
        Create the widget associated with the Plugin to display the plugin
        position on the canvas.

        Parameters
        ----------
        title : str
            The plugin title.
        node_id : int
            The node ID. Required for referencing the widgets later.
        """
        _widget = PluginInWorkflowBox(title, node_id, parent=self.qt_canvas)
        _widget.widget_activated.connect(self.set_active_node)
        _widget.widget_delete_request.connect(
            partial(self.delete_single_node_and_children, node_id))
        _widget.setVisible(True)
        self._node_widgets[node_id] = _widget

    @QtCore.Slot(int)
    def set_active_node(self, node_id, force_update=False):
        """
        Set the node with node_id to be the active node.

        This method will

        Parameters
        ----------
        node_id : int
            The unique identifier for the node to be activated.
        force_update : bool, optional
            Keyword to force an update cycle. This must be used after loading
            a new WorkflowTree or after activating the Frame.

        Raises
        ------
        KeyError
            A KeyError is raised if the node_id key has not been registered
            with the manager yet.
        """
        if node_id not in self._nodes.keys():
            return
        if node_id == self.active_node_id and not force_update:
            return
        for nid in self._node_widgets:
            self._node_widgets[nid].widget_select(node_id == nid)
        self.active_node_id = node_id
        self.plugin_to_edit.emit(node_id)

    def update_node_positions(self):
        """
        Update the node positions on the canvas after changes to the tree.

        This method will reposition the nodes on the drawing canvas and link
        parents and children with lines to allow following the workflow.
        """
        if self.root is None:
            return
        _pos = self.root.get_relative_positions()
        _width = (max(_pos.values())[0]
                  + gui_constants.GENERIC_PLUGIN_WIDGET_WIDTH)
        _offset = 0
        if _width < self.qt_canvas.parent().width():
            _offset = (self.qt_canvas.parent().width() - _width) // 2
        pos_vals = np.asarray(list(_pos.values()))
        pos_vals[:, 0] += - np.amin(pos_vals[:, 0]) + self.pos_x_min + _offset
        pos_vals[:, 1] += - np.amin(pos_vals[:, 1]) + self.pos_y_min
        self._node_positions = {key: pos_vals[i] for i, key in enumerate(_pos)}
        for node_id in TREE.node_ids:
            self._node_widgets[node_id].move(self._node_positions[node_id][0],
                                       self._node_positions[node_id][1])
        self.qt_canvas.setFixedSize(self.root.width + 2 * self.pos_x_min
                                    + _offset,
                                    self.root.height + 2 * self.pos_y_min)
        self.__update_node_connections()

    def __update_node_connections(self):
        """
        Update the node connections.

        This method will query the nodes - starting with root - about its
        children and all connections.
        """
        node_conns = self.root.get_recursive_connections()
        widget_conns = []
        for node0, node1 in node_conns:
            x0 = (self._node_positions[node0][0]
                  + gui_constants.GENERIC_PLUGIN_WIDGET_WIDTH // 2)
            y0 = (self._node_positions[node0][1]
                  + gui_constants.GENERIC_PLUGIN_WIDGET_HEIGHT)
            x1 = (self._node_positions[node1][0]
                  + gui_constants.GENERIC_PLUGIN_WIDGET_WIDTH // 2)
            y1 = self._node_positions[node1][1]
            widget_conns.append([x0, y0, x1, y1])
        self.qt_canvas.update_widget_connections(widget_conns)

    def update_from_tree(self, reset_active_node=False):
        """
        Update the canvas and nodes from the WorkflowTree.

        Parameters
        ----------
        reset_active_node : bool, optional
            Flag to toggle resetting the active node. After loading a
            WorkflowTree from file, this can be used to reset the selection.
        """
        _stored_active_node = self.active_node_id
        self.__delete_all_nodes_and_widgets()
        for _node_id, _node in TREE.nodes.items():
            name = _node.plugin.plugin_name
            self.active_node_id = _node.parent_id
            self.__create_position_node(_node_id)
            self.__create_widget(name, _node_id)
        self.update_node_positions()
        if reset_active_node:
            self.active_node_id = None
            self.plugin_to_edit.emit(-1)
            return
        self.active_node_id = _stored_active_node
        self.set_active_node(_stored_active_node, force_update=True)

    def __delete_all_nodes_and_widgets(self):
        """
        Delete all nodes and widgets from the Tree to prepare loading a
        new workflow.
        """
        _all_ids = list(self._node_widgets.keys())
        self.__delete_nodes_and_widgets(_all_ids)

    def delete_single_node_and_children(self, node_id):
        """
        Remove a node from the tree.

        This method will send a signal to instruct the WorkflowTree to delete
        a node. It will also instruct the corresponding node widget to delete
        itself.

        Parameters
        ----------
        node_id : int
            The node_id if the node to be deleted.
        """
        _ids = TREE.nodes[node_id].get_recursive_ids()
        TREE.delete_node_by_id(node_id)
        self._nodes[node_id].remove_node_from_tree()
        self.__delete_nodes_and_widgets(_ids)
        self.plugin_to_delete.emit(node_id)
        if len(TREE.node_ids) > 0:
            self.set_active_node(TREE.node_ids[-1])
            self.update_node_positions()
        else:
            self.plugin_to_edit.emit(-1)

    def __delete_nodes_and_widgets(self, ids):
        """
        Delete all nodes and widgets with corresponding IDs from the manager.

        Parameters
        ----------
        ids : list
            The list of integer widget/node IDs.
        """
        for _id in ids:
            self._node_widgets[_id].deleteLater()
        # wait to verify that widgets have had time to be removed
        time.sleep(0.0005)
        for _id in ids:
            del self._nodes[_id]
            del self._node_widgets[_id]
            del self._node_positions[_id]
        if len(self._nodes) == 0:
            self.root = None
            self.active_node_id = None
            self.qt_canvas.update_widget_connections([])


WorkflowTreeEditManager = SingletonFactory(_WorkflowTreeEditManager)

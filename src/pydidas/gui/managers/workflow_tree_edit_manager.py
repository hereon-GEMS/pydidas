# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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
Module with the WorkflowTreeEditManager which interfaces the WorkflowTree
with the editing Canvas.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["WorkflowTreeEditManager"]


import time
from typing import Iterable, Optional

import numpy as np
from qtpy import QtCore, QtGui, QtWidgets

from pydidas.core import SingletonFactory
from pydidas.plugins import PluginCollection
from pydidas.widgets.workflow_edit import PluginInWorkflowBox
from pydidas.workflow import PluginPositionNode, WorkflowTree


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

    sig_plugin_selected = QtCore.Signal(int)
    sig_plugin_class_selected = QtCore.Signal(str)
    sig_inconsistent_plugins = QtCore.Signal(list)
    sig_consistent_plugins = QtCore.Signal(list)

    PLUGIN_WIDGET_WIDTH = -1
    PLUGIN_WIDGET_HEIGHT = -1

    def __init__(self, qt_canvas: Optional[QtWidgets.QWidget] = None):
        """
        Set up the instance.

        Parameters
        ----------
        qt_canvas : QtWidget, optional
            The QtWidget which acts as canvas for the plugin workflow tree.
            The default is None.
        """
        super().__init__()
        self.qt_canvas = qt_canvas
        self.root = None
        self._node_positions = {}
        self._node_widgets = {}
        self._nodes = {}
        self.__qtapp = QtWidgets.QApplication.instance()
        if hasattr(self.__qtapp, "sig_font_size_changed"):
            self.__qtapp.sig_font_size_changed.connect(self.__app_font_changed)
            self.__qtapp.sig_font_family_changed.connect(self.__app_font_changed)
            self.__app_font_changed()
        PLUGIN_COLLECTION.sig_updated_plugins.connect(self.__delete_all_items)

    def update_qt_canvas(self, qt_canvas: Optional[QtWidgets.QWidget] = None):
        """
        Store references to the QtCanvas for drawing.

        This method stores an internal reference to the canvas.
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

    @QtCore.Slot()
    def reset(self):
        """
        Reset the current instance.
        """
        self.root = None
        self._node_positions = {}
        self._node_widgets = {}
        self._nodes = {}

    def add_new_plugin_node(
        self, name: str, title: str = "", parent_node_id: Optional[int] = None
    ):
        """
        Add a new plugin node to the workflow.

        Add a new plugin node to the workflow. The plugin type is determined
        by the name. An optional title can be used as name for the plugin
        widget but the title will be determined automatically from the plugin
        name if not selected.
        New plugins will always be created as children of the active plugin
        and it is the users responsibility to select the correct parent
        prior to calling this method or to use the parent_node_id keyword.

        Parameters
        ----------
        name : str
            The name of the plugin.
        title : str, optional
            The title of the plugin widget. If no title is given, this will default
            to the widget name. The default is an empty string.
        parent_node : Union[int, None], optional
            The id of the parent node, if given. If None, this will default to the
            WorkflowTree's active node.

        Raises
        ------
        Warning
            If the Qt drawing Canvas for the plugins has not been defined yet.
        """
        _plugin = PLUGIN_COLLECTION.get_plugin_by_plugin_name(name)()
        _parent = (
            TREE.active_node if parent_node_id is None else TREE.nodes[parent_node_id]
        )
        TREE.create_and_add_node(_plugin, parent=_parent)

        _node_id = TREE.active_node_id
        self.__create_position_node(_node_id)
        self.__create_widget(title if len(title) > 0 else name, _node_id)
        self.set_active_node(_node_id, force_update=True)
        if not self.qt_canvas:
            raise Warning("No QtCanvas defined. Nodes cannot be displayed")
        self.update_node_positions()
        self._check_consistency()

    def __create_position_node(self, node_id: int):
        """
        Create a new PluginPositionNode with the current node ID.

        Parameters
        ----------
        node_id : int
            The node ID.
        """
        _parent_id = (
            None
            if TREE.nodes[node_id].parent is None
            else TREE.nodes[node_id].parent.node_id
        )
        _parent = self._nodes.get(_parent_id, None)
        _node = PluginPositionNode(parent=_parent, node_id=node_id)
        self._nodes[node_id] = _node
        if self.root is None:
            self.root = _node

    def __create_widget(self, title: str, node_id: int, label: str = ""):
        """
        Create the widget associated with the Plugin to display the plugin
        position on the canvas.

        Parameters
        ----------
        title : str
            The plugin title.
        node_id : int
            The node ID. Required for referencing the widgets later.
        label : str, optional
            The plugin label. The default is an empty string.
        """
        _widget = PluginInWorkflowBox(
            title,
            node_id,
            parent=self.qt_canvas,
            label=label,
            standard_size=(self.PLUGIN_WIDGET_WIDTH, self.PLUGIN_WIDGET_HEIGHT),
        )
        _widget.sig_widget_activated.connect(self.set_active_node)
        _widget.sig_widget_delete_branch_request.connect(self.delete_branch)
        _widget.sig_widget_delete_request.connect(self.delete_node)
        _widget.sig_new_node_parent_request.connect(self.new_node_parent_request)
        _widget.sig_create_copy_request.connect(self.create_node_copy_request)
        self.sig_consistent_plugins.connect(_widget.receive_consistent_signal)
        self.sig_inconsistent_plugins.connect(_widget.receive_inconsistent_signal)
        _widget.setVisible(True)
        self.sig_plugin_selected.connect(_widget.new_widget_selected)
        self._node_widgets[node_id] = _widget

    @QtCore.Slot(int)
    def set_active_node(self, node_id: int, force_update: bool = False):
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
        if node_id not in self._nodes:
            return
        if node_id == TREE.active_node_id and not force_update:
            return
        TREE.active_node_id = node_id
        self.sig_plugin_selected.emit(node_id)
        self.sig_plugin_class_selected.emit(TREE.active_node.plugin.plugin_name)
        QtCore.QTimer.singleShot(20, QtWidgets.QApplication.instance().processEvents)

    @QtCore.Slot(str)
    def replace_plugin(self, plugin_name: str):
        """
        Replace the active node's Plugin by a new Plugin class.

        Parameters
        ----------
        plugin_name : str
            The name of the new Plugin.
        """
        _plugin = PLUGIN_COLLECTION.get_plugin_by_plugin_name(plugin_name)()
        TREE.replace_node_plugin(TREE.active_node_id, _plugin)
        self._node_widgets[TREE.active_node_id].update_plugin(plugin_name)
        self.sig_plugin_selected.emit(TREE.active_node_id)
        self._check_consistency()

    @QtCore.Slot(int, str)
    def new_node_label_selected(self, node_id: int, label: str):
        """
        Process the newly selected plugin label.

        Parameters
        ----------
        node_id : int
            The node ID to be updated
        label : str
            The new node label.
        """
        self._node_widgets[node_id].update_text(node_id, label)

    @QtCore.Slot(int, int)
    def new_node_parent_request(self, calling_node: int, new_parent_node: int):
        """
        Handle the signal that a node requested to have a new parent.

        Parameters
        ----------
        calling_node : int
            The node ID of the calling node.
        new_parent_node : int
            The node ID of the requested parent.
        """
        TREE.change_node_parent(calling_node, new_parent_node)
        TREE.order_node_ids()
        self.update_from_tree()
        self._check_consistency()

    @QtCore.Slot(int, int)
    def create_node_copy_request(self, calling_node: int, new_parent_node: int):
        """
        Handle the signal that a node requested to append a copy of itself to parent.

        Parameters
        ----------
        calling_node : int
            The node ID of the calling node.
        new_parent_node : int
            The node ID of the requested parent.
        """
        _plugin = TREE.nodes[calling_node].plugin
        _param_vals = _plugin.get_param_values_as_dict()
        self.add_new_plugin_node(_plugin.plugin_name, parent_node_id=new_parent_node)
        TREE.active_node.plugin.set_param_values_from_dict(_param_vals)
        TREE.order_node_ids()
        time.sleep(0.0005)
        self.update_from_tree()
        self._check_consistency()

    @QtCore.Slot()
    def update_node_positions(self):
        """
        Update the node positions on the canvas after changes to the tree.

        This method will reposition the nodes on the drawing canvas and link
        parents and children with lines to allow following the workflow.
        """
        if self.root is None:
            return
        _positions = self.root.get_relative_positions()
        _pos_vals = np.asarray(list(_positions.values()))
        _pos_vals[:, 0] *= self.PLUGIN_WIDGET_WIDTH
        _pos_vals[:, 1] *= self.PLUGIN_WIDGET_HEIGHT
        _pos_vals = np.round(_pos_vals).astype(int)
        self._node_positions = {key: _pos_vals[i] for i, key in enumerate(_positions)}
        for node_id in TREE.node_ids:
            self._node_widgets[node_id].move(
                self._node_positions[node_id][0], self._node_positions[node_id][1]
            )
        self.qt_canvas.setFixedSize(
            int(np.round(self.root.width * self.PLUGIN_WIDGET_WIDTH + 10)),
            int(np.round(self.root.height * self.PLUGIN_WIDGET_HEIGHT + 10)),
        )
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
            x0 = self._node_positions[node0][0] + self.PLUGIN_WIDGET_WIDTH // 2
            y0 = self._node_positions[node0][1] + self.PLUGIN_WIDGET_HEIGHT
            x1 = self._node_positions[node1][0] + self.PLUGIN_WIDGET_WIDTH // 2
            y1 = self._node_positions[node1][1]
            widget_conns.append([x0, y0, x1, y1])
        self.qt_canvas.update_widget_connections(widget_conns)

    def update_from_tree(self, reset_active_node: bool = False):
        """
        Update the canvas and nodes from the WorkflowTree.

        Parameters
        ----------
        reset_active_node : bool, optional
            Flag to toggle resetting the active node. After loading a
            WorkflowTree from file, this can be used to reset the selection.
        """
        self.__delete_all_items()
        for _node_id, _node in TREE.nodes.items():
            _name = _node.plugin.plugin_name
            _label = _node.plugin.get_param_value("label")
            self.__create_position_node(_node_id)
            self.__create_widget(_name, _node_id, label=_label)
        self.update_node_positions()
        self._check_consistency()
        if reset_active_node:
            self.sig_plugin_selected.emit(-1)
            TREE.active_node_id = None
            return
        self.set_active_node(TREE.active_node_id, force_update=True)

    def _check_consistency(self):
        """
        Check the WorkflowTree for data dimension consistency and send corresponding
        signals to the widgets to style themselves accordingly.
        """
        _consistent, _inconsistent = TREE.get_consistent_and_inconsistent_nodes()
        self.sig_consistent_plugins.emit(_consistent)
        self.sig_inconsistent_plugins.emit(_inconsistent)

    @QtCore.Slot()
    def __delete_all_items(self):
        """
        Delete all managed items.

        This includes all nodes and widgets.
        """
        _all_ids = list(self._node_widgets.keys())
        self.__delete_widgets(*_all_ids)
        self.__delete_references(*_all_ids)

    @QtCore.Slot(int)
    def delete_branch(self, node_id: int):
        """
        Remove a node and branch from the tree.

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
        self._nodes[node_id].delete_node_references()
        self.__delete_widgets(*[_id for _id in _ids if _id != node_id])
        self.__delete_references(*_ids)
        if len(TREE.node_ids) > 0:
            self.set_active_node(TREE.active_node_id, force_update=True)
            self.update_node_positions()
        else:
            self.sig_plugin_selected.emit(-1)

    @QtCore.Slot(int)
    def delete_node(self, node_id: int):
        """
        Remove a single node from the tree and connect its children to its parent.

        This method will send a signal to instruct the WorkflowTree to delete
        a node. It will also instruct the corresponding node widget to delete
        itself.

        Parameters
        ----------
        node_id : int
            The node_id if the node to be deleted.
        """
        if self._nodes[node_id] == self.root and self.root is not None:
            if self.root.n_children == 0:
                self.root = None
            elif self.root.n_children == 1:
                self.root = self.root.get_children()[0]
        self._nodes[node_id].connect_parent_to_children()
        self.__delete_references(node_id)
        TREE.delete_node_by_id(node_id, keep_children=True, recursive=False)
        if len(TREE.node_ids) > 0:
            self.set_active_node(TREE.active_node_id, force_update=True)
            self.update_node_positions()
        else:
            self.sig_plugin_selected.emit(-1)
        self._check_consistency()

    def __delete_references(self, *node_ids: Iterable[int]):
        """
        Delete the references for all specified managed nodes.

        Parameters
        ----------
        node_ids : Iterable[int]
            The list of node_ids to be dereferenced.
        """
        for _id in node_ids:
            del self._nodes[_id]
            del self._node_widgets[_id]
            del self._node_positions[_id]
        if len(self._nodes) == 0:
            self.root = None
            if self.qt_canvas is not None:
                self.qt_canvas.update_widget_connections([])

    def __delete_widgets(self, *node_ids: Iterable[int]):
        """
        Disconnect and delete all widgets with corresponding IDs from the manager.

        Parameters
        ----------
        *node_ids : Iterable[int]
            All integer widget/node IDs in any Iterable datatype.
        """
        for _id in node_ids:
            if _id in self._node_widgets:
                self._node_widgets[_id].disconnect()
                self._node_widgets[_id].deleteLater()

    @QtCore.Slot()
    def __app_font_changed(self):
        """
        Handle the QApplication's font changed signal and update the widgets.
        """
        _font = self.__qtapp.font()
        _font.setPointSizeF(self.__qtapp.font_size + 1)
        _metrics = QtGui.QFontMetrics(_font)
        _rect = _metrics.boundingRect("pyFAI azimuthal integration Test")
        self.PLUGIN_WIDGET_WIDTH = _width = _rect.width() + 10
        self.PLUGIN_WIDGET_HEIGHT = _height = int(self.PLUGIN_WIDGET_WIDTH / 4.2)
        for _widget in self._node_widgets.values():
            _widget.setFixedSize(QtCore.QSize(_width, _height))
        self.update_node_positions()


WorkflowTreeEditManager = SingletonFactory(_WorkflowTreeEditManager)

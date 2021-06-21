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

"""Module with the WorkflowCanvasManager."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['WorkflowCanvasManager']

import numpy as np

from PyQt5 import QtCore

from pydidas.config import gui_constants, qt_presets

from .workflow_plugin_position_node import WorkflowPluginPositionNode
from .workflow_plugin_label import WorkflowPluginLabel

PALETTES = qt_presets.PALETTES
STYLES = qt_presets.STYLES


class WorkflowCanvasManager(QtCore.QObject):
    """
    Manage the editing of the workflow tree.

    The WorkflowCanvasManager is designed as singleton to manage editing
    the workflow tree, plugin parameters and the corresponding plugins' QT
    widgets. It is responsible for creating widgets and placing them correctly
    on the canvas of the workflow editor. Most method names correspond to
    similar methods in WorkflowEditTreeManager class. This class should only
    be used by the WorkflowEditTreeManager to manage the widget aspect.
    """
    plugin_to_edit = QtCore.pyqtSignal(int)
    plugin_to_delete = QtCore.pyqtSignal(int)
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
        qt_main : QtMainWindow, optional
            Reference to the main application. The default is None.

        Returns
        -------
        None.
        """
        super().__init__()
        self.root = None
        self.qt_canvas= qt_canvas

        self.node_pos = {}
        self.widgets = {}
        self.nodes = {}
        self.node_ids = []
        self.active_node = None
        self.active_node_id = None

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

        Returns
        -------
        None.
        """
        if qt_canvas:
            self.qt_canvas = qt_canvas


    def add_plugin_node(self, name, node_id, title=None):
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
        node_id : int
            The id for the new node. This should be set by the calling manager.
        title : str, optional
            The title of the plugin widget. If None, this will default to the
            widget name. The default is None.

        Raises
        ------
        AttributeError
            AttributeError is raised if the Qt drawing Canvas for the plugins
            has not been defined yet.

        Returns
        -------
        None.
        """
        if node_id in self.node_ids:
            raise ValueError('Specified node_id not found.')

        title = title if title else name
        widget = WorkflowPluginLabel(self.qt_canvas, title, node_id)
        widget.widget_activated.connect(self.set_active_node)
        widget.widget_delete_request.connect(self.delete_node)
        widget.setVisible(True)
        node = WorkflowPluginPositionNode(self.active_node, node_id)
        if not self.root:
            self.root = node
        self.nodes[node_id] = node
        self.widgets[node_id] = widget
        self.node_ids.append(node_id)
        self.set_active_node(node_id)

        if not self.qt_canvas:
            # raise Warning('No QtCanvas defined. Nodes added but cannot be '
            #               'displayed')
            return
        self.update_node_positions()

    def update_node_positions(self):
        """
        Update the node positions on the canvas after changes to the tree.

        This method will reposition the nodes on the drawing canvas and link
        parents and children with lines to allow following the workflow.

        Raises
        ------
        KeyError
            If no root node exits.

        Returns
        -------
        None.
        """
        if not self.root:
            raise KeyError('No root node specified')
        _pos = self.root.get_relative_positions()
        _width = max(_pos.values())[0] + gui_constants.GENERIC_PLUGIN_WIDGET_WIDTH
        _offset = 0
        if _width < self.qt_canvas.parent().width():
            _offset = (self.qt_canvas.parent().width() - _width) // 2
        pos_vals = np.asarray(list(_pos.values()))
        pos_vals[:, 0] += - np.amin(pos_vals[:, 0]) + self.pos_x_min + _offset
        pos_vals[:, 1] += - np.amin(pos_vals[:, 1]) + self.pos_y_min
        self.node_pos = {}
        for i, key in enumerate(_pos):
            self.node_pos.update({key: pos_vals[i]})
        for node_id in self.node_ids:
            self.widgets[node_id].move(self.node_pos[node_id][0],
                                       self.node_pos[node_id][1])
        self.qt_canvas.setFixedSize(self.root.width + 2 * self.pos_x_min + _offset,
                                    self.root.height + 2 * self.pos_y_min)
        self.__update_node_connections()

    def __update_node_connections(self):
        """
        Update the node connections.

        This method will query the nodes - starting with root - about its
        children and all connections.

        Returns
        -------
        None.
        """
        node_conns = self.root.get_recursive_connections()
        widget_conns = []
        for node0, node1 in node_conns:
            x0 = self.node_pos[node0][0] + self.nodes[node1].generic_width // 2
            y0 = self.node_pos[node0][1] + self.nodes[node1].generic_height
            x1 = self.node_pos[node1][0] + self.nodes[node1].generic_width // 2
            y1 = self.node_pos[node1][1]
            widget_conns.append([x0, y0, x1, y1])
        self.qt_canvas.update_widget_connections(widget_conns)

    def set_active_node(self, node_id):
        """
        Set the node with node_id to be the active node.

        This method will

        Parameters
        ----------
        node_id : int
            The unique identifier for the node to be activated.

        Raises
        ------
        KeyError
            A KeyError is raised if the node_id key has not been registered
            with the manager yet.

        Returns
        -------
        None.
        """
        if node_id == self.active_node_id:
            return
        if node_id not in self.widgets:
            raise KeyError(f'The node_id "{node_id}" has not been registered.')
        for nid in self.widgets:
            if node_id == nid:
                self.widgets[nid].widget_select()
            else:
                self.widgets[nid].widget_deselect()
        self.active_node = self.nodes[node_id]
        self.active_node_id = node_id
        self.plugin_to_edit.emit(node_id)

    def delete_node(self, node_id):
        """
        Remove a node from the tree.

        This method will delete a node and remove it from the tree. It will
        also instruct the corresponding node widget to delete itself.

        Parameters
        ----------
        node_id : int
            The node_id if the node to be deleted.

        Returns
        -------
        None.
        """
        _all_ids = self.nodes[node_id].get_recursive_ids()
        self.nodes[node_id].delete_node()
        for _id in _all_ids:
            self.widgets[_id].deleteLater()
            del self.nodes[_id]
            del self.widgets[_id]
            del self.node_pos[_id]
        self.node_ids = [_id for _id in self.node_ids if _id not in _all_ids]
        self.__update_node_connections()
        if len(self.node_ids) == 0:
            self.root = None
            self.active_node = None
            self.active_node_id = None
            return
        self.set_active_node(self.node_ids[-1])
        self.update_node_positions()

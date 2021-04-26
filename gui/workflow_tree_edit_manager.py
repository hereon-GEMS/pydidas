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

"""Module with the WorkflowTreeEditManager."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['WorkflowEditTreeManager']

import numpy as np

from PyQt5 import QtCore, QtWidgets

from plugin_workflow_gui.plugin_collection import PluginCollection
from plugin_workflow_gui.config import gui_constants, qt_presets
from plugin_workflow_gui.workflow_tree import PluginPositionNode

PLUGIN_COLLECTION = PluginCollection()
PALETTES = qt_presets.PALETTES
STYLES = qt_presets.STYLES


class _WorkflowPluginWidget(QtWidgets.QLabel):
    """Widget with title and delete button for every selected plugin
    in the processing chain.

    Note: This class is part of the gui subpackage to avoid circular imports
    between this class and the WorkflowEditTreeManager.
    """
    widget_width = gui_constants.GENERIC_PLUGIN_WIDGET_WIDTH
    widget_height = gui_constants.GENERIC_PLUGIN_WIDGET_HEIGHT

    def __init__(self, parent=None, title='No title', widget_id=None):
        """
        Setup the _WorkflowPluginWidget.

        The setup method will create an instance of _WorkflowPluginWidget
        which is used to select/deselect plugins for parameter and workflow
        configuration.

        Parameters
        ----------
        parent : TYPE, optional
            DESCRIPTION. The default is None.
        title : TYPE, optional
            DESCRIPTION. The default is 'No title'.
        widget_id : TYPE, optional
            DESCRIPTION. The default is None.

        Raises
        ------
        ValueError
            DESCRIPTION.

        Returns
        -------
        None.

        """
        super().__init__(parent)
        self.qt_parent = parent
        self.active = False
        if widget_id is None:
            raise ValueError('No plugin node id given.')

        self.widget_id = widget_id
        self.setText(title)

        self.setFixedSize(self.widget_width, self.widget_height)
        self.setAutoFillBackground(True)
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)

        self.qtw_del_button = QtWidgets.QPushButton(self)
        self.qtw_del_button.setIcon(self.style().standardIcon(40))
        self.qtw_del_button.setGeometry(self.widget_width - 20, 2, 18, 18)
        for item in [self, self.qtw_del_button]:
            item.setStyleSheet(STYLES['workflow_plugin_inactive'])
        self.qtw_del_button.clicked.connect(self.delete)

    def mousePressEvent(self, event):
        event.accept()
        if not self.active:
            WORKFLOW_EDIT_MANAGER.set_active_node(self.widget_id)

    def delete(self):
        WORKFLOW_EDIT_MANAGER.delete_node(self.widget_id)

    def widget_select(self):
        self.setStyleSheet(STYLES['workflow_plugin_active'])
        self.active = True

    def widget_deselect(self):
        self.setStyleSheet(STYLES['workflow_plugin_inactive'])
        self.active = False


class _WorkflowEditTreeManager(QtCore.QObject):
    """
    Manage the editing of the workflow tree.

    The WorkflowEditTreeManager is designed as singleton to manage editing
    the workflow tree, plugin parameters and the corresponding plugins' QT
    widgets.
    """
    plugin_to_edit = QtCore.pyqtSignal(int)
    pos_x_min = 5
    pos_y_min = 5

    def __init__(self, qt_canvas=None, qt_main=None):
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
        self.qt_main = qt_main

        self.node_pos = {}
        self.widgets = {}
        self.nodes = {}
        self.plugins = {}
        self.node_ids = []
        self.active_node = None
        self.active_node_id = None

    def update_qt_items(self, qt_canvas=None, qt_main=None):
        """
        Store references to the QT items.

        This method stores internal references to the canvas and main window.
        Because the class is designed as singleton, this information will
        typically not be available at instantiation and needs to be supplied
        at runtime.

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
        if qt_canvas:
            self.qt_canvas = qt_canvas
        if qt_main:
            self.qt_main = qt_main

    def add_plugin_node(self, name, title=None):
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

        Returns
        -------
        None.
        """
        if not self.root:
            _newid = 0
        else:
            _newid = self.node_ids[-1] + 1

        title = title if title else name
        widget = _WorkflowPluginWidget(self.qt_canvas, title, _newid)
        widget.setVisible(True)
        node = PluginPositionNode(self.active_node, _newid)
        if not self.root:
            self.root = node
        self.nodes[_newid] = node
        self.widgets[_newid] = widget
        self.plugins[_newid] = PLUGIN_COLLECTION.get_plugin_by_name(name)()
        self.node_ids.append(_newid)
        self.set_active_node(_newid)
        self.update_node_positions()
        self.qt_main.update()

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
        if _width < self.qt_main.params['workflow_edit_canvas_x']:
            _offset = (self.qt_main.params['workflow_edit_canvas_x'] - _width) // 2
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
        node_id : TYPE
            DESCRIPTION.

        Raises
        ------
        KeyError
            A KeyError is raised if the node_id key has not been registered
            with the manager yet.

        Returns
        -------
        None.
        """
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
            del self.plugins[_id]
        self.node_ids = [_id for _id in self.node_ids if _id not in _all_ids]
        self.__update_node_connections()
        if len(self.node_ids) == 0:
            self.root = None
            self.active_node = None
            self.active_node_id = None
            return
        self.set_active_node(self.node_ids[-1])
        self.update_node_positions()


class _WorkflowEditTreeManagerFactory:
    """Factory to create a WorkflowEditTreeManager Singleton."""
    def __init__(self):
        """Factory setup method."""
        self._instance = None

    def __call__(self, **kwargs):
        """
        Factory call method to return the instance of
        WorkflowEditTreeManager.
        """
        if not self._instance:
            self._instance = _WorkflowEditTreeManager(**kwargs)
        return self._instance


WorkflowEditTreeManager = _WorkflowEditTreeManagerFactory()

WORKFLOW_EDIT_MANAGER = WorkflowEditTreeManager()
# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Module with the WorkflowTreeEditManager."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['WorkflowEditTreeManager']

from PyQt5 import QtCore

from pydidas.core import SingletonFactory
from pydidas.plugins import PluginCollection
from pydidas.widgets.workflow_edit import WorkflowCanvasManager

PLUGIN_COLLECTION = PluginCollection()


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

        self.canvas_manager = WorkflowCanvasManager(qt_canvas)
        self.canvas_manager.plugin_to_edit.connect(self.set_active_node)
        self.canvas_manager.plugin_to_delete.connect(self.delete_node)
        self.plugins = {}
        self.node_ids = []
        self.active_node_id = None

    def update_qt_canvas(self, qt_canvas):
        """
        Store references to the Qt items.

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
            self.canvas_manager.update_qt_canvas(qt_canvas)


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

        Raises
        ------
        AttributeError
            AttributeError is raised if the Qt drawing Canvas for the plugins
            has not been defined yet.
        """
        if not self.root:
            _newid = 0
        else:
            _newid = self.node_ids[-1] + 1

        self.node_ids.append(_newid)
        title = title if title else name
        self.plugins[_newid] = \
            PLUGIN_COLLECTION.get_plugin_by_plugin_name(name)()
        self.canvas_manager.add_plugin_node(name, _newid, title)
        if not self.root:
            self.root = True
        self.set_active_node(_newid)

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
        """
        if node_id != self.active_node_id:
            if node_id not in self.node_ids:
                raise KeyError(f'The node_id "{node_id}" has not been'
                               'registered.')
            self.canvas_manager.set_active_node(node_id)
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
        _all_ids = self.canvas_manager.nodes[node_id].get_recursive_ids()
        for _id in _all_ids:
            del self.plugins[_id]
        self.canvas_manager.delete_node(node_id)
        self.node_ids = [_id for _id in self.node_ids if _id not in _all_ids]
        if len(self.node_ids) == 0:
            self.root = None
            self.active_node_id = None
            return
        self.set_active_node(self.node_ids[-1])


WorkflowEditTreeManager = SingletonFactory(_WorkflowEditTreeManager)

WORKFLOW_EDIT_MANAGER = WorkflowEditTreeManager()

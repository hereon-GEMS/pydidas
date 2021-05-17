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

from PyQt5 import QtCore

from plugin_workflow_gui.plugin_collection import PluginCollection
from plugin_workflow_gui.widgets.workflow_edit import WorkflowCanvasManager

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
        qt_main : QtMainWindow, optional
            Reference to the main application. The default is None.

        Returns
        -------
        None.
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

        Returns
        -------
        None.
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

        Returns
        -------
        None.
        """
        if not self.root:
            _newid = 0
        else:
            _newid = self.node_ids[-1] + 1

        self.node_ids.append(_newid)

        title = title if title else name
        self.plugins[_newid] = PLUGIN_COLLECTION.get_plugin_by_name(name)()

        print('new id: ', _newid)
        print('start canvas_manager add plugin')
        self.canvas_manager.add_plugin_node(name, _newid, title)
        print('returned from canvas_manager add plugin')
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

        Returns
        -------
        None.
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

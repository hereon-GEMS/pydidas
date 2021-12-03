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

"""
Module with the WorkflowEditFrame which is used to create the WorkflowTree.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['WorkflowEditFrame']

from PyQt5 import QtCore, QtWidgets

from ..widgets import BaseFrame
from ..workflow import WorkflowTree
from ..workflow.workflow_tree_io import WorkflowTreeIoMeta
from .workflow_tree_edit_manager import WorkflowTreeEditManager
from .builders.workflow_edit_frame_builder import (
    create_workflow_edit_frame_widgets_and_layout)

TREE = WorkflowTree()
WORKFLOW_EDIT_MANAGER = WorkflowTreeEditManager()


class WorkflowEditFrame(BaseFrame):
    """
    The WorkflowEditFrame includes three major objects:
        a. The editing canvas which shows the WorkflowTree structure.
        b. A Plugin information and selection box to browse all available
           plugins and add them to the WorkflowTree.
        c. An editing panel to modify the Parameters for the individual
           plugins.
    """
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent)

        create_workflow_edit_frame_widgets_and_layout(self)

        self._widgets['plugin_collection'].selection_confirmed.connect(
            self.workflow_add_plugin)
        WORKFLOW_EDIT_MANAGER.plugin_to_edit.connect(self.configure_plugin)
        WORKFLOW_EDIT_MANAGER.update_qt_canvas(
            self._widgets['workflow_canvas'])
        self._widgets['but_save'].clicked.connect(self.save_tree_to_file)
        self._widgets['but_load'].clicked.connect(self.load_tree_from_file)

    @QtCore.pyqtSlot(str)
    def workflow_add_plugin(self, name):
        """
        Get the signal that a new Plugin has been selected and must be added
        to the WorkflowTree and forward it to the WorkflowTreeEditManager.

        Parameters
        ----------
        name : str
            The name of the new Plugin.
        """
        WORKFLOW_EDIT_MANAGER.add_new_plugin_node(name)

    @QtCore.pyqtSlot(int)
    def configure_plugin(self, node_id):
        """
        Get the signal that a new Plugin has been selected to be edited and
        pass the information to the PluginEditCanvas.

        Parameters
        ----------
        node_id : int
            The Plugin node ID.
        """
        if node_id == -1:
            self._widgets['plugin_edit_canvas'].clear_layout()
            return
        plugin = TREE.nodes[node_id].plugin
        self._widgets['plugin_edit_canvas'].configure_plugin(node_id, plugin)

    def save_tree_to_file(self):
        """
        Open a QFileDialog to geta save name and export the WorkflowTree to
        the selected file with the specified format.
        """
        _file_selection = WorkflowTreeIoMeta.get_string_of_formats()
        _func = QtWidgets.QFileDialog.getSaveFileName
        fname = _func(self, 'Name of file', None, _file_selection)[0]
        if fname in ['', None]:
            return
        TREE.export_to_file(fname, overwrite=True)

    def load_tree_from_file(self):
        """
        Open a Qdialog to select a filename, read the file and import an
        existing WorkflowTree from the retrieved information.
        """
        _file_selection = WorkflowTreeIoMeta.get_string_of_formats()
        _func = QtWidgets.QFileDialog.getOpenFileName
        fname = _func(self, 'Name of file', None, _file_selection)[0]
        if fname in ['', None]:
            return
        TREE.import_from_file(fname)
        WORKFLOW_EDIT_MANAGER.update_from_tree()

    @QtCore.pyqtSlot(int)
    def frame_activated(self, index):
        """
        Overload the frame_activated method of the BaseFrame class to update
        the synchronize the displayed Tree with the WorkflowTree singleton.

        Parameters
        ----------
        index : int
            The frame index.
        """
        if self.frame_index == index:
            WORKFLOW_EDIT_MANAGER.update_from_tree()


if __name__ == '__main__':
    import pydidas
    from pydidas.gui.main_window import MainWindow
    import sys
    import qtawesome as qta
    app = QtWidgets.QApplication(sys.argv)
    #app.setStyle('Fusion')

    # needs to be initialized after the app has been created.
    # sys.excepthook = pydidas.widgets.excepthook
    CENTRAL_WIDGET_STACK = pydidas.widgets.CentralWidgetStack()
    STANDARD_FONT_SIZE = pydidas.constants.STANDARD_FONT_SIZE

    _font = app.font()
    _font.setPointSize(STANDARD_FONT_SIZE)
    app.setFont(_font)
    gui = MainWindow()

    gui.register_frame('Test', 'Test', qta.icon('mdi.clipboard-flow-outline'),
                       WorkflowEditFrame)
    gui.create_toolbars()

    gui.show()
    sys.exit(app.exec_())
    app.deleteLater()

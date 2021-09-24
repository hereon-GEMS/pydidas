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

"""Module with the WorkflowEditFrame which is used to create the workflow
tree."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['WorkflowEditFrame']

from PyQt5 import QtCore

from pydidas.gui.workflow_tree_edit_manager import WorkflowTreeEditManager
from pydidas.widgets import BaseFrame
from pydidas.gui.builders.workflow_edit_frame_builder import (
    create_workflow_edit_frame_widgets_and_layout)
from pydidas.workflow_tree import WorkflowTree

TREE = WorkflowTree()
WORKFLOW_EDIT_MANAGER = WorkflowTreeEditManager()


class WorkflowEditFrame(BaseFrame):
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent)

        create_workflow_edit_frame_widgets_and_layout(self)

        self._widgets['plugin_collection'].selection_confirmed.connect(
            self.workflow_add_plugin)
        WORKFLOW_EDIT_MANAGER.plugin_to_edit.connect(self.configure_plugin)
        WORKFLOW_EDIT_MANAGER.update_qt_canvas(
            self._widgets['workflow_canvas'])

    @QtCore.pyqtSlot(str)
    def workflow_add_plugin(self, name):
        WORKFLOW_EDIT_MANAGER.add_new_plugin_node(name)

    @QtCore.pyqtSlot(int)
    def configure_plugin(self, node_id):
        plugin = TREE.nodes[node_id].plugin
        self._widgets['plugin_edit_canvas'].configure_plugin(node_id, plugin)


if __name__ == '__main__':
    import pydidas
    from pydidas.gui.main_window import MainWindow
    import sys
    import qtawesome as qta
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication(sys.argv)
    #app.setStyle('Fusion')

    # needs to be initialized after the app has been created.
    # sys.excepthook = pydidas.widgets.excepthook
    CENTRAL_WIDGET_STACK = pydidas.widgets.CentralWidgetStack()
    STANDARD_FONT_SIZE = pydidas.config.STANDARD_FONT_SIZE

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

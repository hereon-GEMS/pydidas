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

"""Module with the WorkflowEditFrame which is used to create the workflow
tree."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['WorkflowEditFrame']

from PyQt5 import QtCore

from .workflow_tree_edit_manager import WORKFLOW_EDIT_MANAGER
from ..widgets import BaseFrame
from .builders.workflow_edit_frame_builder import (
    create_workflow_edit_frame_widgets_and_layout)


class WorkflowEditFrame(BaseFrame):
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent)

        create_workflow_edit_frame_widgets_and_layout(self)

        self._widgets['plugin_collection'].selection_confirmed.connect(
            self.workflow_add_plugin)
        WORKFLOW_EDIT_MANAGER.update_qt_canvas(
            self._widgets['workflow_canvas'])
        WORKFLOW_EDIT_MANAGER.plugin_to_edit.connect(self.configure_plugin)

    def workflow_add_plugin(self, name):
        WORKFLOW_EDIT_MANAGER.add_plugin_node(name)

    @QtCore.pyqtSlot(int)
    def configure_plugin(self, node_id):
        plugin = WORKFLOW_EDIT_MANAGER.plugins[node_id]
        self._widgets['plugin_edit_canvas'].configure_plugin(node_id, plugin)

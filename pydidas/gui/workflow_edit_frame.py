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

from PyQt5 import QtWidgets, QtCore

from ..widgets import (WorkflowTreeCanvas, PluginCollectionPresenter,
                       ScrollArea)
from ..widgets.parameter_config import PluginParameterConfigWidget
from ..config.gui_constants import (WORKFLOW_EDIT_CANVAS_X,
                                    WORKFLOW_EDIT_CANVAS_Y)
from .workflow_tree_edit_manager import WORKFLOW_EDIT_MANAGER
from .base_frame import BaseFrame

class WorkflowEditFrame(BaseFrame):
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent)
        params = kwargs.get('params', {})
        self.params = {
            'workflow_edit_canvas_x': params.get('workflow_edit_canvas_x',
                                                 WORKFLOW_EDIT_CANVAS_X),
            'workflow_edit_canvas_y': params.get('workflow_edit_canvas_y',
                                                 WORKFLOW_EDIT_CANVAS_Y)}


        self.w_workflow_canvas = WorkflowTreeCanvas(self)
        self.w_plugin_edit_canvas = PluginParameterConfigWidget(self)
        self.w_plugin_collection = PluginCollectionPresenter(self)
        self.w_workflow_area = ScrollArea(
            self, widget=self.w_workflow_canvas, minimumHeight=500)
        self.w_plugin_edit_area = ScrollArea(
            self, widget=self.w_plugin_edit_canvas, fixedWidth=400,
            minimumHeight=500)
        self.w_plugin_edit_area.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                              QtWidgets.QSizePolicy.Expanding)

        self.w_plugin_collection.selection_confirmed.connect(
            self.workflow_add_plugin)

        self.w_save_button= QtWidgets.QPushButton('save workflow')
        _layout = self.layout()
        _layout.addWidget(self.w_workflow_area, 0, 0, 1, 1)
        _layout.addWidget(self.w_plugin_collection, 1, 0, 2, 1)
        _layout.addWidget(self.w_plugin_edit_area, 0, 1, 2, 1)
        _layout.addWidget(self.w_save_button, 2, 1, 1, 1)
        # _layout.addWidget()
        self.setLayout(_layout)

        WORKFLOW_EDIT_MANAGER.update_qt_canvas(self.w_workflow_canvas)
        WORKFLOW_EDIT_MANAGER.plugin_to_edit.connect(self.configure_plugin)

    def workflow_add_plugin(self, name):
        WORKFLOW_EDIT_MANAGER.add_plugin_node(name)

    @QtCore.pyqtSlot(int)
    def configure_plugin(self, node_id):
        plugin = WORKFLOW_EDIT_MANAGER.plugins[node_id]
        self.w_plugin_edit_canvas.configure_plugin(node_id, plugin)

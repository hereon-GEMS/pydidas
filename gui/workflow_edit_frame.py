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

"""Module with the WorkflowEditFrame which is used to create the workflow
tree."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['WorkflowEditFrame']

from PyQt5 import QtWidgets, QtCore

from ..widgets import (WorkflowTreeCanvas, PluginCollectionPresenter,
                       ScrollArea)
from ..widgets.param_config import PluginParamConfig
from ..config.gui_constants import (WORKFLOW_EDIT_CANVAS_X,
                                    WORKFLOW_EDIT_CANVAS_Y)
from .workflow_tree_edit_manager import WORKFLOW_EDIT_MANAGER
from .toplevel_frame import ToplevelFrame

class WorkflowEditFrame(ToplevelFrame):
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent, initLayout=False)
        params = kwargs.get('params', {})
        self.params = {
            'workflow_edit_canvas_x': params.get('workflow_edit_canvas_x',
                                                 WORKFLOW_EDIT_CANVAS_X),
            'workflow_edit_canvas_y': params.get('workflow_edit_canvas_y',
                                                 WORKFLOW_EDIT_CANVAS_Y)}


        self.w_workflow_canvas = WorkflowTreeCanvas(self)
        self.w_plugin_edit_canvas = PluginParamConfig(self)
        self.w_plugin_collection = PluginCollectionPresenter(self)
        self.w_workflow_area = ScrollArea(
            self, widget=self.w_workflow_canvas, minHeight=500)
        self.w_plugin_edit_area = ScrollArea(
            self, widget=self.w_plugin_edit_canvas, fixedWidth=400,
            minHeight=500)
        self.w_plugin_edit_area.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                              QtWidgets.QSizePolicy.Expanding)

        self.w_plugin_collection.selection_confirmed.connect(
            self.workflow_add_plugin)

        self.w_save_button= QtWidgets.QPushButton('save workflow')
        _layout = QtWidgets.QGridLayout(self)
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
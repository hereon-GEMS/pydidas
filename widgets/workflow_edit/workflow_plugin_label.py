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

"""Module with the WorkflowPluginWidget which is used to create the workflow
tree."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

from PyQt5 import QtWidgets, QtCore
from plugin_workflow_gui.config import gui_constants, qt_presets

class WorkflowPluginLabel(QtWidgets.QLabel):
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
            item.setStyleSheet(qt_presets.STYLES['workflow_plugin_inactive'])
        self.qtw_del_button.clicked.connect(self.delete)

    def mousePressEvent(self, event):
        event.accept()
        if not self.active:
            WORKFLOW_EDIT_MANAGER.set_active_node(self.widget_id)

    def delete(self):
        WORKFLOW_EDIT_MANAGER.delete_node(self.widget_id)

    def widget_select(self):
        self.setStyleSheet(qt_presets.STYLES['workflow_plugin_active'])
        self.active = True

    def widget_deselect(self):
        self.setStyleSheet(qt_presets.STYLES['workflow_plugin_inactive'])
        self.active = False
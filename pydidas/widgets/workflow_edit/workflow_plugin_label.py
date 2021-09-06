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

"""Module with the WorkflowPluginWidget which is used to create the workflow
tree."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

from PyQt5 import QtWidgets, QtCore
from pydidas.config import gui_constants, qt_presets

class WorkflowPluginLabel(QtWidgets.QLabel):
    """Widget with title and delete button for every selected plugin
    in the processing chain.

    Note: This class is part of the gui subpackage to avoid circular imports
    between this class and the WorkflowEditTreeManager.
    """
    widget_width = gui_constants.GENERIC_PLUGIN_WIDGET_WIDTH
    widget_height = gui_constants.GENERIC_PLUGIN_WIDGET_HEIGHT
    widget_activated = QtCore.pyqtSignal(int)
    widget_delete_request = QtCore.pyqtSignal(int)

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
            self.widget_activated.emit(self.widget_id)

    def delete(self):
        self.widget_delete_request.emit(self.widget_id)

    def widget_select(self):
        self.setStyleSheet(qt_presets.STYLES['workflow_plugin_active'])
        self.active = True

    def widget_deselect(self):
        self.setStyleSheet(qt_presets.STYLES['workflow_plugin_inactive'])
        self.active = False

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

"""Module with the PluginParameterConfigWidget class used to edit plugin parameters."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['PluginParameterConfigWidget']

from functools import partial

from PyQt5 import QtWidgets, QtCore
from .parameter_config_widget import ParameterConfigWidget

from ..utilities import deleteItemsOfLayout


class PluginParameterConfigWidget(ParameterConfigWidget):
    """
    The PluginParameterConfigWidget widget creates the composite widget for updating
    parameters and changing default values.

    Depending on the parameter types, automatic typechecks are implemented.
    """
    def __init__(self, parent=None):
        """
        Setup method.

        Create an instance on the PluginParameterConfigWidget class.

        Parameters
        ----------
        parent : QtWidget, optional
            The parent widget. The default is None.

        Returns
        -------
        None.
        """
        super().__init__(parent=parent)
        self.plugin = None
        self.param_widgets = {}

    def configure_plugin(self, node_id, plugin):
        """
        Update the panel to show the parameters of a different plugin.

        This method clears the widget and populates it again with the
        parameters of the new plugin, defined by the plugin node_id

        Parameters
        ----------
        node_id : int
            The node_id in the workflow edit tree.
        plugin : object
            The instance of the Plugin to be edited.

        Returns
        -------
        None.
        """
        self.plugin = plugin
        self.param_widgets = {}
        _layout = self.layout()
        #delete current widgets
        for i in reversed(range(_layout.count())):
            item = _layout.itemAt(i)
            if isinstance(item, QtWidgets.QLayout):
                deleteItemsOfLayout(item)
                _layout.removeItem(item)
                item.deleteLater()
            elif isinstance(item.widget(), QtWidgets.QWidget):
                widgetToRemove = item.widget()
                _layout.removeWidget(widgetToRemove)
                widgetToRemove.setParent(None)
                widgetToRemove.deleteLater()

        #setup new widgets:
        self.add_label(f'Plugin: {self.plugin.plugin_name}', fontsize=12,
                       width=385)
        self.add_label(f'Node id: {node_id}', fontsize=12)
        self.add_label('\nParameters:', fontsize=12)
        if self.plugin.has_unique_parameter_config_widget():
            _layout.add(self.plugin.parameter_config_widget())
        else:
            self.restore_default_button()
            for param in self.plugin.params:
                self.add_param(param)

    def restore_default_button(self):
        """
        Restore default values for all parameters.

        This method is called on clicks on the "Restore defaults" button and
        will reset all parameter to their default values.

        Returns
        -------
        None.
        """
        but = QtWidgets.QPushButton(self.style().standardIcon(59),
                                    'Restore default parameters')
        but.clicked.connect(partial(self.plugin.restore_defaults, force=True))
        but.clicked.connect(self.update_edits)
        but.setFixedHeight(25)
        self.layout().addWidget(but, 0, QtCore.Qt.AlignRight)

    def update_edits(self):
        """
        Update the input fields with the stored parameter values.

        This method will go through all plugin parameters and populates
        the input fields with the stores parameter values.

        Returns
        -------
        None.
        """
        for param in self.plugin.params:
            self.param_widgets[param.name].set_value(param.value)

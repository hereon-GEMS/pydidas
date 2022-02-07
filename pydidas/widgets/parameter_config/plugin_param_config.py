# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the PluginParameterConfigWidget class used to edit plugin
Parameters.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['PluginParameterConfigWidget']

from functools import partial
from pathlib import Path

from PyQt5 import QtWidgets, QtCore

from ...core import Hdf5key
from ..factory import CreateWidgetsMixIn
from ..utilities import delete_all_items_in_layout
from .parameter_edit_frame import ParameterEditFrame


class PluginParameterConfigWidget(ParameterEditFrame, CreateWidgetsMixIn):
    """
    The PluginParameterConfigWidget widget creates the composite widget for
    updating and changing values of all Parameters in a Plugin.

    Depending on the Parameter types, automatic typechecks are implemented.
    """
    FIXED_WIDTH = 385

    def __init__(self, parent=None):
        """
        Setup method.

        Create an instance on the PluginParameterConfigWidget class.

        Parameters
        ----------
        parent : QtWidget, optional
            The parent widget. The default is None.
        """
        ParameterEditFrame.__init__(self, parent)
        CreateWidgetsMixIn.__init__(self)
        self.plugin = None
        self.node_id = None
        self.setFixedWidth(self.FIXED_WIDTH)

    def configure_plugin(self, node_id, plugin):
        """
        Update the panel to show the Parameters of a different Plugin.

        This method clears the widget and populates it again with the
        Parameters of the new Plugin, defined by the Plugin node_id

        Parameters
        ----------
        node_id : int
            The node_id in the workflow edit tree.
        plugin : object
            The instance of the Plugin to be edited.
        """
        self.clear_layout()
        self.plugin = plugin
        self.node_id = node_id
        self.__create_widgets_for_new_plugin()

    def clear_layout(self):
        """
        Delete all widgets and items which currently populate the
        PluginParameterConfigWidget.
        """
        #delete current widgets
        _layout = self.layout()
        for i in reversed(range(_layout.count())):
            item = _layout.itemAt(i)
            if isinstance(item, QtWidgets.QLayout):
                delete_all_items_in_layout(item)
                _layout.removeItem(item)
                item.deleteLater()
            elif isinstance(item.widget(), QtWidgets.QWidget):
                _widget_to_remove = item.widget()
                _layout.removeWidget(_widget_to_remove)
                _widget_to_remove.setParent(None)
                _widget_to_remove.deleteLater()
            elif isinstance(item, QtWidgets.QSpacerItem):
                _layout.removeItem(item)
        self.param_widgets = {}
        self.param_composite_widgets = {}

    def __create_widgets_for_new_plugin(self):
        """
        Create the required widgets for the new plugin.
        """
        self.create_label('plugin_name', f'Plugin: {self.plugin.plugin_name}',
                          fontsize=12, fixedWidth=self.FIXED_WIDTH,
                          gridPos=(0, 0, 1, 2))
        self.create_label('node_id', f'Node ID: {self.node_id}', fontsize=12,
                          gridPos=(1, 0, 1, 2))
        self.create_spacer('spacer', gridPos=(2, 0, 1, 2))
        self.create_label('params', 'Parameters:', fontsize=12,
                          gridPos=(3, 0, 1, 1))
        if self.plugin.has_unique_parameter_config_widget:
            self.layout().add(self.plugin.get_parameter_config_widget())
        else:
            self.__add_restore_default_button()
            for param in self.plugin.params.values():
                _kwargs = self.__get_param_creation_kwargs(param)
                self.create_param_widget(param, **_kwargs)

    def __add_restore_default_button(self):
        """
        Add a "Restore default values" button for all Parameters.

        This method will create a button to restore the defaults and connect
        the required slot.
        """
        self.create_button('restore_defaults', 'Restore default parameters',
                           icon=self.style().standardIcon(59), fixedHeight=25,
                           layout_kwargs={'gridPos': (2, 1, 1, 1),
                                          'alignment': QtCore.Qt.AlignRight})
        self._widgets['restore_defaults'].clicked.connect(
            self.__restore_defaults)

    @QtCore.pyqtSlot()
    def __restore_defaults(self):
        """
        Restore the default values to all Plugin Parameters.
        """
        self.plugin.restore_all_defaults(confirm=True)
        self.update_edits()

    def __get_param_creation_kwargs(self, param):
        """
        Get the kwargs to create the widgets for the Parameter in different
        styles for the different types of keys.

        Parameters
        ----------
        param : pydidas.core.Parameter
            The Parameter for which an I/O widget shall be created.

        Returns
        -------
        _kwargs : dict
            The kwargs to be used for widget creation.
        """
        if param.type in [Hdf5key, Path]:
            _kwargs = {'width_text': self.FIXED_WIDTH - 50,
                       'width_io': self.FIXED_WIDTH - 80,
                       'width_unit': 0,
                       'width_total': self.FIXED_WIDTH,
                       'linebreak': True}
                       #'halign_text': QtCore.Qt.AlignLeft}
        else:
            _kwargs = {'width_text': 200,
                       'width_io': self.FIXED_WIDTH - 240,
                       'width_total': self.FIXED_WIDTH}
        return _kwargs

    def update_edits(self):
        """
        Update the input fields with the stored parameter values.

        This method will go through all plugin parameters and populates
        the input fields with the stores parameter values.
        """
        for param in self.plugin.params.values():
            self.param_widgets[param.refkey].set_value(param.value)

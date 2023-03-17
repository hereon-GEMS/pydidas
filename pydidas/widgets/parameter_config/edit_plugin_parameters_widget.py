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
Module with the EditPluginParametersWidget class used to edit plugin
Parameters.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["EditPluginParametersWidget"]

from pathlib import Path

from qtpy import QtWidgets, QtCore

from ...core import Hdf5key, constants
from ..factory import CreateWidgetsMixIn
from ..utilities import delete_all_items_in_layout
from .parameter_edit_canvas import ParameterEditCanvas


class EditPluginParametersWidget(ParameterEditCanvas, CreateWidgetsMixIn):
    """
    The EditPluginParametersWidget widget creates the composite widget for
    updating and changing values of all Parameters in a Plugin.

    Depending on the Parameter types, automatic typechecks are implemented.
    """

    sig_new_label = QtCore.Signal(int, str)

    def __init__(self, **kwargs):
        """
        Setup method.

        Create an instance on the EditPluginParametersWidget class.

        Parameters
        ----------
        parent : QtWidget, optional
            The parent widget. The default is None.
        """
        ParameterEditCanvas.__init__(self, **kwargs)
        CreateWidgetsMixIn.__init__(self)
        self.plugin = None
        self.node_id = None
        self.setFixedWidth(constants.PLUGIN_PARAM_WIDGET_WIDTH)

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
        EditPluginParametersWidget.
        """
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
        self.create_label(
            "plugin_name",
            f"\nPlugin: {self.plugin.plugin_name}",
            fontsize=constants.STANDARD_FONT_SIZE + 1,
            bold=True,
            fixedWidth=constants.PLUGIN_PARAM_WIDGET_WIDTH,
            gridPos=(0, 0, 1, 2),
        )
        if self.node_id is not None:
            self.create_label(
                "node_id",
                f"Node ID: {self.node_id}",
                fontsize=constants.STANDARD_FONT_SIZE + 2,
                gridPos=(1, 0, 1, 2),
            )
        self.create_spacer("spacer", gridPos=(2, 0, 1, 2))
        self.create_label(
            "params",
            "Parameters:",
            fontsize=constants.STANDARD_FONT_SIZE + 2,
            gridPos=(3, 0, 1, 1),
        )
        self.__add_restore_default_button()
        if self.plugin.has_unique_parameter_config_widget:
            self.add_any_widget(
                "plugin_widget",
                self.plugin.get_parameter_config_widget(),
                gridPos=(-1, 0, 1, 2),
            )
        else:
            for param in self.plugin.params.values():
                _kwargs = (
                    constants.DEFAULT_TWO_LINE_PLUGIN_PARAM_CONFIG
                    if param.dtype in [Hdf5key, Path]
                    else constants.DEFAULT_PLUGIN_PARAM_CONFIG
                )
                self.create_param_widget(param, **_kwargs)
            self.param_widgets["label"].io_edited.connect(self._label_updated)

    @QtCore.Slot(str)
    def _label_updated(self, label):
        """
        Process the updated label and emit a signal.

        Parameters
        ----------
        label : str
            The new label.
        """
        self.sig_new_label.emit(self.plugin.node_id, label)

    def __add_restore_default_button(self):
        """
        Add a "Restore default values" button for all Parameters.

        This method will create a button to restore the defaults and connect
        the required slot.
        """
        self.create_button(
            "restore_defaults",
            "Restore default parameters",
            icon=self.style().standardIcon(59),
            fixedHeight=25,
            fixedWidth=225,
            layout_kwargs={"gridPos": (2, 0, 1, 2), "alignment": QtCore.Qt.AlignRight},
        )
        self._widgets["restore_defaults"].clicked.connect(self.__restore_defaults)

    @QtCore.Slot()
    def __restore_defaults(self):
        """
        Restore the default values to all Plugin Parameters.
        """
        self.plugin.restore_all_defaults(confirm=True)
        self.update_edits()

    def update_edits(self):
        """
        Update the input fields with the stored parameter values.

        This method will go through all plugin parameters and populates
        the input fields with the stores parameter values.
        """
        if self.plugin.has_unique_parameter_config_widget:
            self._widgets["plugin_widget"].update_edits()
            return
        for param in self.plugin.params.values():
            self.update_widget_value(param.refkey, param.value)

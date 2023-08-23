# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the EditPluginParametersWidget widget used to display and edit the
Parameters of a Plugin.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["EditPluginParametersWidget"]


from pathlib import Path

from qtpy import QtCore, QtWidgets
from qtpy.QtWidgets import QStyle

from ...core import Hdf5key, constants
from ...core.constants import PLUGIN_PARAM_EDIT_ASPECT_RATIO, POLICY_FIX_EXP
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
        self.setFixedWidth(
            int(
                QtWidgets.QApplication.instance().standard_font_height
                * PLUGIN_PARAM_EDIT_ASPECT_RATIO
                + 25
            )
        )
        self.__qtapp = QtWidgets.QApplication.instance()
        self.__qtapp.sig_new_font_height.connect(self.__update_width)

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
        self.__advanced_hidden = True
        self.__add_header()
        if self.plugin.has_unique_parameter_config_widget:
            self.__add_unique_config_widget()
        else:
            self.__add_generic_param_widgets()
        self.create_empty_widget("final_spacer", sizePolicy=POLICY_FIX_EXP)

    def clear_layout(self):
        """
        Clear all items from the layout and generate a new layout.
        """
        self.param_widgets = {}
        self.param_composite_widgets = {}
        self._widgets = {}
        delete_all_items_in_layout(self.layout())
        QtWidgets.QApplication.instance().sendPostedEvents(
            None, QtCore.QEvent.DeferredDelete
        )

    def __add_header(self):
        """
        Add the header with label and a restore default button.
        """
        self.create_label(
            "plugin_name",
            f"Plugin: {self.plugin.plugin_name}",
            fontsize_offset=1,
            bold=True,
            gridPos=(0, 0, 1, 2),
        )
        if self.node_id is not None:
            self.create_label(
                "node_id",
                f"Node ID: {self.node_id}",
                fontsize_offset=2,
                gridPos=(1, 0, 1, 2),
            )
        self.create_spacer("spacer", gridPos=(2, 0, 1, 2))
        self.create_label(
            "params",
            "Parameters:",
            fontsize_offset=2,
            gridPos=(3, 0, 1, 1),
        )
        self.create_button(
            "restore_defaults",
            "Restore default parameters",
            icon="qt-std::SP_BrowserReload",
            gridPos=(2, 0, 1, 2),
        )
        self._widgets["restore_defaults"].clicked.connect(self.__restore_defaults)

    def __add_unique_config_widget(self):
        """
        Add the unique config widget for the selected plugin.
        """
        self.add_any_widget(
            "plugin_widget",
            self.plugin.get_parameter_config_widget(),
            gridPos=(-1, 0, 1, 2),
        )
        self._widgets["plugin_widget"].param_widgets["label"].io_edited.connect(
            self._label_updated
        )

    def __add_generic_param_widgets(self):
        """
        Add the generic param widgets for standard plugins.
        """
        for param in self.plugin.params.values():
            if (
                param.refkey not in self.plugin.advanced_parameters
                and not param.refkey.startswith("_")
            ):
                _kwargs = {"linebreak": param.dtype in [Hdf5key, Path]}
                self.create_param_widget(param, **_kwargs)
        if len(self.plugin.advanced_parameters) > 0:
            self.__advanced_hidden = True
            self.create_button(
                "but_toggle_advanced_params",
                "Display advanced Parameters",
                icon="qt-std::SP_TitleBarUnshadeButton",
                width=constants.PLUGIN_PARAM_WIDGET_WIDTH,
            )
            for _key in self.plugin.advanced_parameters:
                _param = self.plugin.get_param(_key)
                _kwargs = {
                    "linebreak": param.dtype in [Hdf5key, Path],
                    "visible": False,
                }
                self.create_param_widget(_param, **_kwargs)
            self._widgets["but_toggle_advanced_params"].clicked.connect(
                self.__toggle_advanced_params
            )
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

    @QtCore.Slot()
    def __restore_defaults(self):
        """
        Restore the default values to all Plugin Parameters.

        This method will update both the plugin Parameters as well as the displayed
        widget values.
        """
        self.plugin.restore_all_defaults(confirm=True)
        if self.plugin.has_unique_parameter_config_widget:
            self._widgets["plugin_widget"].update_edits()
            return
        for param in self.plugin.params.values():
            self.update_widget_value(param.refkey, param.value)

    @QtCore.Slot()
    def __toggle_advanced_params(self):
        """
        Toggle the visiblity of the advanced Parameters.
        """
        self.__advanced_hidden = not self.__advanced_hidden
        for _key in self.plugin.advanced_parameters:
            self.toggle_param_widget_visibility(_key, not self.__advanced_hidden)
        self._widgets["but_toggle_advanced_params"].setText(
            "Display advanced Parameters"
            if self.__advanced_hidden
            else "Hide advanced Parameters"
        )
        self._widgets["but_toggle_advanced_params"].setIcon(
            self.style().standardIcon(
                QStyle.SP_TitleBarUnshadeButton
                if self.__advanced_hidden
                else QStyle.SP_TitleBarShadeButton
            )
        )

    @QtCore.Slot(float)
    def __update_width(self, font_height: float):
        """
        Update the width based on the font height to achieve a constant aspect ratio.

        Parameters
        ----------
        font_height : float
            The font height in pixels.
        """
        self.setFixedWidth(int(PLUGIN_PARAM_EDIT_ASPECT_RATIO * font_height))

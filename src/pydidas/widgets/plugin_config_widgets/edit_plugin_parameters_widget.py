# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["EditPluginParametersWidget"]


from qtpy import QtCore, QtWidgets

from pydidas.core.constants import FONT_METRIC_PARAM_EDIT_WIDTH, POLICY_FIX_EXP
from pydidas.plugins import BasePlugin
from pydidas.widgets.factory import CreateWidgetsMixIn, EmptyWidget
from pydidas.widgets.parameter_config.parameter_widgets_mixin import (
    ParameterWidgetsMixIn,
)
from pydidas.widgets.plugin_config_widgets.generic_plugin_config_widget import (
    GenericPluginConfigWidget,
)
from pydidas.widgets.utilities import delete_all_items_in_layout


class EditPluginParametersWidget(
    EmptyWidget, ParameterWidgetsMixIn, CreateWidgetsMixIn
):
    """
    The EditPluginParametersWidget widget creates the composite widget for
    updating and changing values of all Parameters in a Plugin.

    Depending on the Parameter types, automatic typechecks are implemented.
    """

    sig_new_label = QtCore.Signal(int, str)

    def __init__(self, **kwargs: dict):
        """
        Setup method.

        Create an instance on the EditPluginParametersWidget class.

        Parameters
        ----------
        parent : QtWidget, optional
            The parent widget. The default is None.
        """
        if "font_metric_width_factor" not in kwargs:
            kwargs["font_metric_width_factor"] = FONT_METRIC_PARAM_EDIT_WIDTH
        EmptyWidget.__init__(self, **kwargs)
        ParameterWidgetsMixIn.__init__(self)
        CreateWidgetsMixIn.__init__(self)
        self.plugin = None
        self.node_id = None
        self.setFixedWidth(
            int(
                QtWidgets.QApplication.instance().font_char_width
                * FONT_METRIC_PARAM_EDIT_WIDTH
            )
        )
        self.__qtapp = QtWidgets.QApplication.instance()
        self.__qtapp.sig_new_font_metrics.connect(self.process_new_font_metrics)

    def configure_plugin(
        self, node_id: int, plugin: BasePlugin, allow_restore_defaults: bool = True
    ):
        """
        Update the panel to show the Parameters of a different Plugin.

        This method clears the widget and populates it again with the
        Parameters of the new Plugin, defined by the Plugin node_id

        Parameters
        ----------
        node_id : int
            The node_id in the workflow edit tree.
        plugin : BasePlugin
            The instance of the Plugin to be edited.
        allow_restore_defaults : bool, optional
            Flag whether to allow restoring the default parameters.
            The default is True.
        """
        self.clear_layout()
        self.plugin = plugin
        self.node_id = node_id
        if self.plugin.has_unique_parameter_config_widget:
            self.__add_unique_config_widget()
        else:
            self.__add_generic_param_widgets()
        self._widgets["plugin_widget"].sig_new_label.connect(self.sig_new_label)
        self.create_empty_widget("final_spacer", sizePolicy=POLICY_FIX_EXP)
        self._widgets["plugin_widget"]._widgets["restore_defaults"].setVisible(
            allow_restore_defaults
        )

    def clear_layout(self):
        """
        Clear all items from the layout and generate a new layout.
        """
        if isinstance(self._widgets.get("plugin_widget", None), QtWidgets.QWidget):
            try:
                self._widgets["plugin_widget"].disconnect()
            except RuntimeError:
                pass
        delete_all_items_in_layout(self.layout())
        QtWidgets.QApplication.instance().sendPostedEvents(
            None, QtCore.QEvent.DeferredDelete
        )

    def __add_unique_config_widget(self):
        """
        Add the unique config widget for the selected plugin.
        """
        _class = self.plugin.get_parameter_config_widget()
        self.add_any_widget(
            "plugin_widget",
            _class(self.plugin, self.node_id),
            gridPos=(-1, 0, 1, 2),
        )

    def __add_generic_param_widgets(self):
        """
        Add the generic param widgets for standard plugins.
        """
        self.add_any_widget(
            "plugin_widget",
            GenericPluginConfigWidget(self.plugin, self.node_id),
            gridPos=(-1, 0, 1, 2),
        )

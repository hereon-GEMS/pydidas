# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
Module with the PluginCollectionBrowser class used to browse and select
plugins to add them to the WorkflowTree.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PluginCollectionBrowser"]

from functools import partial
from typing import Any, ClassVar

from qtpy import QtCore

from pydidas.core import constants
from pydidas.core.constants import PROC_PLUGIN_TYPE_NAMES
from pydidas.plugins import PluginCollection
from pydidas.plugins.plugin_registry import PluginRegistry
from pydidas.widgets.base_classes import EmptyWidget, WidgetFactoryMixIn
from pydidas.widgets.base_reimplementations import ReadOnlyTextEdit
from pydidas.widgets.extended_widgets import LineEditWithIcon
from pydidas.widgets.workflow_edit._plugin_registry_tree_widget import (
    _PluginRegistryTreeWidget,
)


PLUGIN_COLLECTION = PluginCollection()

_GENERIC_PLUGIN_ITEM_NAMES = [
    "Input plugins",
    "Processing plugins",
    "Output plugins",
    *PROC_PLUGIN_TYPE_NAMES.values(),
]


class PluginCollectionBrowser(WidgetFactoryMixIn, EmptyWidget):
    """
    A widget allows to browse through the list of available plugins.

    The PluginCollectionBrowser includes a search filter field, a QTreeView
    to browse through the list of available plugins, and a QTextEdit to show
    a description of the plugin.

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget. The default is None.
    collection : PluginRegistry or None, optional
        The plugin collection. Normally, this defaults to the generic
        plugin collection and should not be changed by the user.
    **kwargs : Any
        Any keyword arguments. Supported keywords are generic keywords and
        "collection" to set the linked plugin collection. By default, this should
        not be changed and will default to the PluginCollection singleton.
    """

    init_kwargs: ClassVar[list[str]] = ["collection"]

    sig_add_plugin_to_tree = QtCore.Signal(str)
    sig_append_to_specific_node = QtCore.Signal(int, str)
    sig_replace_plugin = QtCore.Signal(str)

    def __init__(self, collection: PluginRegistry | None = None, **kwargs: Any) -> None:
        WidgetFactoryMixIn.__init__(self)
        EmptyWidget.__init__(self, **kwargs)
        self.collection = collection or PluginCollection()

        self.add_any_widget(
            "filter_edit",
            LineEditWithIcon(
                icon="pydidas::generic_search", placeholderText="Search filter..."
            ),
            gridPos=(0, 0, 1, 1),
        )
        self.create_button(
            "but_reset_filter",
            "Reset filter",
            icon="qt-std::SP_BrowserReload",
            gridPos=(0, 1, 1, 1),
        )
        self.add_any_widget(
            "plugin_treeview",
            _PluginRegistryTreeWidget(collection=self.collection, **kwargs),
            gridPos=(1, 0, 1, 2),
        )
        self.create_any_widget(
            "plugin_description", ReadOnlyTextEdit, gridPos=(0, 2, 2, 1)
        )
        self.layout().setColumnStretch(0, 1)
        self.layout().setColumnStretch(1, 1)
        self.layout().setColumnStretch(2, 4)
        self.setMinimumHeight(400)
        self._widgets["but_reset_filter"].clicked.connect(
            partial(self._widgets["filter_edit"].setText, "")
        )
        self._widgets["filter_edit"].textChanged.connect(
            self._widgets["plugin_treeview"].update_filter
        )
        self._widgets["plugin_treeview"].sig_plugin_preselected.connect(
            self.display_plugin_description
        )
        self._widgets["plugin_treeview"].sig_add_plugin_to_tree.connect(
            self.__confirm_selection
        )
        self._widgets["plugin_treeview"].sig_replace_plugin.connect(
            self.sig_replace_plugin
        )
        self._widgets["plugin_treeview"].sig_append_to_specific_node.connect(
            self.sig_append_to_specific_node
        )

    @QtCore.Slot(float, float)
    def process_new_font_metrics(self, char_width: float, char_height: float) -> None:
        """
        Adjust the window based on the new font metrics.

        Parameters
        ----------
        char_width : float
            The font width in pixels.
        char_height : float
            The font height in pixels.
        """
        super().process_new_font_metrics(char_width, char_height)
        if "plugin_treeview" in self._widgets:
            self._widgets["plugin_treeview"].setMinimumWidth(
                int(char_width * constants.FONT_METRIC_CONFIG_WIDTH)
            )

    @QtCore.Slot(str)
    def __confirm_selection(self, name: str) -> None:
        """
        Confirm the selection of the plugin to add it to the workflow tree.

        Parameters
        ----------
        name : str
            The name of the selected plugin.
        """
        if name in _GENERIC_PLUGIN_ITEM_NAMES:
            return
        self.sig_add_plugin_to_tree.emit(name)

    @QtCore.Slot(str)
    def display_plugin_description(self, name: str) -> None:
        """
        Display the plugin description of the selected plugin.

        Parameters
        ----------
        name : str
            The name of the plugin.
        """
        if name in _GENERIC_PLUGIN_ITEM_NAMES:
            return
        _plugin_class = self.collection.get_plugin_by_plugin_name(name)
        self._widgets["plugin_description"].set_text_from_list(
            _plugin_class.get_class_description_as_list(), _plugin_class.plugin_name
        )

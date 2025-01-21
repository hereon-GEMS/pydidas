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
Module with the PluginCollectionBrowser class used to browse and select
plugins to add them to the WorkflowTree.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PluginCollectionBrowser"]


from qtpy import QtCore

from pydidas.core.constants import PROC_PLUGIN_TYPE_NAMES
from pydidas.plugins import PluginCollection
from pydidas.widgets.factory import CreateWidgetsMixIn, EmptyWidget
from pydidas.widgets.misc import ReadOnlyTextWidget
from pydidas.widgets.workflow_edit.select_new_plugin_widget import SelectNewPluginWidget


PLUGIN_COLLECTION = PluginCollection()


class PluginCollectionBrowser(CreateWidgetsMixIn, EmptyWidget):
    """
    A widget allows to browse through the list of available plugins.

    The PluginCollectionBrowser includes both a QTreeView to browse through
    the list of available plugins as well as a QTextEdit to show a description
    of the plugin.

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget. The default is None.
    **kwargs : dict
        Any keyword arguments. Supported keywords are generic keywords and
        "collection" to set the linked plugin collection. By default, this should
        not be changed and will default to the PluginCollection singleton.
    """

    init_kwargs = ["collection"]

    sig_add_plugin_to_tree = QtCore.Signal(str)
    sig_append_to_specific_node = QtCore.Signal(int, str)
    sig_replace_plugin = QtCore.Signal(str)

    def __init__(self, **kwargs: dict):
        EmptyWidget.__init__(self, **kwargs)
        CreateWidgetsMixIn.__init__(self)
        _local_plugin_coll = kwargs.get("collection", None)
        self.collection = (
            _local_plugin_coll if _local_plugin_coll is not None else PLUGIN_COLLECTION
        )
        self.add_any_widget(
            "plugin_treeview",
            SelectNewPluginWidget(collection=self.collection),
            gridPos=(0, 0, 1, 1),
        )
        self.add_any_widget(
            "plugin_description", ReadOnlyTextWidget(self), gridPos=(0, 1, 1, 1)
        )
        self.setMinimumHeight(400)

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
        self.layout().setColumnStretch(0, 2)
        self.layout().setColumnStretch(1, 4)

    @QtCore.Slot(str)
    def __confirm_selection(self, name: str):
        """
        Confirm the selection of the plugin to add it to the workflow tree.

        Parameters
        ----------
        name : str
            The name of the selected plugin.
        """
        if name in [
            "Input plugins",
            "Processing plugins",
            "Output plugins",
            *list(PROC_PLUGIN_TYPE_NAMES.values()),
        ]:
            return
        self.sig_add_plugin_to_tree.emit(name)

    @QtCore.Slot(str)
    def display_plugin_description(self, name: str):
        """
        Display the plugin description of the selected plugin.

        Parameters
        ----------
        name : str
            The name of the plugin.
        """
        if name in [
            "Input plugins",
            "Processing plugins",
            "Output plugins",
            *list(PROC_PLUGIN_TYPE_NAMES.values()),
        ]:
            return
        _p = self.collection.get_plugin_by_plugin_name(name)
        self._widgets["plugin_description"].set_text_from_list(
            _p.get_class_description_as_list(), _p.plugin_name
        )

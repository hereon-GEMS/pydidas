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
Module with the PluginCollectionBrowser class used to browse and select
plugins to add them to the WorkflowTree.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["PluginCollectionBrowser"]

from qtpy import QtWidgets, QtCore

from ...plugins import PluginCollection
from ..read_only_text_widget import ReadOnlyTextWidget
from ..utilities import apply_widget_properties
from .plugin_collection_tree_widget import PluginCollectionTreeWidget


PLUGIN_COLLECTION = PluginCollection()


class PluginCollectionBrowser(QtWidgets.QWidget):
    """
    The PluginCollectionBrowser includes both a QTreeView to browse through
    the list of available plugins as well as a QTextEdit to show a description
    of the plugin.

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget. The default is None.
    **kwargs : dict
        Any keyword arguments. Supported keywords are listed below.
    **collection : Union[pydidas.PluginCollection, None]
        The plugin collection. Normally, this entry should not be changed by
        the user. If None, this defaults to the generic plugin collection.
        The default is None.
    """

    selection_confirmed = QtCore.Signal(str)

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        apply_widget_properties(self, **kwargs)
        _local_plugin_coll = kwargs.get("collection", None)
        self.collection = (
            _local_plugin_coll if _local_plugin_coll is not None else PLUGIN_COLLECTION
        )

        self._widgets = dict(
            plugin_treeview=PluginCollectionTreeWidget(self, self.collection),
            plugin_description=ReadOnlyTextWidget(self),
        )

        self.setMinimumHeight(300)
        _layout = QtWidgets.QHBoxLayout()
        _layout.setContentsMargins(0, 0, 0, 0)
        _layout.addWidget(self._widgets["plugin_treeview"])
        _layout.addWidget(self._widgets["plugin_description"])
        self.setLayout(_layout)

        self._widgets["plugin_treeview"].selection_changed.connect(
            self.__display_plugin_description
        )
        self._widgets["plugin_treeview"].selection_confirmed.connect(
            self.__confirm_selection
        )
        self.collection.sig_updated_plugins.connect(
            self._widgets["plugin_treeview"]._update_collection
        )

    @QtCore.Slot(str)
    def __confirm_selection(self, name):
        """
        Confirm the selection of the plugin to add it to the workflow tree.

        Parameters
        ----------
        name : str
            The name of the selected plugin.
        """
        if name in ["Input plugins", "Processing plugins", "Output plugins"]:
            return
        self.selection_confirmed.emit(name)

    @QtCore.Slot(str)
    def __display_plugin_description(self, name):
        """
        display the plugin description of the selected plugin.

        Parameters
        ----------
        name : str
            The name of the plugin.
        """
        if name in ["Input plugins", "Processing plugins", "Output plugins"]:
            return
        _p = self.collection.get_plugin_by_plugin_name(name)()
        self._widgets["plugin_description"].setTextFromDict(
            _p.get_class_description_as_dict(), _p.plugin_name
        )

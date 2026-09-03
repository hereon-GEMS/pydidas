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
Module with _PluginRegistryTreeWidget for browsing plugins.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["_PluginRegistryTreeWidget"]


from functools import partial
from typing import Any

from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtCore import QModelIndex

from pydidas.core import constants
from pydidas.core.utils import apply_qt_properties
from pydidas.plugins import PluginCollection
from pydidas.plugins.plugin_registry import PluginRegistry
from pydidas.widgets.workflow_edit._plugin_treeview_model import (
    _PluginViewItemDelegate,
    _SearchFilterModel,
)
from pydidas.workflow import WorkflowTree


class _PluginRegistryTreeWidget(QtWidgets.QTreeView):
    """
    A QTreeView which displays all registered plugins sorted according to plugin type.

    Parameters
    ----------
    parent : QWidget or None, optional
        The Qt parent widget. The default is None.
    collection : PluginRegistry or None, optional
        The plugin collection. Normally, this defaults to the generic
        plugin collection and should not be changed by the user.
    **kwargs : Any
        Additional keyword arguments for widget modifications.
    """

    sig_plugin_preselected = QtCore.Signal(str)
    sig_add_plugin_to_tree = QtCore.Signal(str)
    sig_append_to_specific_node = QtCore.Signal(int, str)
    sig_replace_plugin = QtCore.Signal(str)

    def __init__(self, collection: PluginRegistry | None = None, **kwargs: Any) -> None:
        QtWidgets.QTreeView.__init__(self, parent=kwargs.get("parent", None))
        apply_qt_properties(self, **kwargs)

        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setMinimumWidth(
            int(
                QtWidgets.QApplication.instance().font_char_width
                * constants.FONT_METRIC_CONFIG_WIDTH
            )
        )
        self.setUniformRowHeights(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setHeaderHidden(True)

        self.collection = collection or PluginCollection()
        self.collection.sig_updated_plugins.connect(self.update_collection)
        self._tree = kwargs.get("tree", WorkflowTree())
        self.__model = _SearchFilterModel()
        self.__model.setSourceModel(QtGui.QStandardItemModel())
        self.setModel(self.__model)
        self.setItemDelegate(_PluginViewItemDelegate(self))

        self.update_collection()
        self.clicked.connect(
            partial(self._send_signal_for_selected_item, self.sig_plugin_preselected)
        )
        self.doubleClicked.connect(
            partial(self._send_signal_for_selected_item, self.sig_add_plugin_to_tree)
        )
        self.selectionModel().currentChanged.connect(self._current_selection_changed)
        self._create_menu()

    @QtCore.Slot()
    def update_collection(self) -> None:
        """
        Update the model based on the PluginCollection.

        This method/slot is called for example after changing the available plugins.
        """
        plugin_items = (
            {0: QtGui.QStandardItem("Input plugins")}
            | {
                _key: QtGui.QStandardItem(_label)
                for _key, _label in constants.PROC_PLUGIN_TYPE_NAMES.items()
            }
            | {2: QtGui.QStandardItem("Output plugins")}
        )

        for _plugin in self.collection.get_all_plugin_classes():
            _type = _plugin.plugin_subtype
            plugin_items[_type].appendRow(QtGui.QStandardItem(_plugin.plugin_name))

        _source = self.__model.sourceModel()
        _source.clear()  # type: ignore[attr-defined]
        _root = _source.invisibleRootItem()  # type: ignore[attr-defined]
        for _item in plugin_items.values():
            _root.appendRow(_item)
        self.expandAll()

    def _create_menu(self) -> None:
        """Create the custom context menu for adding and replacing nodes."""
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._menu_item_context = QtWidgets.QMenu(self)
        self.customContextMenuRequested.connect(self._open_context_menu)

        self._actions = {
            "replace": QtWidgets.QAction("Replace node", self),
            "append": QtWidgets.QAction("Append to node", self),
        }
        self._actions["replace"].triggered.connect(
            partial(self.__action_selected_item_in_menu, self.sig_replace_plugin)
        )
        self._actions["append"].triggered.connect(
            partial(self.__action_selected_item_in_menu, self.sig_add_plugin_to_tree)
        )
        self._menu_to_append = QtWidgets.QMenu("Append to specific node", self)
        self._menu_item_context.addAction(self._actions["replace"])
        self._menu_item_context.addAction(self._actions["append"])
        self._menu_item_context.addSeparator()
        self._menu_item_context.addMenu(self._menu_to_append)

    @QtCore.Slot(QtCore.QPoint)
    def _open_context_menu(self, point: QtCore.QPoint) -> None:
        """
        Open the context menu after updating the menu entries based on the
        current WorkflowTree.
        """
        if not self.selectedIndexes():
            return
        if self.selectedIndexes()[0].data() in constants.PLUGIN_TYPE_NAMES.values():
            return
        self.__update_generic_action_names()
        self.__update_append_menu()
        self._menu_item_context.exec(self.viewport().mapToGlobal(point))

    def __update_generic_action_names(self) -> None:
        """Update the generic action names based on the selected active node."""
        _active_node = self._tree.active_node_id is not None
        _node_str = self._tree.active_plugin_header
        self._actions["replace"].setEnabled(_active_node)
        self._actions["replace"].setText(f"Replace node {_node_str}")
        self._actions["append"].setText(
            f"Append to node {_node_str}" if _active_node else "Add new node"
        )

    def __update_append_menu(self) -> None:
        """Update the menu to append the new node to a specific node."""
        self._menu_to_append.clear()
        self._menu_append_actions = {}
        for _id in self._tree.node_ids:
            _name = f"#{_id:03d} [{self._tree.nodes[_id].plugin.plugin_name}]"
            self._menu_append_actions[_id] = QtWidgets.QAction(
                f"Append to node {_name}"
            )
            self._menu_to_append.addAction(self._menu_append_actions[_id])
            self._menu_append_actions[_id].triggered.connect(
                partial(self._emit_append_to_specific_node_signal, _id)
            )

    @QtCore.Slot(int)
    def _emit_append_to_specific_node_signal(self, node_id: int) -> None:
        """
        Add a plugin to the WorkflowTree and to append it to a specific node.

        Parameters
        ----------
        node_id : int
            The node ID.
        """
        if not self.selectedIndexes():
            return
        _index = self.selectedIndexes()[0]
        if not _index.isValid():
            return
        _name = _index.data(QtCore.Qt.DisplayRole)
        self.sig_append_to_specific_node.emit(node_id, _name)

    @QtCore.Slot(bool)
    def __action_selected_item_in_menu(
        self, signal: QtCore.Signal, _checked: bool = False
    ) -> None:
        """
        Emit the signal to notify watchers that an action in the menu was selected.

        Parameters
        ----------
        signal : QtCore.Signal
            The signal to be emitted.
        _checked : bool
            Qt keyword whether the action was checked. Unused here,
            but required for the Qt signal signature.
        """
        if not self.selectedIndexes():
            return
        index = self.selectedIndexes()[0]
        self._send_signal_for_selected_item(signal, index)  # type: ignore[arg-type]

    @QtCore.Slot(QModelIndex, QModelIndex)
    def _current_selection_changed(
        self, current: QModelIndex, _previous: QModelIndex
    ) -> None:
        """
        Update the context menu based on the current selection.

        Parameters
        ----------
        current : QModelIndex
            The current index.
        _previous : QModelIndex
            The previous index.
        """
        self._send_signal_for_selected_item(self.sig_plugin_preselected, current)

    @QtCore.Slot(QModelIndex)
    def _send_signal_for_selected_item(
        self, signal: QtCore.Signal, index: QModelIndex
    ) -> None:
        """
        Confirm the selection and emit a signal with the name of the selection.

        Parameters
        ----------
        signal : Signal
            The signal to emit.
        index : QModelIndex
            The source index.
        """
        if not index.isValid():
            return
        _name = index.data(QtCore.Qt.DisplayRole)
        if _name not in constants.PLUGIN_TYPE_NAMES.values():
            signal.emit(_name)  # type: ignore[attr-defined]

    @QtCore.Slot(str)
    def update_filter(self, filter_text: str) -> None:
        """
        Update the Plugin search filter.

        Parameters
        ----------
        filter_text : str
            The new search filter.
        """
        _pattern = QtCore.QRegularExpression(
            filter_text, QtCore.QRegularExpression.CaseInsensitiveOption
        )
        self.__model.setFilterRegularExpression(_pattern)
        self.expandAll()

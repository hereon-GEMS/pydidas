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
The SelectNewPluginWidget class allows to browse through all registered plugins.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PluginRegistryTreeWidget", "SelectNewPluginWidget"]


from functools import partial
from typing import Union

import numpy as np
from qtpy import QtCore, QtGui, QtWidgets

from pydidas.core import constants
from pydidas.core.utils import apply_qt_properties
from pydidas.plugins import PluginCollection
from pydidas.plugins.plugin_registry import PluginRegistry
from pydidas.widgets.factory import CreateWidgetsMixIn, EmptyWidget
from pydidas.widgets.misc import LineEditWithIcon
from pydidas.workflow import WorkflowTree


PLUGIN_COLLECTION = PluginCollection()
TREE = WorkflowTree()


class SelectNewPluginWidget(CreateWidgetsMixIn, EmptyWidget):
    """
    A widget for displaying all available Plugins and to allow the user to select one.

    SelectNewPluginWidget includes a search filter field and a QTreeView which
    displays all the available plugins.
    """

    init_kwargs = ["collection"]

    sig_plugin_preselected = QtCore.Signal(str)
    sig_add_plugin_to_tree = QtCore.Signal(str)
    sig_append_to_specific_node = QtCore.Signal(int, str)
    sig_replace_plugin = QtCore.Signal(str)

    def __init__(self, collection: Union[PluginRegistry, None] = None, **kwargs: dict):
        CreateWidgetsMixIn.__init__(self)
        EmptyWidget.__init__(self, **kwargs)
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
            "treeview",
            PluginRegistryTreeWidget(collection=collection, **kwargs),
            gridPos=(1, 0, 1, 2),
        )
        self._widgets["treeview"].sig_plugin_preselected.connect(
            self.sig_plugin_preselected
        )
        self._widgets["treeview"].sig_add_plugin_to_tree.connect(
            self.sig_add_plugin_to_tree
        )
        self._widgets["treeview"].sig_append_to_specific_node.connect(
            self.sig_append_to_specific_node
        )
        self._widgets["treeview"].sig_replace_plugin.connect(self.sig_replace_plugin)
        self._widgets["but_reset_filter"].clicked.connect(
            partial(self._widgets["filter_edit"].setText, "")
        )
        self._widgets["filter_edit"].textChanged.connect(
            self._widgets["treeview"].update_filter
        )

    @QtCore.Slot(float, float)
    def process_new_font_metrics(self, char_width: float, char_height: float):
        """
        Adjust the window based on the new font metrics.

        Parameters
        ----------
        char_width: float
            The font width in pixels.
        char_height : float
            The font height in pixels.
        """
        EmptyWidget.process_new_font_metrics(self, char_width, char_height)
        if "treeview" in self._widgets:
            self._widgets["treeview"].setMinimumWidth(
                int(char_width * constants.FONT_METRIC_CONFIG_WIDTH)
            )


class PluginRegistryTreeWidget(QtWidgets.QTreeView):
    """
    A QTreeView which displays all registered plugins sorted according to plugin type.

    Parameters
    ----------
    parent : Union[QWidget, None], optional
        The Qt parent widget. The default is None.
    collection : Union[pydidas.PluginCollection, None], optional
        The plugin collection. Normally, this defaults to the generic
        plugin collection and should not be changed by the user.
    **kwargs : dict
        Additional keyword arguments for widget modifications.
    """

    sig_plugin_preselected = QtCore.Signal(str)
    sig_add_plugin_to_tree = QtCore.Signal(str)
    sig_append_to_specific_node = QtCore.Signal(int, str)
    sig_replace_plugin = QtCore.Signal(str)

    def __init__(self, collection: Union[PluginRegistry, None] = None, **kwargs: dict):
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

        self.collection = collection if collection is not None else PLUGIN_COLLECTION
        self.collection.sig_updated_plugins.connect(self.update_collection)
        self.__model = _SearchFilterModel()
        self.__model.setSourceModel(QtGui.QStandardItemModel())
        self.setModel(self.__model)
        self.setItemDelegate(_TreeviewItemDelegate(self))

        self.update_collection()
        self.clicked.connect(
            partial(self.__send_signal_for_selected_item, self.sig_plugin_preselected)
        )
        self.doubleClicked.connect(
            partial(self.__send_signal_for_selected_item, self.sig_add_plugin_to_tree)
        )
        self.selectionModel().currentChanged.connect(self.__current_selection_changed)
        self.__create_menu()

    @QtCore.Slot()
    def update_collection(self):
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

        for _plugin in self.collection.get_all_plugins_of_type("input"):
            plugin_items[0].appendRow(QtGui.QStandardItem(_plugin.plugin_name))
        for _plugin in self.collection.get_all_plugins_of_type("proc"):
            _parent = plugin_items[_plugin.plugin_subtype]
            _parent.appendRow(QtGui.QStandardItem(_plugin.plugin_name))
        for _plugin in self.collection.get_all_plugins_of_type("output"):
            plugin_items[2].appendRow(QtGui.QStandardItem(_plugin.plugin_name))

        _source = self.__model.sourceModel()
        _source.clear()
        _root = _source.invisibleRootItem()
        for _item in plugin_items.values():
            _root.appendRow(_item)
        self.expandAll()

    def __create_menu(self):
        """
        Create the custom context menu for adding an replacing nodes.
        """
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
    def _open_context_menu(self, point):
        """
        Open the context menu after updating the menu entries based on the
        current WorkflowTree.
        """
        if self.selectedIndexes()[0].data() in constants.PLUGIN_TYPE_NAMES.values():
            return
        self.__update_generic_action_names()
        self.__update_append_menu()
        self._menu_item_context.exec(self.viewport().mapToGlobal(point))

    def __update_generic_action_names(self):
        """
        Update the generic action names based on the selected active node.
        """
        _active_node = TREE.active_node_id is not None
        _node_str = TREE.active_plugin_header
        self._actions["replace"].setEnabled(_active_node)
        self._actions["replace"].setText(f"Replace node {_node_str}")
        self._actions["append"].setText(
            f"Append to node {_node_str}" if _active_node else "Add new node"
        )

    def __update_append_menu(self):
        """
        Update the menu to append the new node to a specific node.
        """
        self._menu_to_append.clear()
        self._menu_append_actions = {}
        for _id in TREE.node_ids:
            _name = f"#{_id:03d} [{TREE.nodes[_id].plugin.plugin_name}]"
            self._menu_append_actions[_id] = QtWidgets.QAction(
                f"Append to node {_name}"
            )
            self._menu_to_append.addAction(self._menu_append_actions[_id])
            self._menu_append_actions[_id].triggered.connect(
                partial(self._emit_append_to_specific_node_signal, _id)
            )

    @QtCore.Slot(int)
    def _emit_append_to_specific_node_signal(self, node_id: int):
        """
        Add a plugin to the WorkflowTree and to append it to a specific node.

        Parameters
        ----------
        node_id : int
            The node ID.
        """
        _index = self.selectedIndexes()[0]
        if not _index.isValid():
            return
        _name = _index.data(QtCore.Qt.DisplayRole)
        self.sig_append_to_specific_node.emit(node_id, _name)

    @QtCore.Slot()
    def __action_selected_item_in_menu(
        self, signal: QtCore.Signal, checked: bool = True
    ):
        """
        Emit the signal to notify watchers that an action in the menu was selected.

        Parameters
        ----------
        signal : QtCore.Signal
            The signal to be emitted
        checked : bool
            Qt keyword whether the action was checked.
        """
        index = self.selectedIndexes()[0]
        self.__send_signal_for_selected_item(signal, index)

    @QtCore.Slot(QtCore.QModelIndex, QtCore.QModelIndex)
    def __current_selection_changed(
        self, current: QtCore.QModelIndex, previous: QtCore.QModelIndex
    ):
        """
        Update the context menu based on the current selection.

        Parameters
        ----------
        current : QtCore.QModelIndex
            The current index.
        previous : QtCore.QModelIndex
            The previous index.
        """
        self.__send_signal_for_selected_item(self.sig_plugin_preselected, current)

    @QtCore.Slot()
    def __send_signal_for_selected_item(self, signal: QtCore.Signal, index: int):
        """
        Confirm the selection and emit a signal with the name of the selection.

        Parameters
        ----------
        signal : Signal
            The signal emitted by the QTreeView.
        index : QtCore.QModelIndex
            The source index.
        """
        if not index.isValid():
            return
        _name = index.data(QtCore.Qt.DisplayRole)
        if _name not in constants.PLUGIN_TYPE_NAMES.values():
            signal.emit(_name)

    @QtCore.Slot(str)
    def update_filter(self, filter_text: str):
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


class _SearchFilterModel(QtCore.QSortFilterProxyModel):
    """
    A custom QSortFilterProxyModel to filter out entries not matching the search filter.
    """

    def __init__(self, **kwargs: dict):
        QtCore.QSortFilterProxyModel.__init__(self, kwargs.get("parent", None))
        self.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setDynamicSortFilter(True)

    def _accept_index(self, index: int) -> bool:
        """
        Recursive implementation to display a row.

        This filter will match a row if
            - its item matches the filter
            - an item in one of its children matches the filter.

        Parameters
        ----------
        index : QModelIndex
            The index of the row.

        Returns
        -------
        bool
            Flag whether the filter accepts the index or not.
        """
        if index.isValid():
            _label = index.data(QtCore.Qt.DisplayRole)
            if self.filterRegularExpression().match(_label).hasMatch():
                return True
            for _row in range(index.model().rowCount(index)):
                if self._accept_index(index.model().index(_row, 0, index)):
                    return True
        return False

    def filterAcceptsRow(
        self, sourceRow: int, sourceParent: QtCore.QModelIndex
    ) -> bool:
        """
        Reimplement the filterAcceptsRow method to use the filter.

        Parameters
        ----------
        sourceRow : int
            The source row number.
        sourceParent : QModelIndex
            The row's parent.

        Returns
        -------
        bool
            Flag whether the filter accepts the row or not.
        """
        _index = self.sourceModel().index(sourceRow, 0, sourceParent)
        return self._accept_index(_index)


class _TreeviewItemDelegate(QtWidgets.QStyledItemDelegate):
    """
    A QStyledItemDelegate to modify the font size for the different items.

    Parameters
    ----------
    root : QStandardItem
        The root node of the QStandardItemModel.
    """

    def __init__(self, parent):
        QtWidgets.QStyledItemDelegate.__init__(self, parent)
        self.__qtapp = QtWidgets.QApplication.instance()
        self.__height = int(np.ceil(2 * self.__qtapp.font_size + 2))
        self.__qtapp.sig_new_font_metrics.connect(self.process_new_font_metrics)

    @QtCore.Slot(float, float)
    def process_new_font_metrics(self, char_width: float, char_height: float):
        """
        Handle the QApplication's updated font.

        Parameters
        ----------
        char_width: float
            The font width in pixels.
        char_height : float
            The font height in pixels.
        """
        self.__height = int(char_height + 10)
        self.sizeHintChanged.emit(self.parent().currentIndex())

    def sizeHint(
        self, options: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex
    ) -> QtCore.QSize:
        """
        Overload the size hint method to achieve a uniform row height.

        Parameters
        ----------
        options : QtWidgets.QStyleOptionViewItem
            The options.
        index : QtCore.QModelIndex
            The index.

        Returns
        -------
        size : QtCore.QSize
            The updated sizeHint from the QStyledItemDelegate.
        """
        size = QtWidgets.QStyledItemDelegate.sizeHint(self, options, index)
        size.setHeight(self.__height)
        return size

    def paint(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex,
    ):
        """
        Overload the paint function with a custom font size for the top level items.

        Parameters
        ----------
        painter : QtGui.QPainter
            The QPainter called by the default method..
        option : .QStyleOptionViewItem
            Any Qt options passed to the painter.
        index : QModelIndex
            The index of the item to be painted.
        """
        option.font.setFamily(self.__qtapp.font_family)
        if index.data(QtCore.Qt.DisplayRole) in constants.PLUGIN_TYPE_NAMES.values():
            option.font.setPointSizeF(self.__qtapp.font_size + 2)
        QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)

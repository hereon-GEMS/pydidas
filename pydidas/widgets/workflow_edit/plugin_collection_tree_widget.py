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
Module with the PluginCollectionTreeWidget class used to browse through all
registered plugins.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["PluginCollectionTreeWidget"]

from functools import partial

from qtpy import QtWidgets, QtGui, QtCore

from ...core import constants
from ...core.utils import apply_qt_properties, apply_font_properties
from ...plugins import PluginCollection
from ...workflow import WorkflowTree


PLUGIN_COLLECTION = PluginCollection()
TREE = WorkflowTree()


class PluginCollectionTreeWidget(QtWidgets.QTreeView):
    """
    A tree view widget which displays all registered plugins sorted according
    to plugin type.

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

    def __init__(self, parent=None, collection=None, **kwargs):
        super().__init__(parent)
        apply_qt_properties(self, **kwargs)
        self.collection = collection if collection is not None else PLUGIN_COLLECTION

        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setFixedWidth(400)
        self.setUniformRowHeights(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        _header_font = self.header().font()
        apply_font_properties(
            _header_font, fontsize=constants.STANDARD_FONT_SIZE + 4, underline=True
        )
        self.header().setFont(_header_font)

        self._update_collection()
        self.clicked.connect(
            partial(self.__send_signal_with_new_plugin, self.sig_plugin_preselected)
        )
        self.doubleClicked.connect(
            partial(self.__send_signal_with_new_plugin, self.sig_add_plugin_to_tree)
        )
        self.__create_menu()

    @QtCore.Slot()
    def _update_collection(self):
        """
        Update the collection, for example after changing the available
        plugins.
        """
        _root, _model = self.__create_tree_model()
        self.setModel(_model)
        self.expandAll()
        self.setItemDelegate(_TreeviewItemDelegate(_root))

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
            partial(self.__send_signal_with_new_plugin, self.sig_replace_plugin)
        )
        self._actions["append"].triggered.connect(
            partial(self.__send_signal_with_new_plugin, self.sig_add_plugin_to_tree)
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
        self.__update_generic_action_names()
        self.__update_append_menu()
        self._menu_item_context.exec(self.viewport().mapToGlobal(point))

    def __update_generic_action_names(self):
        """
        Update the generic action names based on the selected active node.
        """
        if TREE.active_node_id is None:
            self._actions["replace"].setEnabled(False)
            self._actions["replace"].setText("Replace node")
            self._actions["append"].setText("Add new node")
        else:
            self._actions["replace"].setEnabled(True)
            _node_str = (
                f"#{TREE.active_node_id:03d} [{TREE.active_node.plugin.plugin_name}]"
            )
            self._actions["replace"].setText(f"Replace node {_node_str}")
            self._actions["append"].setText(f"Append to node {_node_str}")

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
    def _emit_append_to_specific_node_signal(self, node_id):
        """
        Emit the signal to append the node to a specific node.

        Parameters
        ----------
        node_id : int
            The Node id.
        """
        _index = self.selectedIndexes()[0]
        _name = self.model().itemFromIndex(_index).text()
        self.sig_append_to_specific_node.emit(node_id, _name)

    def __create_tree_model(self):
        """
        Create the tree model of the plugins.

        Returns
        -------
        root_node : QtGui.QStandardItem
            The root node item.
        tree_model : QtGui.QStandardItemModel
            The tree view model.
        """
        tree_model = QtGui.QStandardItemModel()
        tree_model.setHorizontalHeaderLabels(["Available plugins"])

        root_node = tree_model.invisibleRootItem()
        input_plugins = QtGui.QStandardItem("Input plugins")
        output_plugins = QtGui.QStandardItem("Output plugins")

        proc_plugin_items = {
            _key: QtGui.QStandardItem(_label)
            for _key, _label in constants.PROC_PLUGIN_TYPE_NAMES.items()
        }

        for _plugin in self.collection.get_all_plugins_of_type("input"):
            input_plugins.appendRow(QtGui.QStandardItem(_plugin.plugin_name))
        for _plugin in self.collection.get_all_plugins_of_type("proc"):
            _parent = proc_plugin_items[_plugin.plugin_subtype]
            _parent.appendRow(QtGui.QStandardItem(_plugin.plugin_name))
        for _plugin in self.collection.get_all_plugins_of_type("output"):
            output_plugins.appendRow(QtGui.QStandardItem(_plugin.plugin_name))

        root_node.appendRow(input_plugins)
        for _item in proc_plugin_items.values():
            root_node.appendRow(_item)
        root_node.appendRow(output_plugins)
        return root_node, tree_model

    def __send_signal_with_new_plugin(self, signal):
        """
        Confirm the selection and emit a signal with the name of the selection.

        Parameters
        ----------
        signal : Qsignal
            The signal emitted by the QTreeView.
        """
        index = self.selectedIndexes()[0]
        name = self.model().itemFromIndex(index).text()
        signal.emit(name)


class _TreeviewItemDelegate(QtWidgets.QStyledItemDelegate):
    """
    A QStyledItemDelegate to modify the font size for the different items.

    Parameters
    ----------
    root : QStandardItem
        The root node of the QStandardItemModel.
    """

    def __init__(self, root):
        super().__init__()
        self._model = root.model()

    def sizeHint(self, p_option, p_index):
        """
        Overload the size hint method to achieve a uniform row height.

        Parameters
        ----------
        p_option : type
            The options.
        p_index : type
            The index.

        Returns
        -------
        size : sizeHint
            The updated sizeHint from the QStyledItemDelegate.
        """
        size = QtWidgets.QStyledItemDelegate.sizeHint(self, p_option, p_index)
        size.setHeight(2 * constants.STANDARD_FONT_SIZE + 2)
        return size

    def paint(self, painter, option, index):
        """
        Overload the paint function with a custom font size for the top level
        items.

        Parameters
        ----------
        painter : type
            The QPainter.
        option : type
            Qt options.
        index : type
            the index.
        """
        _parent = self._model.itemFromIndex(index).parent()
        if _parent is None:
            option.font.setPointSize(constants.STANDARD_FONT_SIZE + 2)
        QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)

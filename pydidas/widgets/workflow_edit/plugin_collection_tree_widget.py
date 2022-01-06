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
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['PluginCollectionTreeWidget']

from functools import partial

from PyQt5 import QtWidgets, Qt, QtGui, QtCore

from ...core.constants import QT_STYLES
from ...plugins import PluginCollection

from ..utilities import apply_widget_properties


PLUGIN_COLLECTION = PluginCollection()


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
    selection_changed = QtCore.pyqtSignal(str)
    selection_confirmed = QtCore.pyqtSignal(str)

    def __init__(self, parent=None, collection=None, **kwargs):
        super().__init__(parent)
        apply_widget_properties(self, **kwargs)
        self.collection = (collection if collection is not None
                           else PLUGIN_COLLECTION)

        self.setEditTriggers(Qt.QAbstractItemView.NoEditTriggers)
        self.setFixedWidth(493)
        self.setMinimumHeight(200)
        self.setUniformRowHeights(True)
        self.setSelectionMode(Qt.QAbstractItemView.SingleSelection)
        self.header().setStyleSheet(QT_STYLES['title'])

        _root, _model = self.__create_tree_model()
        self.setModel(_model)
        self.expandAll()
        self.setItemDelegate(_TreeviewItemDelegate(_root))

        self.clicked.connect(
            partial(self.__confirm_selection, self.selection_changed))
        self.doubleClicked.connect(
            partial(self.__confirm_selection, self.selection_confirmed))

    def __create_tree_model(self):
        """
        Create the tree model of the plugins.

        Returns
        -------
        root_node : QStandardItem
            The root node item.
        tree_model : QStandardItemModel
            The tree view model.
        """
        tree_model = Qt.QStandardItemModel()
        tree_model.setHorizontalHeaderLabels(['Available plugins'])

        root_node = tree_model.invisibleRootItem()
        input_plugins = Qt.QStandardItem('Input plugins')
        proc_plugins = Qt.QStandardItem('Processing plugins')
        output_plugins = Qt.QStandardItem('Output plugins')

        for _plugin in self.collection.get_all_plugins_of_type('input'):
            input_plugins.appendRow(Qt.QStandardItem(_plugin.plugin_name))
        for _plugin in self.collection.get_all_plugins_of_type('proc'):
            proc_plugins.appendRow(Qt.QStandardItem(_plugin.plugin_name))
        for _plugin in self.collection.get_all_plugins_of_type('output'):
            output_plugins.appendRow(Qt.QStandardItem(_plugin.plugin_name))

        root_node.appendRow(input_plugins)
        root_node.appendRow(proc_plugins)
        root_node.appendRow(output_plugins)
        return root_node, tree_model

    def __confirm_selection(self, signal):
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
        size.setHeight(25)
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
            option.font.setWeight(QtGui.QFont.Bold)
            option.font.setPointSize(12)
        QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)

# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Module with the PluginCollectionPresenter class used to browse and select
plugins to add them to the workflow."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['PluginCollectionPresenter']

from functools import partial

from PyQt5 import QtWidgets, Qt, QtGui, QtCore

from ..plugins import PluginCollection
from ..config import STYLES
from .read_only_text_widget import ReadOnlyTextWidget

PLUGIN_COLLECTION = PluginCollection()


class PluginCollectionPresenter(QtWidgets.QWidget):
    """
    The PluginCollectionPresenter includes both a QTreeView to browse through
    the list of available plugins as well as a QTextEdit to show a description
    of the plugin.
    """
    selection_confirmed = QtCore.pyqtSignal(str)

    def __init__(self, parent=None, **kwargs):
        """
        Create a PluginCollectionPresenter instance.

        Parameters
        ----------
        parent : QWidget, optional
            The parent widget. The default is None.
        collection : pydidas.PluginCollection
            The plugin collection. Normally, this defaults to the generic
            plugin collection and should not be changed by the user.
        """
        super().__init__(parent)
        self.collection = (kwargs.get('collection', None)
                           if kwargs.get('collection', None) is not None
                           else PLUGIN_COLLECTION)

        _treeview = _PluginCollectionTreeWidget(self, self.collection)
        self._widgets = dict(plugin_treeview=_treeview,
                             plugin_description=ReadOnlyTextWidget(self))

        self.setMinimumHeight(300)
        _layout = QtWidgets.QHBoxLayout()
        _layout.setContentsMargins(0, 0, 0, 0)
        _layout.addWidget(self._widgets['plugin_treeview'])
        _layout.addWidget(self._widgets['plugin_description'])
        self.setLayout(_layout)

        self._widgets['plugin_treeview'].selection_changed.connect(
            self.__display_plugin_description)
        self._widgets['plugin_treeview'].selection_confirmed.connect(
            self.__confirm_selection)

    @QtCore.pyqtSlot(str)
    def __confirm_selection(self, name):
        """
        Confirm the selection of the plugin to add it to the workflow tree.

        Parameters
        ----------
        name : str
            The name of the selected plugin.
        """
        if name in ['Input plugins', 'Processing plugins', 'Output plugins']:
            return
        self.selection_confirmed.emit(name)

    @QtCore.pyqtSlot(str)
    def __display_plugin_description(self, name):
        """
        display the plugin description of the selected plugin.

        Parameters
        ----------
        name : str
            The name of the plugin.
        None.
        """
        if name in ['Input plugins', 'Processing plugins', 'Output plugins']:
            return
        _p = self.collection.get_plugin_by_plugin_name(name)()
        self._widgets['plugin_description'].setTextFromDict(
            _p.get_class_description_as_dict(), _p.plugin_name)


class _PluginCollectionTreeWidget(QtWidgets.QTreeView):
    """
    A tree view widget which displays all registered plugins sorted according
    to plugin type.
    """
    selection_changed = QtCore.pyqtSignal(str)
    selection_confirmed = QtCore.pyqtSignal(str)

    def __init__(self, parent=None, collection=None):
        """
        Create the _PluginCollectionTreeWidget.

        The setup method will create the _PluginCollectionTreeWidget which
        displays all registed plugins.

        Parameters
        ----------
        parent : QWidget, optional
            The Qt parent widget. The default is None.
        collection : pydidas.PluginCollection
            The plugin collection. Normally, this defaults to the generic
            plugin collection and should not be changed by the user.
        """
        super().__init__()
        self.collection = (collection if collection is not None
                           else PLUGIN_COLLECTION)
        self.parent = parent
        self.setEditTriggers(Qt.QAbstractItemView.NoEditTriggers)

        self.setFixedWidth(493)
        self.setMinimumHeight(200)
        self.setUniformRowHeights(True)
        self.setSelectionMode(Qt.QAbstractItemView.SingleSelection)
        self.header().setStyleSheet(STYLES['title'])
        _root, _model = self.__create_tree_model()
        self.setModel(_model)
        self.expandAll()
        self.setItemDelegate(_TreeviewFontDelegate(_root))
        self.clicked.connect(partial(self.__confirm_selection,
                                     self.selection_changed))
        self.doubleClicked.connect(partial(self.__confirm_selection,
                                           self.selection_confirmed))

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


class _TreeviewFontDelegate(QtWidgets.QStyledItemDelegate):
    """
    A QStyledItemDelegate to modify the font size for the different items.
    """
    def __init__(self, root):
        """
        Create _TreeviewFontDelegate class.

        Parameters
        ----------
        root : QStandardItem
            The root node of the QStandardItemModel.
        """
        super().__init__()
        self.root = root

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
        model = index.model()
        if model.itemFromIndex(index).parent() is None:
            option.font.setWeight(QtGui.QFont.Bold)
            option.font.setPointSize(12)
        QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)

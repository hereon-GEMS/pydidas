# MIT License
#
# Copyright (c) 2021 Malte Storm, Helmholtz-Zentrum Hereon.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Module with the PluginCollectionPresenter class used to browse and select
plugins to add them to the workflow."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['PluginCollectionPresenter']

from functools import partial

from PyQt5 import QtWidgets, Qt, QtGui, QtCore

from ..plugin_collection import PluginCollection
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

    def __init__(self, parent=None):
        """
        Create a PluginCollectionPresenter instance.

        Parameters
        ----------
        parent : QWidget, optional
            The parent widget. The default is None.

        Returns
        -------
        None.
        """
        super().__init__(parent)
        self.parent = parent

        self.w_treeview_plugins = _PluginCollectionTreeWidget(self)
        self.setMinimumHeight(300)
        self.w_plugin_description = _PluginDescriptionField(self)
        _layout = QtWidgets.QHBoxLayout()
        _layout.setContentsMargins(0, 0, 0, 0)
        _layout.addWidget(self.w_treeview_plugins)
        _layout.addWidget(self.w_plugin_description)
        self.setLayout(_layout)

        self.w_treeview_plugins.selection_changed.connect(
           self.__display_plugin_description
        )
        self.w_treeview_plugins.selection_confirmed.connect(
            self.__confirm_selection
        )

    def __confirm_selection(self, signal):
        """
        Confirm the selection of the plugin to add it to the workflow tree.

        Parameters
        ----------
        signal : QSignal
            The signal from the QTreeView.

        Returns
        -------
        None.
        """
        index = self.w_treeview_plugins.selectedIndexes()[0]
        name = self.w_treeview_plugins.model().itemFromIndex(index).text()
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

        Returns
        -------
        None.
        """
        if name in ['Input plugins', 'Processing plugins', 'Output plugins']:
            return
        p = PLUGIN_COLLECTION.get_plugin_by_name(name)()
        self.w_plugin_description.setText(
            p.get_class_description(return_list=True), p.plugin_name)
        del p

class _PluginDescriptionField(ReadOnlyTextWidget):
    def setText(self, text, title=None):
        """
        Print information.

        This widget accepts both a single text entry and a list of entries
        for the text. A list of entries will be converted to a single text
        according to a <key: entry> scheme.

        Parameters
        ----------
        text : Union[str, list]
            The text to be displayed. A string will be processed directly
            whereas a list will be processed with the first entries of every
            list entry being interpreted as key, entry.
        title : str, optional
            The title. If None, no title will be printed. The default is None.

        Returns
        -------
        None.
        """
        if isinstance(text, str):
            super().setText(text)
        elif isinstance(text, list):
            super().setText('')
            if title:
                self.setFontPointSize(14)
                self.setFontWeight(75)
                self.append(f'Plugin description: {title}')
            self.setFontPointSize(10)
            self.append('')

            for key, item in text:
                self.setFontWeight(75)
                self.append(key + ':')
                self.setFontWeight(50)
                self.append(' ' * 4 + item if key != 'Parameters' else item)
        self.verticalScrollBar().triggerAction(
            QtWidgets.QScrollBar.SliderToMinimum)


class _PluginCollectionTreeWidget(QtWidgets.QTreeView):
    """
    A tree view widget which displays all registered plugins sorted according
    to plugin type.
    """
    selection_changed = QtCore.pyqtSignal(str)
    selection_confirmed = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        """
        Create the _PluginCollectionTreeWidget.

        The setup method will create the _PluginCollectionTreeWidget which
        displays all registed plugins.

        Parameters
        ----------
        parent : QWidget, optional
            The Qt parent widget. The default is None.

        Returns
        -------
        None.
        """
        super().__init__()
        self.parent = parent
        self.setEditTriggers(Qt.QAbstractItemView.NoEditTriggers)

        self.setFixedWidth(493)
        self.setMinimumHeight(200)
        self.setUniformRowHeights(True)
        self.setSelectionMode(Qt.QAbstractItemView.SingleSelection)
        self.header().setStyleSheet(STYLES['title'])


        tree_model = Qt.QStandardItemModel()
        tree_model.setHorizontalHeaderLabels(['Available plugins'])

        root_node = tree_model.invisibleRootItem()
        input_plugins = Qt.QStandardItem('Input plugins')
        for item in PLUGIN_COLLECTION.plugins['input'].values():
            input_plugins.appendRow(Qt.QStandardItem(item.plugin_name))
        root_node.appendRow(input_plugins)

        proc_plugins = Qt.QStandardItem('Processing plugins')
        for item in PLUGIN_COLLECTION.plugins['proc'].values():
            proc_plugins.appendRow(Qt.QStandardItem(item.plugin_name))
        root_node.appendRow(proc_plugins)

        output_plugins = Qt.QStandardItem('Output plugins')
        for item in PLUGIN_COLLECTION.plugins['output'].values():
            output_plugins.appendRow(Qt.QStandardItem(item.plugin_name))
        root_node.appendRow(output_plugins)

        self.setModel(tree_model)
        self.expandAll()
        self.setItemDelegate(_TreeviewFontDelegate(root_node))
        self.clicked.connect(partial(self.__confirm_selection,
                                     self.selection_changed))
        self.doubleClicked.connect(partial(self.__confirm_selection,
                                           self.selection_confirmed))

    def __confirm_selection(self, signal):
        """
        Confirm the selection and emit a signal with the name of the selection.

        Parameters
        ----------
        signal : Qsignal
            The signal emitted by the QTreeView.

        Returns
        -------
        None.
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

        Returns
        -------
        None.
        """
        super().__init__()
        self.root = root

    def sizeHint(self, p_option, p_index):
        """
        Overload the size hint method to achieve a uniform row height.

        Parameters
        ----------
        p_option : type
            The options
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
        Overload the paint function with a custom font size.

        Parameters
        ----------
        painter : type
            The QPainter.
        option : type
            Qt options.
        index : type
            the index.

        Returns
        -------
        None.

        """
        model = index.model()
        if model.itemFromIndex(index).parent() is None:
            option.font.setWeight(QtGui.QFont.Bold)
            option.font.setPointSize(12)
        QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)

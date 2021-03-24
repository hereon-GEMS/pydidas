# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 10:39:19 2021

@author: ogurreck
"""
from PyQt5 import QtWidgets, Qt, QtGui, QtCore

from plugin_workflow_gui.plugin_collection import PluginCollection
from plugin_workflow_gui.config import STYLES

PLUGIN_COLLECTION = PluginCollection()

class WidgetTreeviewForPlugins(QtWidgets.QTreeView):
    selection_changed_signal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setEditTriggers(Qt.QAbstractItemView.NoEditTriggers)

        self.setFixedWidth(400)
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
        self.setItemDelegate(PluginCollectionTreeDelegate(root_node))
        self.clicked.connect(self.selection_changed)

    def selection_changed(self):
        index = self.selectedIndexes()[0]
        name = self.model().itemFromIndex(index).text()
        self.selection_changed_signal.emit(name)


class PluginCollectionTreeDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, root):
        super().__init__()
        self.root = root

    def sizeHint(self, p_option, p_index):
        size = QtWidgets.QStyledItemDelegate.sizeHint(self, p_option, p_index)
        size.setHeight(25)
        return size

    def paint(self, painter, option, index):
        model = index.model()
        if model.itemFromIndex(index).parent() is None:
            option.font.setWeight(QtGui.QFont.Bold)
            option.font.setPointSize(12)
        QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)

# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 10:39:19 2021

@author: ogurreck
"""
from PyQt5 import QtWidgets, Qt, QtGui, QtCore

from plugin_workflow_gui.plugin_collection import PluginCollection

PLUGIN_COLLECTION = PluginCollection()

class PluginTreeView(QtWidgets.QTreeView):
    name_selected_signal = QtCore.pyqtSlot(str)

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setEditTriggers(Qt.QAbstractItemView.NoEditTriggers)

        self.setUniformRowHeights(True)
        self.header().setStyleSheet('QWidget {font: bold; font-size: 15pt}')

        treeModel = Qt.QStandardItemModel()
        treeModel.setHorizontalHeaderLabels(['Available plugins'])

        rootNode = treeModel.invisibleRootItem()
        input_plugins = Qt.QStandardItem('Input plugins')
        for key, item in PLUGIN_COLLECTION.plugins['input'].items():
            input_plugins.appendRow(Qt.QStandardItem(item.name))
        rootNode.appendRow(input_plugins)

        proc_plugins = Qt.QStandardItem('Processing plugins')
        for key, item in PLUGIN_COLLECTION.plugins['proc'].items():
            proc_plugins.appendRow(Qt.QStandardItem(item.name))
        rootNode.appendRow(proc_plugins)

        output_plugins = Qt.QStandardItem('Output plugins')
        for key, item in PLUGIN_COLLECTION.plugins['output'].items():
            output_plugins.appendRow(Qt.QStandardItem(item.name))
        rootNode.appendRow(output_plugins)

        self.setModel(treeModel)
        self.expandAll()
        self.setItemDelegate(PluginCollectionTreeDelegate(rootNode))

        # self.doubleClicked.connect(self.parent.tree_changed)#doubleClicked)

    # @QtCore.pyqtSlot(str)
    # def name_selected_signal(self, value):


    def _doubleClicked(self, index):
        item = self.selectedIndexes()[0]
        print(item.model().itemFromIndex(index).text())

        # self.setDragEnabled(True)

    # def edit(self, index, trigger, event):
    #     print(trigger)
    #     if trigger == Qt.QAbstractItemView.DoubleClicked:
    #         return False
    #     return self.edit(index, trigger, event)

class PluginCollectionTreeDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, root):
        super().__init__()
        self.root = root

    def sizeHint(self, p_option, p_index):
        size = QtWidgets.QStyledItemDelegate.sizeHint(self, p_option, p_index)
        size.setHeight(25)
        return size

    def paint(self, painter, option, index):
        m = index.model()
        if m.itemFromIndex(index).parent() is None:
            option.font.setWeight(QtGui.QFont.Bold)
            option.font.setPointSize(12)
        QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)


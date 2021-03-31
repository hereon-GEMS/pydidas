# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 10:39:19 2021

@author: ogurreck
"""
from PyQt5 import QtWidgets, Qt, QtGui, QtCore
from functools import partial

from plugin_workflow_gui.plugin_collection import PluginCollection
from plugin_workflow_gui.config import STYLES

PLUGIN_COLLECTION = PluginCollection()


class PluginCollectionPresenter(QtWidgets.QWidget):
    selection_confirmed = QtCore.pyqtSignal(str)

    def __init__(self, parent=None, qt_main=None, master=None):
        super().__init__(parent)
        self.parent = parent
        self.qt_main = qt_main
        self.master = master

        self.w_treeview_plugins = PluginCollectionTreeWidget(self)
        self.w_plugin_description = TextDescriptionForPlugins(self)
        _layout = QtWidgets.QHBoxLayout()
        _layout.setContentsMargins(0, 0, 0, 0)
        _layout.addWidget(self.w_treeview_plugins)
        _layout.addWidget(self.w_plugin_description)
        self.setLayout(_layout)

        self.w_treeview_plugins.selection_changed.connect(
           self.update_plugin_description
        )
        self.w_treeview_plugins.selection_confirmed.connect(
            self.update_selection
        )

    def update_selection(self, signal):
        index = self.w_treeview_plugins.selectedIndexes()[0]
        name = self.w_treeview_plugins.model().itemFromIndex(index).text()
        self.selection_confirmed.emit(name)

    @QtCore.pyqtSlot(str)
    def update_plugin_description(self, name):
        if name in ['Input plugins', 'Processing plugins', 'Output plugins']:
            return
        p = PLUGIN_COLLECTION.get_plugin_by_name(name)()
        self.w_plugin_description.setText(
            p.get_class_description(return_list=True), p.plugin_name
        )
        del p


class TextDescriptionForPlugins(QtWidgets.QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setAcceptRichText(True)
        self.setReadOnly(True)
        self.setFixedWidth(500)

    def setText(self, text, title=None):
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
                item = '    ' + item if key != 'Parameters' else item
                self.append('    ' + item if key != 'Parameters' else item)
        self.verticalScrollBar().triggerAction(
            QtWidgets.QScrollBar.SliderToMinimum
        )


class PluginCollectionTreeWidget(QtWidgets.QTreeView):
    selection_changed = QtCore.pyqtSignal(str)
    selection_confirmed = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
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
        self.setItemDelegate(TreeviewFontDelegate(root_node))
        self.clicked.connect(partial(self.update_selection, self.selection_changed))
        self.doubleClicked.connect(partial(self.update_selection, self.selection_confirmed))

    def update_selection(self, signal):
        index = self.selectedIndexes()[0]
        name = self.model().itemFromIndex(index).text()
        signal.emit(name)


class TreeviewFontDelegate(QtWidgets.QStyledItemDelegate):
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

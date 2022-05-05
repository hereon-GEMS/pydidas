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

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import unittest
import random
import sys
import tempfile
import shutil
import copy

import numpy as np
from qtpy import QtWidgets, QtCore, QtTest, QtGui

from pydidas.widgets.workflow_edit import (
    PluginCollectionBrowser, PluginCollectionTreeWidget)
from pydidas.unittest_objects.dummy_plugin_collection import (
    DummyPluginCollection)


_typemap = {0: 'input', 1: 'proc', 2: 'output'}


class TestPluginCollectionBrowser(unittest.TestCase):

    def setUp(self):
        self._pluginpath = tempfile.mkdtemp()
        self.q_app = QtWidgets.QApplication(sys.argv)
        self.n_per_type = 8
        self.num = 3 * self.n_per_type
        self._syspath = copy.deepcopy(sys.path)
        self._qsettings = QtCore.QSettings('Hereon', 'pydidas')
        self._qsettings_plugin_path = self._qsettings.value(
            'global/plugin_path')
        self._qsettings.setValue('global/plugin_path', '')
        self.pcoll = DummyPluginCollection(n_plugins=self.num,
                                           plugin_path=self._pluginpath,
                                           create_empty=True)
        self.widgets = []

    def tearDown(self):
        sys.path = self._syspath
        self._qsettings.setValue('global/plugin_path',
                                 self._qsettings_plugin_path)
        shutil.rmtree(self._pluginpath)
        self.q_app.deleteLater()
        self.q_app.quit()

    def tree_click_test(self, double):
        obj = PluginCollectionTreeWidget(None, collection=self.pcoll)
        spy = QtTest.QSignalSpy(obj.selection_changed)
        self.click_index(obj, double)
        _index = obj.selectedIndexes()[0]
        _name = obj.model().itemFromIndex(_index).text()
        self.assertEqual(len(spy), 1)
        self.assertEqual(spy[0][0], _name)

    def click_index(self, obj, double=False):
        model = obj.model()
        _type = random.choice([0, 1, 2])
        _num = random.choice(np.arange(self.n_per_type))
        _item = model.item(_type).child(_num)
        index = model.indexFromItem(_item)
        obj.scrollTo(index)
        item_rect = obj.visualRect(index)
        QtTest.QTest.mouseClick(obj.viewport(), QtCore.Qt.LeftButton,
                                QtCore.Qt.NoModifier, item_rect.center())
        if double:
            QtTest.QTest.mouseDClick(obj.viewport(), QtCore.Qt.LeftButton,
                                     QtCore.Qt.NoModifier, item_rect.center())
        return _item

    def test_PluginCollectionTreeWidget_init(self):
        obj = PluginCollectionTreeWidget(None, collection=self.pcoll)
        self.assertIsInstance(obj, QtWidgets.QTreeView)
        self.assertEqual(obj.width(), 493)

    def test_PluginCollectionTreeWidget__create_tree_model(self):
        obj = PluginCollectionTreeWidget(None, collection=self.pcoll)
        _root, _model = obj._PluginCollectionTreeWidget__create_tree_model()
        self.assertIsInstance(_root, QtGui.QStandardItem)
        self.assertIsInstance(_model, QtGui.QStandardItemModel)
        self.assertEqual(_model.rowCount(), 3)
        for _num, _ptype in enumerate(['input', 'proc', 'output']):
            self.assertEqual(_model.item(_num).rowCount(), self.n_per_type)

    def test_PluginCollectionTreeWidget_single_click(self):
        self.tree_click_test(False)

    def test_PluginCollectionTreeWidget_double_click(self):
        self.tree_click_test(True)

    def test_PluginCollectionBrowser_init(self):
        obj = PluginCollectionBrowser(None, collection=self.pcoll)
        self.assertIsInstance(obj, QtWidgets.QWidget)

    def test_PluginCollectionBrowser_confirm_selection(self):
        obj = PluginCollectionBrowser(None, collection=self.pcoll)
        spy = QtTest.QSignalSpy(obj.selection_confirmed)
        _item = self.click_index(obj._widgets['plugin_treeview'], double=True)
        self.assertEqual(len(spy), 1)
        self.assertEqual(spy[0][0], _item.text())

    def test_PluginCollectionBrowser_preview_plugin(self):
        obj = PluginCollectionBrowser(None, collection=self.pcoll)
        _item = self.click_index(obj._widgets['plugin_treeview'])
        _plugin = self.pcoll.get_plugin_by_plugin_name(_item.text())
        _text = obj._widgets['plugin_description'].toPlainText()
        _desc = _plugin.get_class_description_as_dict()
        _desc['Parameters'] = '\n    '.join(_desc['Parameters'].split('\n'))
        _itemlist = list(_desc.values()) + list(_desc.keys())
        for n, item in enumerate(_itemlist):
            self.assertTrue(_text.find(item) >= 0)


if __name__ == "__main__":
    unittest.main()

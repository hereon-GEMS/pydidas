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

from pydidas.core import PydidasQsettings
from pydidas.widgets.workflow_edit import (
    PluginCollectionBrowser,
    PluginCollectionTreeWidget,
)
from pydidas.unittest_objects.dummy_plugin_collection import DummyPluginCollection


_typemap = {0: "input", 1: "proc", 2: "output"}


class TestPluginCollectionBrowser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._pluginpath = tempfile.mkdtemp()
        cls.q_app = QtWidgets.QApplication.instance()
        if cls.q_app is None:
            cls.q_app = QtWidgets.QApplication(sys.argv)
        cls.n_per_type = 8
        cls._syspath = copy.deepcopy(sys.path)
        cls._qsettings = PydidasQsettings()
        cls._qsettings_plugin_path = cls._qsettings.value("user/plugin_path")
        cls._qsettings.set_value("user/plugin_path", "")
        cls.pcoll = DummyPluginCollection(
            n_plugins=3 * cls.n_per_type, plugin_path=cls._pluginpath, create_empty=True
        )
        cls.widgets = []

    @classmethod
    def tearDownClass(cls):
        sys.path = cls._syspath
        cls._qsettings.set_value("user/plugin_path", cls._qsettings_plugin_path)
        shutil.rmtree(cls._pluginpath)
        widgets = cls.widgets[:]
        cls.widgets.clear()
        while widgets:
            w = widgets.pop(-1)
            w.deleteLater()
        cls.q_app.deleteLater()
        cls.q_app.quit()

    def tree_click_test(self, double):
        obj = PluginCollectionTreeWidget(None, collection=self.pcoll)
        self.widgets.append(obj)
        spy = QtTest.QSignalSpy(obj.sig_plugin_preselected)
        self.click_index(obj, double)
        _index = obj.selectedIndexes()[0]
        _name = obj.model().itemFromIndex(_index).text()
        self.assertEqual(len(spy), 1)
        self.assertEqual(spy[0][0], _name)

    def click_index(self, obj, double=False):
        model = obj.model()
        # ignore processing plugins because they are grouped differently
        _type = random.choice([0, 4])
        _num = random.choice(np.arange(self.n_per_type))
        _item = model.item(_type).child(_num)
        index = model.indexFromItem(_item)
        obj.scrollTo(index)
        item_rect = obj.visualRect(index)
        QtTest.QTest.mouseClick(
            obj.viewport(),
            QtCore.Qt.LeftButton,
            QtCore.Qt.NoModifier,
            item_rect.center(),
        )
        if double:
            QtTest.QTest.mouseDClick(
                obj.viewport(),
                QtCore.Qt.LeftButton,
                QtCore.Qt.NoModifier,
                item_rect.center(),
            )
        return _item

    def test_PluginCollectionTreeWidget_init(self):
        obj = PluginCollectionTreeWidget(None, collection=self.pcoll)
        self.widgets.append(obj)
        self.assertIsInstance(obj, QtWidgets.QTreeView)
        self.assertEqual(obj.width(), 400)

    def test_PluginCollectionTreeWidget__create_tree_model(self):
        obj = PluginCollectionTreeWidget(None, collection=self.pcoll)
        self.widgets.append(obj)
        _root, _model = obj._PluginCollectionTreeWidget__create_tree_model()
        self.assertIsInstance(_root, QtGui.QStandardItem)
        self.assertIsInstance(_model, QtGui.QStandardItemModel)
        self.assertEqual(_model.rowCount(), 5)
        # only check 0, 1, 4 for input, generic proc and output
        for _num in [0, 1, 4]:
            self.assertEqual(_model.item(_num).rowCount(), self.n_per_type)

    def test_PluginCollectionTreeWidget_single_click(self):
        self.tree_click_test(False)

    def test_PluginCollectionTreeWidget_double_click(self):
        self.tree_click_test(True)

    def test_PluginCollectionBrowser_init(self):
        obj = PluginCollectionBrowser(None, collection=self.pcoll)
        self.widgets.append(obj)
        self.assertIsInstance(obj, QtWidgets.QWidget)

    def test_PluginCollectionBrowser_confirm_selection(self):
        obj = PluginCollectionBrowser(None, collection=self.pcoll)
        self.widgets.append(obj)
        spy = QtTest.QSignalSpy(obj.sig_add_plugin_to_tree)
        _item = self.click_index(obj._widgets["plugin_treeview"], double=True)
        self.assertEqual(len(spy), 1)
        self.assertEqual(spy[0][0], _item.text())

    def test_PluginCollectionBrowser_preview_plugin(self):
        obj = PluginCollectionBrowser(None, collection=self.pcoll)
        self.widgets.append(obj)
        _item = self.click_index(obj._widgets["plugin_treeview"])
        _plugin = self.pcoll.get_plugin_by_plugin_name(_item.text())
        _text = obj._widgets["plugin_description"].toPlainText()
        _desc = _plugin.get_class_description_as_dict()
        _desc["Parameters"] = "\n    ".join(_desc["Parameters"].split("\n"))
        _itemlist = list(_desc.values()) + list(_desc.keys())
        for n, item in enumerate(_itemlist):
            self.assertTrue(_text.find(item) >= 0)


if __name__ == "__main__":
    unittest.main()

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

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import multiprocessing as mp
import os
import shutil
import tempfile
import unittest
from multiprocessing import managers

import yaml
from qtpy import QtWidgets

from pydidas.core import (
    BaseApp,
    ParameterCollection,
    get_generic_param_collection,
    get_generic_parameter,
)
from pydidas_qtcore import PydidasQApplication


class _TestApp(BaseApp):
    default_params = get_generic_param_collection("label", "n_image", "active_node")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stored = []
        self._config = {
            "item1": 1,
            "item2": slice(0, 5),
            "item3": "dummy",
            "carryon_counter": -1,
        }

    def multiprocessing_get_tasks(self):
        return [1, 2, 3]

    def multiprocessing_carryon(self):
        self._config["carryon_counter"] += 1
        return self._config["carryon_counter"] % 2 == 0

    def multiprocessing_func(self, *args):
        return args

    def multiprocessing_store_results(self, task, result):
        self.stored.append(result[0])


class TestBaseApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tempdir = tempfile.mkdtemp()
        _app = QtWidgets.QApplication.instance()
        if _app is None:
            _app = PydidasQApplication([])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._tempdir)

    def test_creation(self):
        app = BaseApp()
        self.assertIsInstance(app, BaseApp)

    def test_creation_with_args(self):
        _nx = get_generic_parameter("composite_nx")
        _nx.value = 10
        _ny = get_generic_parameter("composite_ny")
        _ny.value = 5
        _dir = get_generic_parameter("composite_dir")
        _dir.value = "y"
        _args = ParameterCollection(_nx, _ny, _dir)
        app = BaseApp(_args)
        self.assertEqual(app.get_param_value("composite_nx"), _nx.value)
        self.assertEqual(app.get_param_value("composite_ny"), _ny.value)
        self.assertEqual(app.get_param_value("composite_dir"), _dir.value)

    def test_multiprocessing_pre_run(self):
        app = BaseApp()
        self.assertIsNone(app.multiprocessing_pre_run())

    def test_multiprocessing_post_run(self):
        app = BaseApp()
        self.assertIsNone(app.multiprocessing_post_run())

    def test_multiprocessing_store_results(self):
        app = BaseApp()
        with self.assertRaises(NotImplementedError):
            app.multiprocessing_store_results(0, 0)

    def test_multiprocessing_get_tasks(self):
        app = BaseApp()
        with self.assertRaises(NotImplementedError):
            app.multiprocessing_get_tasks()

    def test_multiprocessing_pre_cycle(self):
        app = BaseApp()
        self.assertIsNone(app.multiprocessing_pre_cycle(0))

    def test_multiprocessing_func(self):
        app = BaseApp()
        with self.assertRaises(NotImplementedError):
            app.multiprocessing_func(None)

    def test_multiprocessing_carryon(self):
        app = _TestApp()
        self.assertTrue(app.multiprocessing_carryon())
        self.assertFalse(app.multiprocessing_carryon())

    def test_get_config(self):
        app = BaseApp()
        self.assertEqual(app.get_config(), {"run_prepared": False})

    def test_copy(self):
        _mgr = mp.Manager()
        app = BaseApp()
        _items = {
            "dummy": 42,
            "test_func": lambda x: x,
            "some_kwargs": {"a": 1, "b": 2},
        }
        app.mp_manager = {"lock": _mgr.Lock(), "shared_dict": _mgr.dict()}
        for _key, _val in _items.items():
            setattr(app, _key, _val)
        _copy = app.copy()
        self.assertNotEqual(app, _copy)
        self.assertIsInstance(_copy, BaseApp)
        for _key in _items.keys():
            self.assertTrue(hasattr(_copy, _key))
        self.assertEqual(app.mp_manager["lock"], _copy.mp_manager["lock"])
        self.assertEqual(app.mp_manager["shared_dict"], _copy.mp_manager["shared_dict"])

    def test_copy__as_clone(self):
        app = BaseApp()
        app.attributes_not_to_copy_to_app_clone = ["clone_att"]
        app.clone_att = 12
        app.non_clone_att = 42
        _copy = app.copy(clone_mode=True)
        self.assertNotEqual(app, _copy)
        self.assertTrue(hasattr(_copy, "non_clone_att"))
        self.assertFalse(hasattr(_copy, "clone_att"))
        self.assertTrue(_copy.clone_mode)

    def test_export_state(self):
        _label = "the new label value"
        _node = 17
        _item1 = 42.12345
        app = _TestApp()
        app.set_param_value("label", _label)
        app.set_param_value("active_node", _node)
        app._config["new_key"] = True
        app._config["item1"] = _item1
        _state = app.export_state()
        self.assertEqual(_state["params"]["label"], _label)
        self.assertEqual(_state["params"]["active_node"], _node)
        self.assertEqual(_state["config"]["new_key"], True)
        self.assertEqual(_state["config"]["item1"], _item1)
        self.assertIsInstance(_state["config"]["item2"], str)
        with open(os.path.join(self._tempdir, "dummy.yaml"), "w") as _file:
            yaml.dump(_state, _file, Dumper=yaml.SafeDumper)

    def test_import_state(self):
        _state = {
            "params": {"label": "new_label", "n_image": 103, "active_node": 7},
            "config": {
                "item1": 55,
                "item2": "::slice::1::7::2",
                "item3": "new_dummy",
            },
        }
        app = _TestApp()
        app.import_state(_state)
        for _key, _val in _state["params"].items():
            self.assertEqual(app.get_param_value(_key), _val)
        for _key in ["item1", "item3"]:
            self.assertEqual(app._config[_key], _state["config"][_key])
        self.assertEqual(app._config["item2"], slice(1, 7, 2))

    def test_run(self):
        app = _TestApp()
        app.run()
        self.assertEqual(app.stored, app.multiprocessing_get_tasks())

    def test_parse_func(self):
        app = BaseApp()
        self.assertEqual(app.parse_func(), {})

    def test_set_parse_func(self):
        def dummy(obj):
            return {0: hash(self)}

        BaseApp.parse_func = dummy
        app = BaseApp()
        self.assertEqual(dummy(None), app.parse_func())

    def test_deleteLater__no_manager(self):
        app = BaseApp()
        app.deleteLater()
        # assert nothing, just check no error occurs

    def test_deleteLater__with_manager(self):
        _mgr = mp.Manager()
        app = BaseApp()
        app._mp_manager_instance = _mgr
        app._locals = {"lock": _mgr.Lock(), "shared_dict": _mgr.dict()}
        app.deleteLater()
        self.assertEqual(app._mp_manager_instance._state.value, managers.State.SHUTDOWN)


if __name__ == "__main__":
    unittest.main()

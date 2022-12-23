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

import os
import tempfile
import shutil
import unittest

import yaml

from pydidas.core import (
    ParameterCollection,
    get_generic_parameter,
    BaseApp,
    get_generic_param_collection,
)


class TestApp(BaseApp):
    default_params = get_generic_param_collection("label", "n_image", "active_node")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stored = []
        self._config = {
            "item1": 1,
            "item2": slice(0, 5),
            "item3": "dummy",
            "shared_memory": {"test": None},
        }

    def initialize_shared_memory(self):
        self._config["shared_memory"] = {"test": True}

    def multiprocessing_pre_run(self):
        pass

    def multiprocessing_post_run(self):
        pass

    def multiprocessing_get_tasks(self):
        return [1, 2, 3]

    def multiprocessing_pre_cycle(self, *args):
        """
        Perform operations in the pre-cycle of every task.
        """
        return

    def multiprocessing_func(self, *args):
        return args

    def multiprocessing_store_results(self, task, result):
        self.stored.append(result[0])


class TestBaseApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tempdir = tempfile.mkdtemp()

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
        with self.assertRaises(NotImplementedError):
            app.multiprocessing_pre_run()

    def test_multiprocessing_post_run(self):
        app = BaseApp()
        with self.assertRaises(NotImplementedError):
            app.multiprocessing_post_run()

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
        app = BaseApp()
        self.assertTrue(app.multiprocessing_carryon())

    def test_get_config(self):
        app = BaseApp()
        self.assertEqual(app.get_config(), {})

    def test_get_copy(self):
        app = BaseApp()
        _copy = app.get_copy()
        self.assertNotEqual(app, _copy)
        self.assertIsInstance(_copy, BaseApp)

    def test_get_copy__as_slave(self):
        app = BaseApp()
        app.attributes_not_to_copy_to_slave_app = ["slave_att"]
        app.slave_att = 12
        app.non_slave_att = 42
        _copy = app.get_copy(slave_mode=True)
        self.assertNotEqual(app, _copy)
        self.assertTrue(hasattr(_copy, "non_slave_att"))
        self.assertFalse(hasattr(_copy, "slave_att"))

    def test_export_state(self):
        _label = "the new label value"
        _node = 17
        _item1 = 42.12345
        app = TestApp()
        app.set_param_value("label", _label)
        app.set_param_value("active_node", _node)
        app._config["new_key"] = True
        app._config["item1"] = _item1
        _state = app.export_state()
        self.assertEqual(_state["params"]["label"], _label)
        self.assertEqual(_state["params"]["active_node"], _node)
        self.assertEqual(_state["config"]["shared_memory"], "::restore::True")
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
                "shared_memory": "::restore::True",
            },
        }
        app = TestApp()
        app.import_state(_state)
        for _key, _val in _state["params"].items():
            self.assertEqual(app.get_param_value(_key), _val)
        for _key in ["item1", "item3"]:
            self.assertEqual(app._config[_key], _state["config"][_key])
        self.assertEqual(app._config["item2"], slice(1, 7, 2))
        self.assertEqual(app._config["shared_memory"], {"test": True})

    def test_run(self):
        app = TestApp()
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


if __name__ == "__main__":
    unittest.main()

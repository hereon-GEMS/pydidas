# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import io
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import h5py
from qtpy import QtWidgets

from pydidas import unittest_objects
from pydidas.apps import ExecuteWorkflowRunner
from pydidas.contexts import DiffractionExperimentContext, ScanContext
from pydidas.contexts.diff_exp import DiffractionExperiment
from pydidas.contexts.scan import Scan
from pydidas.core import PydidasQsettings, UserConfigError
from pydidas.core.utils import get_random_string
from pydidas.plugins import PluginCollection
from pydidas.workflow import ProcessingTree, WorkflowResultsContext, WorkflowTree
from pydidas.workflow.result_io import WorkflowResultIoMeta
from pydidas_qtcore import PydidasQApplication


TREE = WorkflowTree()
SCAN = ScanContext()
RESULTS = WorkflowResultsContext()
RESULT_SAVER = WorkflowResultIoMeta
COLL = PluginCollection()
EXP = DiffractionExperimentContext()


class TestExecuteWorkflowRunner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _app = QtWidgets.QApplication.instance()
        if _app is None:
            _ = PydidasQApplication([])
        RESULTS.clear_all_results()
        TREE.clear()
        cls._path = Path(tempfile.mkdtemp())
        cls.q_settings = PydidasQsettings()
        cls._n_workers = cls.q_settings.value("global/mp_n_workers", dtype=int)
        cls.q_settings.set_value("global/mp_n_workers", 1)
        _path = Path(unittest_objects.__file__).parent
        if _path not in COLL.registered_paths:
            COLL.find_and_register_plugins(_path)
        cls.__old_stdout = sys.stdout
        sys.stdout = cls.__mystdout = io.StringIO()
        EXP.export_to_file(cls._path.joinpath("diffraction_exp.yml"))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._path)
        cls.q_settings.set_value("global/mp_n_workers", cls._n_workers)
        COLL.unregister_plugin_path(Path(unittest_objects.__file__).parent)
        sys.stdout = cls.__old_stdout

    def setUp(self):
        RESULT_SAVER.set_active_savers_and_title([])
        EXP.restore_all_defaults(True)
        self.generate_tree()
        self.generate_scan()
        self.__sysargs = sys.argv[:]

    def tearDown(self):
        sys.argv = self.__sysargs

    def generate_tree(self):
        TREE.clear()
        TREE.create_and_add_node(unittest_objects.DummyLoader())
        TREE.create_and_add_node(unittest_objects.DummyProc())
        TREE.create_and_add_node(unittest_objects.DummyProc(), parent=TREE.root)
        TREE.export_to_file(self._path.joinpath("workflow_tree.yml"), overwrite=True)

    def generate_scan(self):
        SCAN.restore_all_defaults(True)
        SCAN.set_param_value("scan_dim", 3)
        self._nscan = (5, 7, 3)
        self._scandelta = (0.1, -0.2, 1.1)
        self._scanoffset = (-5, 0, 1.2)
        for i in range(3):
            SCAN.set_param_value("scan_dim", 3)
            SCAN.set_param_value(f"scan_dim{i}_n_points", self._nscan[i])
            SCAN.set_param_value(f"scan_dim{i}_delta", self._scandelta[i])
            SCAN.set_param_value(f"scan_dim{i}_offset", self._scanoffset[i])
        SCAN.export_to_file(self._path.joinpath("scan.yml"), overwrite=True)

    def create_dummy_entries_from_parsing(self, obj: ExecuteWorkflowRunner):
        self._parser_dummy_values = {
            _key: get_random_string(12)
            for _key in ["scan", "diffraction_exp", "workflow", "output_dir"]
        }

        self._parser_dummy_values["overwrite"] = True
        self._parser_dummy_values["verbose"] = True
        for _key, _val in self._parser_dummy_values.items():
            obj.parsed_args[_key] = _val

    def get_empty_dir_name(self):
        while True:
            _dir = self._path.joinpath(get_random_string(12))
            if not _dir.is_dir():
                break
        return _dir

    def test_creation__plain(self):
        obj = ExecuteWorkflowRunner()
        self.assertIsInstance(obj, ExecuteWorkflowRunner)
        for _key in ["scan", "diffraction_exp", "workflow", "output_dir"]:
            self.assertIsNone(obj.parsed_args[_key])
        for _key in ["verbose", "overwrite"]:
            self.assertFalse(obj.parsed_args[_key])

    def test_creation__cmdline_args(self):
        _scan_dir = str(self._path.joinpath(get_random_string(8)))
        sys.argv.extend(["-output_dir", _scan_dir, "--overwrite"])
        obj = ExecuteWorkflowRunner()
        for _key in ["scan", "diffraction_exp", "workflow"]:
            self.assertIsNone(obj.parsed_args[_key])
        self.assertEqual(obj.parsed_args["output_dir"], _scan_dir)
        for _key in ["verbose", "overwrite"]:
            self.assertTrue(obj.parsed_args[_key] == (_key == "overwrite"))

    def test_creation__cmdline_args_and_kwargs(self):
        _scan_dir = str(self._path.joinpath(get_random_string(8)))
        _workflow = get_random_string(12)
        _new_scan_dir = get_random_string(12)
        sys.argv.extend(["-output_dir", _scan_dir, "--overwrite"])
        obj = ExecuteWorkflowRunner(
            overwrite=False,
            output_dir=_new_scan_dir,
            workflow=_workflow,
        )
        for _key in ["scan", "diffraction_exp"]:
            self.assertIsNone(obj.parsed_args[_key])
        self.assertEqual(obj.parsed_args["output_dir"], _new_scan_dir)
        for _key in ["verbose", "overwrite"]:
            self.assertFalse(obj.parsed_args[_key])

    def test_parse_args__check_all_args(self):
        _test_values = {
            _key: get_random_string(12)
            for _key in ["scan", "diffraction_exp", "workflow", "output_dir"]
        }
        _test_values["overwrite"] = True
        _test_values["verbose"] = True
        for _key, _val in _test_values.items():
            if _key in ("overwrite", "verbose"):
                sys.argv.append(f"--{_key}")
            else:
                sys.argv.extend([f"-{_key}", _val])
        obj = ExecuteWorkflowRunner()
        for _key, _val in _test_values.items():
            self.assertEqual(obj.parsed_args[_key], _val)

    def test_parse_args__check_args_abbreviations(self):
        _test_values = {
            _key: get_random_string(12)
            for _key in ["scan", "diffraction_exp", "workflow", "output_dir"]
        }
        for _key, _val in _test_values.items():
            sys.argv.extend([f"-{_key[0]}", _val])
        obj = ExecuteWorkflowRunner()
        for _key, _val in _test_values.items():
            self.assertEqual(obj.parsed_args[_key], _val)

    def test_update_parsed_args_from_kwargs__all_cases(self):
        for _key in ["scan", "diffraction_exp", "workflow", "output_dir"]:
            with self.subTest(_key):
                _new_val = get_random_string(12)
                obj = ExecuteWorkflowRunner()
                self.create_dummy_entries_from_parsing(obj)
                self.assertEqual(obj.parsed_args[_key], self._parser_dummy_values[_key])
                obj.update_parsed_args_from_kwargs(**{_key: _new_val})
                for _local_key in ["scan", "diffraction_exp", "workflow", "output_dir"]:
                    if _local_key == _key:
                        continue
                    self.assertEqual(
                        obj.parsed_args[_local_key],
                        self._parser_dummy_values[_local_key],
                    )
                self.assertEqual(obj.parsed_args[_key], _new_val)

    def test_update_parsed_args_from_kwargs__diffraction_exp_alias(self):
        _new_val = get_random_string(12)
        obj = ExecuteWorkflowRunner()
        self.create_dummy_entries_from_parsing(obj)
        self.assertEqual(
            obj.parsed_args["diffraction_exp"],
            self._parser_dummy_values["diffraction_exp"],
        )
        obj.update_parsed_args_from_kwargs(diffraction_experiment=_new_val)
        self.assertEqual(obj.parsed_args["diffraction_exp"], _new_val)

    def test_update_parsed_args_from_kwargs__double_diffraction_exp(self):
        obj = ExecuteWorkflowRunner()
        self.create_dummy_entries_from_parsing(obj)
        with self.assertRaises(UserConfigError):
            obj.update_parsed_args_from_kwargs(
                diffraction_experiment="abc", diffraction_exp="42"
            )

    def test_print_progress(self):
        obj = ExecuteWorkflowRunner()
        obj._print_progress(0.1)
        _output = self.__mystdout.getvalue().strip()
        self.assertTrue(_output.endswith("10.00%"))

    def test_store_results_to_disk__empty_dir(self):
        RESULTS.update_shapes_from_scan_and_workflow()
        _dir = self.get_empty_dir_name()
        obj = ExecuteWorkflowRunner(output_dir=_dir)
        obj._store_results_to_disk()

    def test_store_results_to_disk__existing_empty_dir(self):
        RESULTS.update_shapes_from_scan_and_workflow()
        _dir = self.get_empty_dir_name()
        _dir.mkdir()
        obj = ExecuteWorkflowRunner(output_dir=_dir)
        obj._store_results_to_disk()
        self.assertTrue(_dir.joinpath("node_01.h5").is_file())
        self.assertTrue(_dir.joinpath("node_02.h5").is_file())

    def test_store_results_to_disk__used_dir(self):
        RESULTS.update_shapes_from_scan_and_workflow()
        _dir = self.get_empty_dir_name()
        _dir.mkdir()
        with open(_dir.joinpath("node_02.h5"), "w") as f:
            f.write("dummy")
        obj = ExecuteWorkflowRunner(output_dir=_dir)
        with self.assertRaises(UserConfigError):
            obj._store_results_to_disk()

    def test_store_results_to_disk__used_dir_w_overwrite(self):
        RESULTS.update_shapes_from_scan_and_workflow()
        _dir = self.get_empty_dir_name()
        _dir.mkdir()
        with open(_dir.joinpath("node_02.h5"), "w") as f:
            f.write("dummy")
        obj = ExecuteWorkflowRunner(output_dir=_dir, overwrite=True)
        obj._store_results_to_disk()
        self.assertTrue(_dir.joinpath("node_01.h5").is_file())
        self.assertTrue(_dir.joinpath("node_02.h5").is_file())

    def test_update_contexts_from_stored_args__scan_instance(self):
        _scan = Scan()
        _scan_params = {
            "scan_dim": 2,
            "scan_dim1_label": get_random_string(6),
            "scan_dim1_n_points": 12,
            "scan_dim2_label": get_random_string(6),
            "scan_dim2_n_points": 7,
        }
        _scan.set_param_values_from_dict(_scan_params)
        obj = ExecuteWorkflowRunner(scan=_scan)
        obj.update_contexts_from_stored_args()
        for _key, _val in _scan_params.items():
            self.assertEqual(SCAN.get_param_value(_key), _val)

    def test_update_contexts_from_stored_args__scan(self):
        _scan_fname = self._path.joinpath("dummy_scan.yml")
        _scan = Scan()
        _scan_params = {
            "scan_dim": 2,
            "scan_dim1_label": get_random_string(6),
            "scan_dim1_n_points": 12,
            "scan_dim2_label": get_random_string(6),
            "scan_dim2_n_points": 7,
        }
        _scan.set_param_values_from_dict(_scan_params)
        _scan.export_to_file(_scan_fname)
        for _item in [_scan, _scan_fname]:
            self.generate_scan()
            obj = ExecuteWorkflowRunner(scan=_item)
            obj.update_contexts_from_stored_args()
            for _key, _val in _scan_params.items():
                self.assertEqual(SCAN.get_param_value(_key), _val)

    def test_update_contexts_from_stored_args__workflow(self):
        _tree_fname = self._path.joinpath("dummy_workflow.yml")
        _tree = ProcessingTree()
        _tree.create_and_add_node(unittest_objects.DummyLoader())
        _tree.create_and_add_node(unittest_objects.DummyProc())
        _tree.create_and_add_node(unittest_objects.DummyProc())
        _tree.create_and_add_node(unittest_objects.DummyProc(), parent=_tree.root)
        _tree.export_to_file(_tree_fname)
        for _item in [_tree, _tree_fname]:
            with self.subTest(_item):
                self.generate_scan()
                obj = ExecuteWorkflowRunner(workflow=_item)
                obj.update_contexts_from_stored_args()
                for _id, _node in _tree.nodes.items():
                    self.assertEqual(TREE.nodes[_id].node_id, _node.node_id)
                    self.assertEqual(
                        TREE.nodes[_id].plugin.__class__.__name__,
                        _node.plugin.__class__.__name__,
                    )

    def test_update_contexts_from_stored_args__diffraction_exp(self):
        _exp_fname = self._path.joinpath("dummy_diffraction_exp.yml")
        _exp = DiffractionExperiment()
        _exp_params = {
            "detector_poni1": 0.1234,
            "detector_poni2": 2.12,
            "detector_dist": 0.665,
        }
        _exp.set_param_values_from_dict(_exp_params)
        _exp.export_to_file(_exp_fname)
        for _item in [_exp, _exp_fname]:
            EXP.restore_all_defaults(True)
            obj = ExecuteWorkflowRunner(diffraction_exp=_item)
            obj.update_contexts_from_stored_args()
            for _key, _val in _exp_params.items():
                self.assertEqual(EXP.get_param_value(_key), _val)

    def test_check_all_args_okay__keys_present(self):
        for _key, _name in [
            ["scan", "Scan"],
            ["workflow", "WorkfromTree"],
            ["diffraction_exp", "DiffractionExperiment"],
            ["output_dir", "Output directory"],
        ]:
            with self.subTest(_key):
                _keys = {
                    _item: (get_random_string(8) if _item != _key else None)
                    for _item in ["scan", "diffraction_exp", "workflow", "output_dir"]
                }
                obj = ExecuteWorkflowRunner(**_keys)
                with self.assertRaises(UserConfigError) as _error:
                    obj.check_all_args_okay()
                self.assertTrue(_error.exception.args[0].index(_name) > 0)

    def test_check_all_args_okay__dir_okay_no_overwrite(self):
        _dir = self.get_empty_dir_name()
        _dir.mkdir()
        with open(_dir.joinpath("dummy.txt"), "w") as f:
            f.write("dummy")
        _keys = {
            _item: get_random_string(8)
            for _item in ["scan", "diffraction_exp", "workflow"]
        }
        obj = ExecuteWorkflowRunner(output_dir=_dir, **_keys)
        with self.assertRaises(UserConfigError) as _error:
            obj.check_all_args_okay()
        self.assertTrue(_error.exception.args[0].index("directory is not empty") > 0)

    def test_process_scan__single_run(self):
        _dir = self.get_empty_dir_name()
        obj = ExecuteWorkflowRunner(
            workflow=self._path.joinpath("workflow_tree.yml"),
            scan=self._path.joinpath("scan.yml"),
            diffraction_exp=self._path.joinpath("diffraction_exp.yml"),
            output_dir=_dir,
        )
        obj.process_scan()
        for _name in ["node_01.h5", "node_02.h5"]:
            with h5py.File(_dir.joinpath(_name), "r") as f:
                _shape = f["entry/data/data"].shape
            self.assertEqual(_shape, self._nscan + (10, 10))

    def test_process_scan__multiple_run(self):
        _dir = self.get_empty_dir_name()
        obj = ExecuteWorkflowRunner(
            workflow=self._path.joinpath("workflow_tree.yml"),
            scan=self._path.joinpath("scan.yml"),
            diffraction_exp=self._path.joinpath("diffraction_exp.yml"),
            output_dir=_dir,
        )
        obj.process_scan()
        _dir2 = self.get_empty_dir_name()
        obj.process_scan(output_dir=_dir2)
        for _root in [_dir, _dir2]:
            for _name in ["node_01.h5", "node_02.h5"]:
                with h5py.File(_root.joinpath(_name), "r") as f:
                    _shape = f["entry/data/data"].shape
                self.assertEqual(_shape, self._nscan + (10, 10))


if __name__ == "__main__":
    unittest.main()

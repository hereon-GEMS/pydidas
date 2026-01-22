# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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

"""Unit tests for ExecuteWorkflowRunner application."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import io
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Generator

import h5py
import pytest

from pydidas import unittest_objects
from pydidas.apps import ExecuteWorkflowRunner
from pydidas.contexts import DiffractionExperimentContext, ScanContext
from pydidas.contexts.diff_exp import DiffractionExperiment
from pydidas.contexts.scan import Scan
from pydidas.core import PydidasQsettings, UserConfigError
from pydidas.core.utils import get_random_string
from pydidas.plugins import PluginCollection
from pydidas.workflow import ProcessingTree, WorkflowResults, WorkflowTree
from pydidas.workflow.result_io import ProcessingResultIoMeta


TREE = WorkflowTree()
SCAN = ScanContext()
RESULTS = WorkflowResults()
RESULT_SAVER = ProcessingResultIoMeta
COLL = PluginCollection()
EXP = DiffractionExperimentContext()


@pytest.fixture(scope="module")
def setup_module() -> Generator[tuple, None, None]:
    RESULTS.clear_all_results()
    TREE.clear()
    path = Path(tempfile.mkdtemp())
    q_settings = PydidasQsettings()
    n_workers = q_settings.value("global/mp_n_workers", dtype=int)
    q_settings.set_value("global/mp_n_workers", 1)
    plugin_path = Path(unittest_objects.__file__).parent
    if plugin_path not in COLL.registered_paths:
        COLL.find_and_register_plugins(plugin_path)
    old_stdout = sys.stdout
    mystdout = io.StringIO()
    EXP.export_to_file(path.joinpath("diffraction_exp.yml"))
    yield path, q_settings, n_workers, old_stdout, mystdout
    shutil.rmtree(path)
    q_settings.set_value("global/mp_n_workers", n_workers)
    COLL.unregister_plugin_path(plugin_path)
    sys.stdout = old_stdout


@pytest.fixture(autouse=True)
def setup_function(setup_module: object) -> Generator[None, None, None]:
    path, q_settings, n_workers, old_stdout, mystdout = setup_module
    RESULT_SAVER.set_active_savers_and_title([])
    EXP.restore_all_defaults(True)
    generate_tree(path)
    generate_scan(path)
    sys.stdout = mystdout
    sysargs = sys.argv[:]
    yield
    sys.argv = sysargs
    sys.stdout = old_stdout


def generate_tree(path: Path) -> None:
    TREE.clear()
    TREE.create_and_add_node(unittest_objects.DummyLoader())
    TREE.create_and_add_node(unittest_objects.DummyProc())
    TREE.create_and_add_node(unittest_objects.DummyProc(), parent=TREE.root)
    TREE.export_to_file(path.joinpath("workflow_tree.yml"), overwrite=True)


def generate_scan(path: Path) -> None:
    SCAN.restore_all_defaults(True)
    nscan = (5, 7, 3)
    scandelta = (0.1, -0.2, 1.1)
    scanoffset = (-5, 0, 1.2)
    for i in range(3):
        SCAN.set_param_value("scan_dim", 3)
        SCAN.set_param_value(f"scan_dim{i}_n_points", nscan[i])
        SCAN.set_param_value(f"scan_dim{i}_delta", scandelta[i])
        SCAN.set_param_value(f"scan_dim{i}_offset", scanoffset[i])
    SCAN.export_to_file(path.joinpath("scan.yml"), overwrite=True)


def create_dummy_entries_from_parsing(obj: object) -> None:
    parser_dummy_values = {  # type: ignore[assignment]
        key: get_random_string(12)
        for key in ["scan", "diffraction_exp", "workflow", "output_dir"]
    }
    parser_dummy_values["overwrite"] = True  # type: ignore[assignment]
    parser_dummy_values["verbose"] = True  # type: ignore[assignment]
    for key, val in parser_dummy_values.items():
        obj.parsed_args[key] = val  # type: ignore[attr-defined]


def get_empty_dir_name(path: Path) -> Path:
    while True:
        dir = path.joinpath(get_random_string(12))
        if not dir.is_dir():
            break
    return dir


def test_creation_plain() -> None:
    obj = ExecuteWorkflowRunner()
    assert isinstance(obj, ExecuteWorkflowRunner)
    for key in ["scan", "diffraction_exp", "workflow", "output_dir"]:
        assert obj.parsed_args[key] is None
    for key in ["verbose", "overwrite"]:
        assert not obj.parsed_args[key]


def test_creation_cmdline_args(setup_module: object) -> None:
    path, _, _, _, _ = setup_module
    scan_dir = str(path.joinpath(get_random_string(8)))
    sys.argv.extend(["-output_dir", scan_dir, "--overwrite"])
    obj = ExecuteWorkflowRunner()
    for key in ["scan", "diffraction_exp", "workflow"]:
        assert obj.parsed_args[key] is None
    assert obj.parsed_args["output_dir"] == scan_dir
    for key in ["verbose", "overwrite"]:
        assert obj.parsed_args[key] == (key == "overwrite")


def test_creation_cmdline_args_and_kwargs(setup_module: object) -> None:
    path, _, _, _, _ = setup_module
    scan_dir = str(path.joinpath(get_random_string(8)))
    workflow = get_random_string(12)
    new_scan_dir = get_random_string(12)
    sys.argv.extend(["-output_dir", scan_dir, "--overwrite"])
    obj = ExecuteWorkflowRunner(
        overwrite=False,
        output_dir=new_scan_dir,
        workflow=workflow,
    )
    for key in ["scan", "diffraction_exp"]:
        assert obj.parsed_args[key] is None
    assert obj.parsed_args["output_dir"] == new_scan_dir
    for key in ["verbose", "overwrite"]:
        assert not obj.parsed_args[key]


def test_parse_args_check_all_args() -> None:
    test_values = {  # type: ignore[assignment]
        key: get_random_string(12)
        for key in ["scan", "diffraction_exp", "workflow", "output_dir"]
    }
    test_values["overwrite"] = True  # type: ignore[assignment]
    test_values["verbose"] = True  # type: ignore[assignment]
    for key, val in test_values.items():
        if key in ("overwrite", "verbose"):
            sys.argv.append(f"--{key}")
        else:
            sys.argv.extend([f"-{key}", val])
    obj = ExecuteWorkflowRunner()
    for key, val in test_values.items():
        assert obj.parsed_args[key] == val


def test_parse_args_check_args_abbreviations() -> None:
    test_values = {  # type: ignore[assignment]
        key: get_random_string(12)
        for key in ["scan", "diffraction_exp", "workflow", "output_dir"]
    }
    for key, val in test_values.items():
        sys.argv.extend([f"-{key[0]}", val])
    obj = ExecuteWorkflowRunner()
    for key, val in test_values.items():
        assert obj.parsed_args[key] == val


@pytest.mark.parametrize("key", ["scan", "diffraction_exp", "workflow", "output_dir"])
def test_update_parsed_args_from_kwargs_all_cases(key: str) -> None:
    new_val = get_random_string(12)
    obj = ExecuteWorkflowRunner()
    create_dummy_entries_from_parsing(obj)
    assert obj.parsed_args[key] == obj.parsed_args[key]
    obj.update_parsed_args_from_kwargs(**{key: new_val})
    for local_key in ["scan", "diffraction_exp", "workflow", "output_dir"]:
        if local_key == key:
            continue
        assert obj.parsed_args[local_key] == obj.parsed_args[local_key]
    assert obj.parsed_args[key] == new_val


def test_update_parsed_args_from_kwargs_diffraction_exp_alias() -> None:
    new_val = get_random_string(12)
    obj = ExecuteWorkflowRunner()
    create_dummy_entries_from_parsing(obj)
    assert obj.parsed_args["diffraction_exp"] == obj.parsed_args["diffraction_exp"]
    obj.update_parsed_args_from_kwargs(diffraction_experiment=new_val)
    assert obj.parsed_args["diffraction_exp"] == new_val


def test_update_parsed_args_from_kwargs_double_diffraction_exp() -> None:
    obj = ExecuteWorkflowRunner()
    create_dummy_entries_from_parsing(obj)
    with pytest.raises(UserConfigError):
        obj.update_parsed_args_from_kwargs(
            diffraction_experiment="abc", diffraction_exp="42"
        )


def test_print_progress(setup_module: object) -> None:
    _, _, _, _, mystdout = setup_module
    sys.stdout = mystdout
    obj = ExecuteWorkflowRunner()
    obj._print_progress(0.1)
    output = mystdout.getvalue().strip()
    assert output.endswith("10.00%")


def test_write_results_to_disk__empty_dir(setup_module: object) -> None:
    path, _, _, _, _ = setup_module
    TREE.prepare_execution()
    _res = TREE.execute_process_and_get_results(0)
    RESULTS.prepare_new_results()
    RESULTS.store_results(0, _res)
    dir = get_empty_dir_name(path)
    obj = ExecuteWorkflowRunner(output_dir=dir)
    obj._write_results_to_disk()  # type: ignore[attr-defined]


def test_write_results_to_disk__existing_empty_dir(setup_module: object) -> None:
    path, _, _, _, _ = setup_module
    dir = get_empty_dir_name(path)
    dir.mkdir()
    TREE.prepare_execution()
    _res = TREE.execute_process_and_get_results(0)
    RESULTS.prepare_new_results()
    RESULTS.store_results(0, _res)
    obj = ExecuteWorkflowRunner(output_dir=dir)
    obj._write_results_to_disk()  # type: ignore[attr-defined]
    assert dir.joinpath("node_01.h5").is_file()
    assert dir.joinpath("node_02.h5").is_file()


def test_write_results_to_disk__used_dir(setup_module: object) -> None:
    path, _, _, _, _ = setup_module
    dir = get_empty_dir_name(path)
    dir.mkdir()
    TREE.prepare_execution()
    _res = TREE.execute_process_and_get_results(0)
    RESULTS.prepare_new_results()
    RESULTS.store_results(0, _res)
    with open(dir.joinpath("node_02.h5"), "w") as f:
        f.write("dummy")
    obj = ExecuteWorkflowRunner(output_dir=dir)
    with pytest.raises(UserConfigError):
        obj._write_results_to_disk()  # type: ignore[attr-defined]


def test_write_results_to_disk__used_dir_w_overwrite(setup_module: object) -> None:
    path, _, _, _, _ = setup_module
    dir = get_empty_dir_name(path)
    dir.mkdir()
    with open(dir.joinpath("node_02.h5"), "w") as f:
        f.write("dummy")
    obj = ExecuteWorkflowRunner(output_dir=dir, overwrite=True)
    obj._write_results_to_disk()  # type: ignore[attr-defined]
    assert dir.joinpath("node_01.h5").is_file()
    assert dir.joinpath("node_02.h5").is_file()


def test_update_contexts_from_stored_args_scan_instance() -> None:
    scan = Scan()
    scan_params = {
        "scan_dim": 2,
        "scan_dim1_label": get_random_string(6),
        "scan_dim1_n_points": 12,
        "scan_dim2_label": get_random_string(6),
        "scan_dim2_n_points": 7,
    }
    scan.set_param_values_from_dict(scan_params)
    obj = ExecuteWorkflowRunner(scan=scan)
    obj.update_contexts_from_stored_args()
    for key, val in scan_params.items():
        assert SCAN.get_param_value(key) == val


def test_update_contexts_from_stored_args_scan(setup_module: object) -> None:
    path, _, _, _, _ = setup_module
    scan_fname = path.joinpath("dummy_scan.yml")
    scan = Scan()
    scan_params = {
        "scan_dim": 2,
        "scan_dim1_label": get_random_string(6),
        "scan_dim1_n_points": 12,
        "scan_dim2_label": get_random_string(6),
        "scan_dim2_n_points": 7,
    }
    scan.set_param_values_from_dict(scan_params)
    scan.export_to_file(scan_fname)
    for item in [scan, scan_fname]:
        generate_scan(path)
        obj = ExecuteWorkflowRunner(scan=item)
        obj.update_contexts_from_stored_args()
        for key, val in scan_params.items():
            assert SCAN.get_param_value(key) == val


def test_update_contexts_from_stored_args_workflow(setup_module: object) -> None:
    path, _, _, _, _ = setup_module
    tree_fname = path.joinpath("dummy_workflow.yml")
    tree = ProcessingTree()
    tree.create_and_add_node(unittest_objects.DummyLoader())
    tree.create_and_add_node(unittest_objects.DummyProc())
    tree.create_and_add_node(unittest_objects.DummyProc())
    tree.create_and_add_node(unittest_objects.DummyProc(), parent=tree.root)
    tree.export_to_file(tree_fname)
    for item in [tree, tree_fname]:
        generate_scan(path)
        obj = ExecuteWorkflowRunner(workflow=item)
        obj.update_contexts_from_stored_args()
        for id, node in tree.nodes.items():
            assert TREE.nodes[id].node_id == node.node_id
            assert (
                TREE.nodes[id].plugin.__class__.__name__
                == node.plugin.__class__.__name__
            )


def test_update_contexts_from_stored_args_diffraction_exp(
    setup_module: object,
) -> None:
    path, _, _, _, _ = setup_module
    exp_fname = path.joinpath("dummy_diffraction_exp.yml")
    exp = DiffractionExperiment()
    exp_params = {
        "detector_poni1": 0.1234,
        "detector_poni2": 2.12,
        "detector_dist": 0.665,
    }
    exp.set_param_values_from_dict(exp_params)
    exp.export_to_file(exp_fname)
    for item in [exp, exp_fname]:
        EXP.restore_all_defaults(True)
        obj = ExecuteWorkflowRunner(diffraction_exp=item)
        obj.update_contexts_from_stored_args()
        for key, val in exp_params.items():
            assert EXP.get_param_value(key) == val


@pytest.mark.parametrize(
    "key, name",
    [
        ("scan", "Scan"),
        ("workflow", "WorkflowTree"),
        ("diffraction_exp", "DiffractionExperiment"),
        ("output_dir", "Output directory"),
    ],
)
def test_check_all_args_okay_keys_present(key: str, name: str) -> None:
    keys = {
        item: (get_random_string(8) if item != key else None)
        for item in ["scan", "diffraction_exp", "workflow", "output_dir"]
    }
    obj = ExecuteWorkflowRunner(**keys)
    with pytest.raises(UserConfigError) as error:
        obj.check_all_args_okay()
    assert name in str(error.value)


def test_check_all_args_okay_dir_okay_no_overwrite(setup_module: object) -> None:
    path, _, _, _, _ = setup_module
    dir = get_empty_dir_name(path)
    dir.mkdir()
    with open(dir.joinpath("dummy.txt"), "w") as f:
        f.write("dummy")
    keys = {
        item: get_random_string(8) for item in ["scan", "diffraction_exp", "workflow"]
    }
    obj = ExecuteWorkflowRunner(output_dir=dir, **keys)
    with pytest.raises(UserConfigError) as error:
        obj.check_all_args_okay()
    assert "directory is not empty" in str(error.value)


@pytest.mark.slow
def test_process_scan_single_run(setup_module: object) -> None:
    path, _, _, _, _ = setup_module
    dir = get_empty_dir_name(path)
    obj = ExecuteWorkflowRunner(
        workflow=path.joinpath("workflow_tree.yml"),
        scan=path.joinpath("scan.yml"),
        diffraction_exp=path.joinpath("diffraction_exp.yml"),
        output_dir=dir,
    )
    obj.process_scan()
    for name in ["node_01.h5", "node_02.h5"]:
        with h5py.File(dir.joinpath(name), "r") as f:
            shape = f["entry/data/data"].shape
        assert shape == (5, 7, 3, 10, 10)


@pytest.mark.slow
def test_process_scan_multiple_run(setup_module: object) -> None:
    path, _, _, _, _ = setup_module
    dir = get_empty_dir_name(path)
    obj = ExecuteWorkflowRunner(
        workflow=path.joinpath("workflow_tree.yml"),
        scan=path.joinpath("scan.yml"),
        diffraction_exp=path.joinpath("diffraction_exp.yml"),
        output_dir=dir,
    )
    obj.process_scan()
    dir2 = get_empty_dir_name(path)
    obj.process_scan(output_dir=dir2)
    for root in [dir, dir2]:
        for name in ["node_01.h5", "node_02.h5"]:
            with h5py.File(root.joinpath(name), "r") as f:
                shape = f["entry/data/data"].shape
            assert shape == (5, 7, 3, 10, 10)


if __name__ == "__main__":
    pytest.main()

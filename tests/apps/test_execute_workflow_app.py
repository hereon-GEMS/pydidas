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

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import multiprocessing as mp
import queue
import time
from collections.abc import Iterator
from multiprocessing.managers import SyncManager
from multiprocessing.shared_memory import SharedMemory
from numbers import Integral
from pathlib import Path
from typing import Any, cast

import h5py
import numpy as np
import pytest
from qtpy import QtTest

from pydidas import IS_QT6, LOGGING_LEVEL, unittest_objects
from pydidas.apps import ExecuteWorkflowApp
from pydidas.apps.parsers import execute_workflow_app_parser
from pydidas.contexts import DiffractionExperimentContext, ScanContext
from pydidas.core import PydidasQsettings, UserConfigError, get_generic_parameter
from pydidas.core.utils import get_random_string
from pydidas.multiprocessing.app_processor import app_processor_func
from pydidas.plugins import PluginCollection
from pydidas.workflow import WorkflowResults, WorkflowTree


COLL = PluginCollection()
EXP = DiffractionExperimentContext()
SCAN = ScanContext()
TREE = WorkflowTree()
RESULTS = WorkflowResults()

_NSCAN = (9, 5, 7)
_SCANDELTA = (0.1, -0.2, 1.1)
_SCANOFFSET = (-5, 0, 1.2)


def _init_scan() -> None:
    SCAN.restore_all_defaults(True)
    SCAN.set_param_value("scan_dim", 3)


def _reset_scan_params() -> None:
    for i in range(3):
        SCAN.set_param_value("scan_dim", 3)
        SCAN.set_param_value(f"scan_dim{i}_n_points", _NSCAN[i - 1])
        SCAN.set_param_value(f"scan_dim{i}_delta", _SCANDELTA[i - 1])
        SCAN.set_param_value(f"scan_dim{i}_offset", _SCANOFFSET[i - 1])


def _get_exec_workflow_app(
    apps: list[ExecuteWorkflowApp], *args: Any, **kwargs: Any
) -> ExecuteWorkflowApp:
    app = ExecuteWorkflowApp(*args, **kwargs)
    if app.clone_mode:
        app._config["tree_str_rep"] = TREE.export_to_string()
    app.prepare_run()
    apps.append(app)
    return app


def _get_shared_memory(app: ExecuteWorkflowApp, name: str) -> SharedMemory:
    return cast(Any, app)._ExecuteWorkflowApp__get_shared_memory(name)


def _get_main_app_and_clone(
    apps: list[ExecuteWorkflowApp],
) -> tuple[ExecuteWorkflowApp, ExecuteWorkflowApp]:
    manager = ExecuteWorkflowApp()
    manager.prepare_run()
    apps.append(manager)
    clone = cast(ExecuteWorkflowApp, manager.copy(clone_mode=True))
    clone.prepare_run()
    apps.append(clone)
    return manager, clone


def _store_results(
    app: ExecuteWorkflowApp, index: int, buffer_index: Any
) -> None:
    cast(Any, app).multiprocessing_store_results(index, buffer_index)


def _run_processor_with_clone_worker(
    apps: list[ExecuteWorkflowApp],
) -> ExecuteWorkflowApp:
    main_app = _get_exec_workflow_app(apps, print_debug=True)
    main_app.prepare_run()
    lock_manager = mp.Manager()
    queues = {
        "queue_input": mp.Queue(),
        "queue_output": mp.Queue(),
        "queue_stop": mp.Queue(),
        "queue_shutting_down": mp.Queue(),
        "queue_signal": mp.Queue(),
    }
    mp_kwargs = {
        "logging_level": LOGGING_LEVEL,
        "lock": lock_manager.Lock(),
        **queues,
    }
    proc = mp.Process(
        target=app_processor_func,
        args=(
            mp_kwargs,
            ExecuteWorkflowApp,
            main_app.params.copy(),
            main_app.get_config(),
        ),
        kwargs={
            "use_tasks": True,
            "app_mp_manager": main_app.mp_manager,
            "print_debug": True,
        },
        name=f"pydidas_{mp.current_process().pid}_worker",
    )
    for i in range(min(10, SCAN.n_points)):
        queues["queue_input"].put(i)
    queues["queue_input"].put(None)
    proc.start()
    time.sleep(0.05)
    with pytest.raises(queue.Empty):
        queues["queue_output"].get_nowait()
    signal = queues["queue_signal"].get()
    assert signal == "::shapes_not_set::"
    main_app._create_shared_memory()
    time.sleep(0.05)
    for i in range(min(10, SCAN.n_points)):
        latest = queues["queue_output"].get()
        main_app.multiprocessing_store_results(*latest)
        assert latest[0] == i
        assert isinstance(latest[1], Integral)
        time.sleep(0.05)
    stop_signal = queues["queue_output"].get()
    assert stop_signal[0] is None
    for node in TREE.get_all_nodes_with_results():
        node_id = node.node_id
        assert node_id is not None
        res = RESULTS.get_results(node_id)
        assert res is not None
        slices = cast(Any, ((0,) * (SCAN.ndim - 1)) + (slice(None),))
        assert np.all(res[slices] > 0)
    queues["queue_stop"].put(1)
    proc.join()
    time.sleep(0.05)
    return main_app


def _write_results_to_shared_arrays(app: ExecuteWorkflowApp) -> None:
    cast(Any, app)._ExecuteWorkflowApp__write_results_to_shared_arrays()


@pytest.fixture(scope="module", autouse=True)
def module_setup() -> Iterator[None]:
    RESULTS.clear_all_results()
    TREE.clear()
    _init_scan()
    q_settings = PydidasQsettings()
    buf_size = q_settings.value("global/shared_buffer_size", float)
    n_workers = q_settings.value("global/mp_n_workers", int)
    plugin_file = unittest_objects.__file__
    assert plugin_file is not None
    plugin_path = Path(plugin_file).parent
    added_plugin_path = plugin_path not in COLL.registered_paths
    if added_plugin_path:
        COLL.find_and_register_plugins(plugin_path)
    yield
    q_settings.set_value("global/shared_buffer_size", buf_size)
    q_settings.set_value("global/mp_n_workers", n_workers)
    if added_plugin_path and plugin_path in COLL.registered_paths:
        COLL.unregister_plugin_path(plugin_path)


@pytest.fixture(scope="module")
def tmp_path_module(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Path]:
    yield tmp_path_factory.mktemp("test_execute_workflow_app")


@pytest.fixture(autouse=True)
def reset_state() -> Iterator[None]:
    RESULTS.clear_all_results()
    TREE.clear()
    TREE.create_and_add_node(unittest_objects.DummyLoader())
    TREE.create_and_add_node(unittest_objects.DummyProc())
    TREE.create_and_add_node(unittest_objects.DummyProc(), parent=TREE.root)
    _reset_scan_params()
    yield
    ExecuteWorkflowApp.parse_func = execute_workflow_app_parser


@pytest.fixture
def apps() -> Iterator[list[ExecuteWorkflowApp]]:
    created_apps: list[ExecuteWorkflowApp] = []
    yield created_apps
    for app in created_apps:
        app.close_shared_arrays_and_memory()


@pytest.fixture
def shares() -> Iterator[list[SharedMemory]]:
    created_shares: list[SharedMemory] = []
    yield created_shares
    for share in created_shares:
        share.close()
        share.unlink()


def test_creation(apps: list[ExecuteWorkflowApp]) -> None:
    app = _get_exec_workflow_app(apps)
    assert isinstance(app, ExecuteWorkflowApp)


def test_creation_with_args(apps: list[ExecuteWorkflowApp]) -> None:
    autosave = get_generic_parameter("autosave_results")
    autosave.value = True
    app = _get_exec_workflow_app(apps, autosave)
    assert app.get_param_value("autosave_results")


def test_creation_with_cmdargs(apps: list[ExecuteWorkflowApp]) -> None:
    ExecuteWorkflowApp.parse_func = lambda x: {"autosave_results": True}
    app = _get_exec_workflow_app(apps)
    assert app.get_param_value("autosave_results")


def test_prepare_mp_configuration(apps: list[ExecuteWorkflowApp]) -> None:
    app = _get_exec_workflow_app(apps)
    assert app._mp_manager_instance.__class__ == SyncManager
    for key in ("shapes_available", "shapes_set", "shapes_dict", "metadata_dict"):
        assert key in app.mp_manager


def test_prepare_mp_configuration__clone_mode(
    apps: list[ExecuteWorkflowApp],
) -> None:
    app = _get_exec_workflow_app(apps, clone_mode=True)
    assert app._mp_manager_instance is None
    assert app.mp_manager == {}


def test_reset_runtime_vars(apps: list[ExecuteWorkflowApp]) -> None:
    app = _get_exec_workflow_app(apps)
    app._index = 12
    app._config.update(
        {
            "result_metadata_set": True,
            "run_prepared": True,
        }
    )
    app._mp_tasks = np.arange(SCAN.n_points)
    app._shared_arrays = {1: np.ones((10, 10)), 2: np.ones((10, 10))}
    app.mp_manager["shapes_available"].set()
    app.mp_manager["shapes_set"].set()
    app.mp_manager["shapes_dict"] = {1: (10, 10), 2: (10, 10)}
    app.mp_manager["metadata_dict"] = {
        1: {
            "axis_labels": ["x", "y"],
            "axis_units": ["m", "m"],
            "axis_ranges": [(0, 1), (0, 1)],
        }
    }
    app.reset_runtime_vars()
    assert app._index is None
    assert not app._config["result_metadata_set"]
    assert not app._config["run_prepared"]
    assert app._mp_tasks.size == 0
    assert app._shared_arrays == {}
    assert not app.mp_manager["shapes_available"].is_set()
    assert not app.mp_manager["shapes_set"].is_set()


def test_store_context(apps: list[ExecuteWorkflowApp]) -> None:
    app = _get_exec_workflow_app(apps)
    app._store_context()
    assert app._config["tree_str_rep"] == TREE.export_to_string()
    for key, val in SCAN.get_param_values_as_dict(
        filter_types_for_export=True
    ).items():
        assert app._config["scan_context"][key] == val
    for key, val in EXP.get_param_values_as_dict(
        filter_types_for_export=True
    ).items():
        assert app._config["exp_context"][key] == val


def test_recreate_context__workflow_tree(apps: list[ExecuteWorkflowApp]) -> None:
    tree_rep = TREE.export_to_string()
    app = _get_exec_workflow_app(apps)
    app._config["tree_str_rep"] = TREE.export_to_string()
    TREE.clear()
    app._recreate_context()
    assert tree_rep == TREE.export_to_string()


def test_recreate_context__scan(apps: list[ExecuteWorkflowApp]) -> None:
    _init_scan()
    scan_copy = SCAN.get_param_values_as_dict()
    app = _get_exec_workflow_app(apps)
    app._config["scan_context"] = SCAN.get_param_values_as_dict(
        filter_types_for_export=True
    )
    SCAN.restore_all_defaults(True)
    app._recreate_context()
    for key, val in scan_copy.items():
        assert SCAN.get_param_value(key) == val


def test_recreate_context__diffraction_experiment(
    apps: list[ExecuteWorkflowApp],
) -> None:
    EXP.set_param_value("xray_energy", 42)
    exp_copy = EXP.get_param_values_as_dict()
    app = _get_exec_workflow_app(apps)
    app._config["exp_context"] = EXP.get_param_values_as_dict(
        filter_types_for_export=True
    )
    EXP.restore_all_defaults(True)
    app._recreate_context()
    for key, val in exp_copy.items():
        assert EXP.get_param_value(key) == val


def test_close_shared_arrays_and_memory__empty(
    apps: list[ExecuteWorkflowApp],
) -> None:
    app = _get_exec_workflow_app(apps)
    app.close_shared_arrays_and_memory()
    assert app._locals.get("shared_memory_buffers") == {}


def test_close_shared_arrays_and_memory(apps: list[ExecuteWorkflowApp]) -> None:
    app = _get_exec_workflow_app(apps)
    for key in (1, 2):
        app._locals["shared_memory_buffers"][key] = SharedMemory(
            create=True, size=100, name=f"test_{key}"
        )
    assert len(app._locals["shared_memory_buffers"]) == 2
    app.close_shared_arrays_and_memory()
    assert app._locals.get("shared_memory_buffers") == {}


def test_close_shared_arrays_and_memory__clone(
    apps: list[ExecuteWorkflowApp],
) -> None:
    main_app = _get_exec_workflow_app(apps)
    for key in (1, 2):
        share = SharedMemory(create=True, size=100, name=f"test_{key}")
        main_app._locals["shared_memory_buffers"][key] = share
    app = cast(ExecuteWorkflowApp, main_app.copy(clone_mode=True))
    apps.append(app)
    app.close_shared_arrays_and_memory()
    assert app._locals.get("shared_memory_buffers") == {}
    assert len(main_app._locals["shared_memory_buffers"]) == 2


def test_prepare_run__clone_mode(apps: list[ExecuteWorkflowApp]) -> None:
    _, app = _get_main_app_and_clone(apps)
    assert app._config["run_prepared"]


def test_prepare_run__main_mode(apps: list[ExecuteWorkflowApp]) -> None:
    app = _get_exec_workflow_app(apps)
    assert app._config["run_prepared"]


def test_prepare_run__main_no_autosave(apps: list[ExecuteWorkflowApp]) -> None:
    app = _get_exec_workflow_app(apps)
    app.set_param_value("autosave_results", False)
    app.prepare_run()
    assert app._config["run_prepared"]


def test_prepare_run__main_w_autosave(
    apps: list[ExecuteWorkflowApp], tmp_path_module: Path
) -> None:
    app = _get_exec_workflow_app(apps)
    app._config["export_files_prepared"] = True
    app.set_param_value("autosave_results", True)
    app.set_param_value("autosave_directory", tmp_path_module.joinpath("test"))
    app.prepare_run()
    assert not app._config["export_files_prepared"]


def test_multiprocessing_pre_cycle(apps: list[ExecuteWorkflowApp]) -> None:
    index = int(np.ceil(np.random.random() * 1e5))
    app = _get_exec_workflow_app(apps)
    app.multiprocessing_pre_cycle(index)
    assert index == app._index


def test_multiprocessing_carryon__not_live(
    apps: list[ExecuteWorkflowApp],
) -> None:
    app = _get_exec_workflow_app(apps)
    app.set_param_value("live_processing", False)
    assert app.multiprocessing_carryon()


def test_multiprocessing_carryon__live(apps: list[ExecuteWorkflowApp]) -> None:
    TREE.root.plugin.input_available = lambda x: x  # type: ignore[attr-defined]
    app = _get_exec_workflow_app(apps)
    app.prepare_run()
    app.set_param_value("live_processing", True)
    app._index = get_random_string(8)
    assert app.multiprocessing_carryon() == app._index


def test_signal_processed_and_can_continue__as_main(
    apps: list[ExecuteWorkflowApp],
) -> None:
    app = _get_exec_workflow_app(apps)
    app.mp_manager["shapes_set"].set()
    assert app.signal_processed_and_can_continue()


def test_signal_processed_and_can_continue__as_clone(
    apps: list[ExecuteWorkflowApp],
) -> None:
    main_app, app = _get_main_app_and_clone(apps)
    main_app.mp_manager["shapes_set"].set()
    assert app.signal_processed_and_can_continue()


def test_multiprocessing_func__as_main_app(apps: list[ExecuteWorkflowApp]) -> None:
    index = 12
    app = _get_exec_workflow_app(apps)
    app.prepare_run()
    app.mp_manager["shapes_dict"][1] = (12, 24)
    app.mp_manager["shapes_dict"][2] = (24, 12)
    res = app.multiprocessing_func(index)
    assert res == 0
    assert isinstance(app._shared_arrays[1], np.ndarray)
    assert isinstance(app._shared_arrays[2], np.ndarray)
    assert np.allclose(TREE.nodes[1].results, app._shared_arrays[1][0])
    assert np.allclose(TREE.nodes[2].results, app._shared_arrays[2][0])
    assert app.mp_manager["shapes_set"].is_set()


def test_multiprocessing_func__as_clone__fresh(
    apps: list[ExecuteWorkflowApp],
) -> None:
    index = 12
    main_app, app = _get_main_app_and_clone(apps)
    res = app.multiprocessing_func(index)
    tree_res = TREE.get_current_results()
    assert main_app.mp_manager["shapes_available"].is_set()
    assert res is None
    for key, data in tree_res.items():
        shape = data.shape
        assert main_app.mp_manager["shapes_dict"][key], shape
        for attr in ["axis_labels", "axis_units", "data_unit", "data_label"]:
            stored_data = main_app.mp_manager["metadata_dict"][key]
            assert getattr(data, attr) == stored_data[attr]
        for dim in range(data.ndim):
            assert np.allclose(
                data.axis_ranges[dim],
                main_app.mp_manager["metadata_dict"][key]["axis_ranges"][dim],
            )


def test_multiprocessing_func__as_clone__main_app_configured(
    apps: list[ExecuteWorkflowApp],
) -> None:
    index = 12
    main_app, app = _get_main_app_and_clone(apps)
    _ = main_app.multiprocessing_func(index)
    _ = main_app.multiprocessing_func(index)
    buffer_index: Integral | None = None
    for _ in range(4):
        buffer_index = app.multiprocessing_func(index)
    assert buffer_index is not None
    tree_res = TREE.get_current_results()
    res1 = main_app._shared_arrays[1][buffer_index]
    res2 = main_app._shared_arrays[2][buffer_index]
    assert np.allclose(res1, tree_res[1])
    assert np.allclose(res2, tree_res[2])


def test_publish_shapes_and_metadata_to_manager__with_dataset(
    apps: list[ExecuteWorkflowApp],
) -> None:
    app = _get_exec_workflow_app(apps)
    TREE.execute_process(0)
    app._publish_shapes_and_metadata_to_manager()
    assert app.mp_manager["shapes_available"].is_set()
    for key, res in TREE.get_current_results().items():
        assert app.mp_manager["shapes_dict"][key] == res.shape
        assert app.mp_manager["metadata_dict"][key]["axis_labels"] == res.axis_labels
        assert app.mp_manager["metadata_dict"][key]["axis_units"] == res.axis_units
        assert app.mp_manager["metadata_dict"][key]["data_unit"] == res.data_unit
        assert app.mp_manager["metadata_dict"][key]["data_label"] == res.data_label
        for dim in range(res.ndim):
            assert np.allclose(
                res.axis_ranges[dim],
                app.mp_manager["metadata_dict"][key]["axis_ranges"][dim],
            )


def test_publish_shapes_and_metadata_to_manager__with_ndarray(
    apps: list[ExecuteWorkflowApp],
) -> None:
    TREE.delete_node_by_id(2)
    TREE.execute_process(0)
    TREE.nodes[1].results = TREE.nodes[1].results.array
    app = _get_exec_workflow_app(apps)
    app._publish_shapes_and_metadata_to_manager()
    assert app.mp_manager["shapes_available"].is_set()
    for key, res in TREE.get_current_results().items():
        assert app.mp_manager["shapes_dict"][key] == res.shape
        for dim in range(res.ndim):
            assert isinstance(
                app.mp_manager["metadata_dict"][key]["axis_labels"][dim], str
            )
            assert isinstance(
                app.mp_manager["metadata_dict"][key]["axis_units"][dim], str
            )
            assert isinstance(
                app.mp_manager["metadata_dict"][key]["axis_ranges"][dim], np.ndarray
            )
            assert isinstance(app.mp_manager["metadata_dict"][key]["data_unit"], str)
            assert isinstance(app.mp_manager["metadata_dict"][key]["data_label"], str)


def test_create_shared_memory__not_set(apps: list[ExecuteWorkflowApp]) -> None:
    app = _get_exec_workflow_app(apps)
    with pytest.raises(UserConfigError):
        app._create_shared_memory()


def test_create_shared_memory__memory_buffer_not_empty(
    apps: list[ExecuteWorkflowApp],
) -> None:
    app = _get_exec_workflow_app(apps)
    app.prepare_run()
    app.mp_manager["shapes_available"].set()
    app._locals["shared_memory_buffers"][1] = SharedMemory(
        create=True, size=100, name="test"
    )
    with pytest.raises(UserConfigError):
        app._create_shared_memory()


def test_check_size_of_results_and_buffer__buffer_too_small(
    apps: list[ExecuteWorkflowApp],
) -> None:
    app = _get_exec_workflow_app(apps)
    max_size = int(app.q_settings_get("global/shared_buffer_size", float))
    app.mp_manager["shapes_dict"] = {1: tuple(max_size * 500 for _ in range(3))}
    with pytest.raises(UserConfigError):
        app._check_size_of_results_and_buffer()


def test_check_size_of_results_and_buffer__buffer_okay(
    apps: list[ExecuteWorkflowApp],
) -> None:
    app = _get_exec_workflow_app(apps)
    app._mp_tasks = np.arange(SCAN.n_points)
    app.mp_manager["shapes_dict"] = {1: (10, 10), 2: (10, 10)}
    app._check_size_of_results_and_buffer()
    assert app.mp_manager["buffer_n"].value > 0


def test_initialize_shared_memory(apps: list[ExecuteWorkflowApp]) -> None:
    app = _get_exec_workflow_app(apps)
    app.mp_manager["buffer_n"].value = 10
    app.mp_manager["shapes_dict"] = {1: (10, 10), 2: (10, 10)}
    app.mp_manager["shapes_available"].set()
    app._initialize_shared_memory()
    assert app.mp_manager["shapes_set"].is_set()
    assert app.mp_manager["buffer_n"].value > 0
    for key in list(app.mp_manager["shapes_dict"].keys()):
        label = f"node_{key:03d}"
        assert isinstance(
            app._locals["shared_memory_buffers"][label],
            SharedMemory,
        )
    assert isinstance(
        app._locals["shared_memory_buffers"]["in_use_flag"],
        SharedMemory,
    )


def test_initialize_arrays_from_shared_memory(
    apps: list[ExecuteWorkflowApp],
) -> None:
    main_app = _get_exec_workflow_app(apps)
    main_app.mp_manager["shapes_dict"] = {1: (10, 10), 2: (10, 10)}
    main_app.mp_manager["buffer_n"].value = 10
    main_app._initialize_shared_memory()
    app = cast(ExecuteWorkflowApp, main_app.copy(clone_mode=True))
    apps.append(app)
    app._initialize_arrays_from_shared_memory()
    for key in (1, 2):
        assert isinstance(app._shared_arrays[key], np.ndarray)
        assert app._shared_arrays[key].shape == (10, 10, 10)
    assert isinstance(app._shared_arrays["in_use_flag"], np.ndarray)


def test_get_shared_memory__in_buffer(apps: list[ExecuteWorkflowApp]) -> None:
    app = _get_exec_workflow_app(apps)
    _ = app.mp_manager["main_pid"].value
    share = mp.shared_memory.SharedMemory(create=True, size=100, name="test")
    app._locals["shared_memory_buffers"]["test"] = share
    res = _get_shared_memory(app, "test")
    assert isinstance(res, SharedMemory)
    assert id(share) == id(res)


def test_get_shared_memory__new(
    apps: list[ExecuteWorkflowApp],
    shares: list[SharedMemory],
) -> None:
    app = _get_exec_workflow_app(apps)
    share = SharedMemory(
        create=True,
        size=100,
        name=f"share_node_001_{app.mp_manager['main_pid'].value}",
    )
    shares.append(share)
    res = _get_shared_memory(app, "node_001")
    assert isinstance(res, mp.shared_memory.SharedMemory)
    res.close()


def test_write_results_to_shared_arrays__arrays_not_created(
    apps: list[ExecuteWorkflowApp],
) -> None:
    TREE.execute_process(0)
    app = _get_exec_workflow_app(apps)
    app._publish_shapes_and_metadata_to_manager()
    app._check_size_of_results_and_buffer()
    app._initialize_shared_memory()
    _write_results_to_shared_arrays(app)
    for key, data in TREE.get_current_results().items():
        assert np.allclose(data, app._shared_arrays[key][0])


def test_write_results_to_shared_arrays__arrays_created(
    apps: list[ExecuteWorkflowApp],
) -> None:
    TREE.execute_process(0)
    app = _get_exec_workflow_app(apps)
    app._publish_shapes_and_metadata_to_manager()
    app._create_shared_memory()
    _write_results_to_shared_arrays(app)
    for key, data in TREE.get_current_results().items():
        assert np.allclose(data, app._shared_arrays[key][0])


def test_must_send_signal_and_wait_for_response(
    apps: list[ExecuteWorkflowApp],
) -> None:
    app = _get_exec_workflow_app(apps)
    sig = app.must_send_signal_and_wait_for_response()
    assert sig == "::shapes_not_set::"


def test_must_send_signal_and_wait_for_response__shapes_set(
    apps: list[ExecuteWorkflowApp],
) -> None:
    app = _get_exec_workflow_app(apps)
    app.mp_manager["shapes_set"].set()
    sig = app.must_send_signal_and_wait_for_response()
    assert sig is None


def test_get_latest_results__shapes_not_set(
    apps: list[ExecuteWorkflowApp],
) -> None:
    _, app = _get_main_app_and_clone(apps)
    assert app.get_latest_results() is None


def test_get_latest_results__shapes_set(apps: list[ExecuteWorkflowApp]) -> None:
    main_app, app = _get_main_app_and_clone(apps)
    _ = main_app.multiprocessing_func(0)
    index = app.get_latest_results()
    assert isinstance(index, Integral)
    for key, data in TREE.get_current_results().items():
        assert np.allclose(data, app._shared_arrays[key][index])


def test_received_signal_message__shapes_not_set(
    apps: list[ExecuteWorkflowApp],
) -> None:
    main_app, app = _get_main_app_and_clone(apps)
    index = app.multiprocessing_func(0)
    assert index is None
    main_app.received_signal_message("::shapes_not_set::")
    assert main_app.mp_manager["shapes_set"].is_set()
    for key in main_app.mp_manager["shapes_dict"]:
        assert isinstance(main_app._shared_arrays[key], np.ndarray)


def test_multiprocessing_store_results_as_clone(
    apps: list[ExecuteWorkflowApp],
) -> None:
    _, app = _get_main_app_and_clone(apps)
    spy = QtTest.QSignalSpy(app.sig_results_updated)
    index = app.multiprocessing_func(0)
    _store_results(app, 0, index)
    spy_result = spy.count() if IS_QT6 else len(spy)
    assert spy_result == 0


def test_multiprocessing_store_results__processing_error(
    apps: list[ExecuteWorkflowApp],
) -> None:
    main_app, _ = _get_main_app_and_clone(apps)
    spy = QtTest.QSignalSpy(main_app.sig_results_updated)
    index = main_app.multiprocessing_func(0)
    _store_results(main_app, 0, -1)
    spy_result = spy.count() if IS_QT6 else len(spy)
    assert spy_result == 0


def test_multiprocessing_store_results(apps: list[ExecuteWorkflowApp]) -> None:
    main_app, _ = _get_main_app_and_clone(apps)
    spy = QtTest.QSignalSpy(main_app.sig_results_updated)
    index = main_app.multiprocessing_func(0)
    _store_results(main_app, 0, index)
    spy_result = spy.count() if IS_QT6 else len(spy)
    assert spy_result == 1
    assert main_app._config["result_metadata_set"]
    result_index = cast(Any, SCAN.get_indices_from_ordinal(0))
    assert np.all(RESULTS._composites[1][result_index] > 0)


@pytest.mark.slow
def test_multiprocessing_store_results__autosave(
    apps: list[ExecuteWorkflowApp], tmp_path_module: Path
) -> None:
    main_app, _ = _get_main_app_and_clone(apps)
    main_app.set_param_value("autosave_results", True)
    main_app.set_param_value("autosave_directory", tmp_path_module.joinpath("test"))
    index = main_app.multiprocessing_func(0)
    _store_results(main_app, 0, index)
    node_id = 1
    fname = tmp_path_module.joinpath("test", f"node_{node_id:02d}.nxs")
    assert main_app._config["export_files_prepared"]
    with h5py.File(fname, "r") as f:
        data = f["entry/data/data"][SCAN.get_indices_from_ordinal(0)]
        assert np.all(data > 0)


def test_multiprocessing_store_results__repetitive(
    apps: list[ExecuteWorkflowApp],
) -> None:
    main_app, _ = _get_main_app_and_clone(apps)
    spy = QtTest.QSignalSpy(main_app.sig_results_updated)
    i_dim = SCAN.ndim - 1
    for i in range(SCAN.shape[i_dim]):
        index = main_app.multiprocessing_func(i)
        _store_results(main_app, i, index)
    spy_result = spy.count() if IS_QT6 else len(spy)
    assert spy_result == SCAN.shape[i_dim]
    slices = cast(Any, (0,) * i_dim + (slice(None),))
    assert np.all(RESULTS._composites[1][slices] > 0)


def test_multiprocessing_store_results__w_main_app_and_clone(
    apps: list[ExecuteWorkflowApp],
) -> None:
    main_app, app = _get_main_app_and_clone(apps)
    spy = QtTest.QSignalSpy(main_app.sig_results_updated)
    i_dim = SCAN.ndim - 1
    for i in range(SCAN.shape[i_dim]):
        index = app.multiprocessing_func(i)
        if index is None:
            main_app._create_shared_memory()
            index = app.get_latest_results()
        _store_results(main_app, i, index)
    spy_result = spy.count() if IS_QT6 else len(spy)
    assert spy_result == SCAN.shape[i_dim]
    # noinspection PyTypeChecker
    assert np.all(RESULTS._composites[1][(0,) * i_dim + (slice(None),)] > 0)


@pytest.mark.slow
def test_run(apps: list[ExecuteWorkflowApp]) -> None:
    app = _get_exec_workflow_app(apps)
    SCAN.set_param_value("scan_dim", 2)
    app.run()
    res = RESULTS.get_results(1)
    assert np.all(res > 0)


@pytest.mark.slow
def test_run__repetitive(apps: list[ExecuteWorkflowApp]) -> None:
    app = _get_exec_workflow_app(apps)
    SCAN.set_param_value("scan_dim", 2)
    app.run()
    app.run()
    res = RESULTS.get_results(1)
    assert np.all(res > 0)


def test_copy__to_clone(apps: list[ExecuteWorkflowApp]) -> None:
    main_app = _get_exec_workflow_app(apps)
    keys = cast(list[str], ExecuteWorkflowApp.attributes_not_to_copy_to_app_clone)
    for key in keys:
        if key == "_mp_manager_instance":
            continue
        setattr(main_app, key, get_random_string(8))
    main_app._locals = {1: 1, 2: 2}
    main_app.mp_manager["shapes_available"].set()
    app_clone = cast(ExecuteWorkflowApp, main_app.copy(clone_mode=True))
    apps.append(app_clone)
    for key in keys:
        if isinstance(getattr(main_app, key), np.ndarray) and isinstance(
            getattr(app_clone, key), np.ndarray
        ):
            assert np.allclose(getattr(main_app, key), getattr(app_clone, key))
        elif isinstance(getattr(main_app, key), np.ndarray) != isinstance(
            getattr(app_clone, key), np.ndarray
        ):
            pass
        else:
            assert getattr(main_app, key) != getattr(app_clone, key)
    assert app_clone._locals == {"shared_memory_buffers": {}}  # type: ignore[attr-defined]
    for key in main_app.mp_manager:
        assert main_app.mp_manager[key] == app_clone.mp_manager[key]


@pytest.mark.slow
def test__run_in_processor_with_clone_worker(
    apps: list[ExecuteWorkflowApp],
) -> None:
    _run_processor_with_clone_worker(apps)


@pytest.mark.slow
def test__repeated_run_in_processor_with_clone_worker(
    apps: list[ExecuteWorkflowApp],
) -> None:
    main_app = _run_processor_with_clone_worker(apps)
    _ = apps.pop()
    main_app.deleteLater()
    main_app = None
    _run_processor_with_clone_worker(apps)


if __name__ == "__main__":
    pytest.main([__file__])

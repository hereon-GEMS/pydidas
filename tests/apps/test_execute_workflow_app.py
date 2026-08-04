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

import threading
import time
from collections.abc import Iterator
from multiprocessing.managers import SyncManager
from pathlib import Path
from unittest.mock import MagicMock, patch

import h5py
import numpy as np
import pytest

from pydidas import unittest_objects
from pydidas.apps import ExecuteWorkflowApp
from pydidas.contexts import DiffractionExperimentContext, ScanContext
from pydidas.core import (
    FileReadError,
    PydidasQsettings,
    UserConfigError,
    get_generic_parameter,
)
from pydidas.core.utils import get_random_string
from pydidas.plugins import PluginCollection
from pydidas.unittest_objects import SignalSpy
from pydidas.workflow import WorkflowResults, WorkflowTree
from pydidas_qtcore import PydidasQApplication


COLL = PluginCollection()
EXP = DiffractionExperimentContext()
SCAN = ScanContext()
TREE = WorkflowTree()
RESULTS = WorkflowResults()

_NSCAN = (9, 5, 7)
_SCANDELTA = (0.1, -0.2, 1.1)
_SCANOFFSET = (-5, 0, 1.2)


@pytest.fixture(scope="module")
def qsettings():
    _qsettings = PydidasQsettings()
    _all_settings = _qsettings.get_all_stored_q_settings()
    yield _qsettings
    for _key, _val in _all_settings.items():
        _qsettings.set_value(_key, _val)


@pytest.fixture(scope="module", autouse=True)
def module_setup() -> Iterator[None]:
    plugin_file = unittest_objects.__file__
    assert plugin_file is not None
    plugin_path = Path(plugin_file).parent
    added_plugin_path = plugin_path not in COLL.registered_paths
    if added_plugin_path:
        COLL.find_and_register_plugins(plugin_path)
    yield
    if added_plugin_path and plugin_path in COLL.registered_paths:
        COLL.unregister_plugin_path(plugin_path)


@pytest.fixture(autouse=True)
def reset_contexts(qsettings, random_scan, random_diff_exp, dummy_tree):
    TREE.clear()
    TREE.update_from_tree(dummy_tree)
    SCAN.update_from_scan(random_scan)
    EXP.update_from_diffraction_exp(random_diff_exp)
    yield


@pytest.fixture
def app():
    app = ExecuteWorkflowApp()
    yield app
    app.q_settings_set("global/mp_n_workers", 2)
    app.close_shared_arrays_and_memory()


@pytest.fixture
def app_clone(app):
    _app = app.copy(clone_mode=True)
    _app._store_context()
    yield _app
    _app.close_shared_arrays_and_memory()


@pytest.fixture(scope="module")
def tmp_path_module(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Path]:
    yield tmp_path_factory.mktemp("test_execute_workflow_app")


@pytest.fixture
def app_list() -> Iterator[list[ExecuteWorkflowApp]]:
    created_apps = []
    yield created_apps
    for app in created_apps:
        app.close_shared_arrays_and_memory()


@pytest.mark.slow
def test_creation__w_args(app_list) -> None:
    autosave = get_generic_parameter("autosave_results")
    autosave.value = True
    app = ExecuteWorkflowApp(autosave)
    app_list.append(app)
    assert app.get_param_value("autosave_results")


@pytest.mark.slow
def test_creation__w_cmdargs(app_list) -> None:
    with patch.object(
        ExecuteWorkflowApp, "parse_func", lambda x: {"autosave_results": True}
    ):
        app = ExecuteWorkflowApp()
        app_list.append(app)
        assert app.get_param_value("autosave_results")


@pytest.mark.slow
@pytest.mark.parametrize("clone_mode", [True, False])
def test_creation__mp_configuration(app_list, clone_mode) -> None:
    app = ExecuteWorkflowApp(clone_mode=clone_mode)
    app_list.append(app)
    if clone_mode:
        assert app._mp_manager_instance is None
    else:
        assert app._mp_manager_instance.__class__ == SyncManager
    for key in ("shapes_available", "shapes_set", "shapes_dict", "metadata_dict"):
        assert (key in app.mp_manager) == (not clone_mode)


@pytest.mark.slow
def test_prepare_run__reset_shared_runtime_vars(app) -> None:
    app._shared_arrays = {1: np.ones((10, 10)), 2: np.ones((10, 10))}
    app.mp_manager["shapes_available"].set()
    app.mp_manager["shapes_set"].set()
    app.mp_manager["shapes_dict"] = {1: (10, 10), 2: (10, 10)}
    app.mp_manager["metadata_dict"] = {1: {"axis_labels": ["x", "y"]}}
    app.prepare_run()
    assert not app._config["result_metadata_set"]
    assert app._shared_arrays == {}
    assert not app.mp_manager["shapes_available"].is_set()
    assert not app.mp_manager["shapes_set"].is_set()
    assert app.mp_manager["metadata_dict"] == {}


@pytest.mark.slow
def test_prepare_run__sets_basic_variables(app, random_scan) -> None:
    app._index = 42
    app._mp_tasks = None
    assert not app._config["run_prepared"]
    app.prepare_run()
    assert app._index == -1
    assert app._mp_tasks.size == random_scan.n_points
    assert app._config["run_prepared"]
    assert not app._config["export_files_prepared"]
    assert TREE._pre_executed


@pytest.mark.slow
def test_multiprocessing_pre_run(app) -> None:
    app.multiprocessing_pre_run()
    assert app._config["run_prepared"] is True


@pytest.mark.slow
def test_prepare_run__stores_context(
    app, random_scan, dummy_tree, random_diff_exp
) -> None:
    assert app._config["tree_str_rep"] == "[]"
    assert app._config["scan_context"] == {}
    assert app._config["exp_context"] == {}
    app.prepare_run()
    assert app._config["tree_str_rep"] == dummy_tree.export_to_string()
    assert app._config["scan_context"] == random_scan.param_export_values
    assert app._config["exp_context"] == random_diff_exp.param_export_values


@pytest.mark.slow
def test_prepare_run__recreates_context_if_clone(
    app_clone, random_scan, dummy_tree, random_diff_exp
) -> None:
    TREE.clear()
    SCAN.restore_all_defaults(True)
    EXP.restore_all_defaults(True)
    app_clone._config["tree_str_rep"] = dummy_tree.export_to_string()
    app_clone._config["scan_context"] = random_scan.param_export_values
    app_clone._config["exp_context"] = random_diff_exp.param_export_values
    app_clone.prepare_run()
    for _id, _node in TREE.nodes.items():
        assert hash(_node) == hash(dummy_tree.nodes[_id])
    assert EXP.param_values == random_diff_exp.param_values
    assert SCAN.param_values == random_scan.param_values


@pytest.mark.slow
def test_close_shared_arrays_and_memory__empty(app) -> None:
    app.close_shared_arrays_and_memory()
    assert app._locals.get("shared_memory_buffers") == {}
    assert app._shared_arrays == {}


@pytest.mark.slow
def test_close_shared_arrays_and_memory(app) -> None:
    app.prepare_run()
    app.multiprocessing_func(0)
    assert app._locals["shared_memory_buffers"]  # assert not empty
    assert app._shared_arrays  # assert not empty
    app.close_shared_arrays_and_memory()
    assert app._locals.get("shared_memory_buffers") == {}
    assert app._shared_arrays == {}


@pytest.mark.slow
def test_close_shared_arrays_and_memory__error_handling(app) -> None:
    app.prepare_run()
    app.multiprocessing_func(0)
    buffer = app._locals["shared_memory_buffers"]["in_use_flag"]
    original_unlink = buffer.unlink
    buffer.unlink = lambda: (_ for _ in ()).throw(FileNotFoundError(""))
    app.close_shared_arrays_and_memory()
    buffer.unlink = original_unlink
    assert app._locals.get("shared_memory_buffers") == {}
    assert app._shared_arrays == {}


@pytest.mark.slow
def test_multiprocessing_get_tasks(app, random_scan) -> None:
    app.prepare_run()
    assert np.allclose(app.multiprocessing_get_tasks(), np.arange(random_scan.n_points))


@pytest.mark.slow
def test_multiprocessing_pre_cycle(app) -> None:
    index = 47
    app.multiprocessing_pre_cycle(index)
    assert index == app._index


@pytest.mark.slow
def test_multiprocessing_carryon__not_live(app) -> None:
    app.set_param_value("live_processing", False)
    assert app.multiprocessing_carryon()


@pytest.mark.slow
def test_multiprocessing_carryon__live(app) -> None:
    TREE.root.plugin.input_available = lambda x: x  # type: ignore[attr-defined]
    app.prepare_run()
    app.set_param_value("live_processing", True)
    app._index = get_random_string(8)
    assert app.multiprocessing_carryon() == app._index


@pytest.mark.slow
@pytest.mark.parametrize("valid", [True, False])
def test_signal_processed_and_can_continue__as_main(app, valid) -> None:
    if valid:
        app.mp_manager["shapes_set"].set()
    else:
        app.mp_manager["shapes_set"].clear()
    assert app.signal_processed_and_can_continue() == valid


@pytest.mark.slow
@pytest.mark.parametrize("valid", [True, False])
def test_signal_processed_and_can_continue__as_clone(app, app_list, valid) -> None:
    app.prepare_run()
    clone = app.copy(clone_mode=True)
    app_list.append(clone)
    if valid:
        app.mp_manager["shapes_set"].set()
    else:
        app.mp_manager["shapes_set"].clear()
    assert clone.signal_processed_and_can_continue() == valid


@pytest.mark.slow
@pytest.mark.parametrize("clone", [True, False])
def test_multiprocessing_func__w_FileReadError(app, app_list, clone) -> None:
    app.prepare_run()
    if clone:
        _main = app
        app = _main.copy(clone_mode=True)
        app_list.append(app)
    with patch.object(TREE, "execute_process", side_effect=FileReadError("test")):  # type: ignore[ref]
        assert app.multiprocessing_func(1) == -1


@pytest.mark.slow
def test_multiprocessing_func__w_full_buffer(app, app_list) -> None:
    app.prepare_run()
    app_clone = app.copy(clone_mode=True)
    app_list.append(app_clone)
    _res = app_clone.multiprocessing_func(0)
    _signal = app_clone.must_send_signal_and_wait_for_response()
    app.received_signal_message(_signal)
    app._shared_arrays["in_use_flag"][:] = 1
    # Verify that get_latest_results blocks when all buffer slots are occupied
    result_holder = []
    thread = threading.Thread(
        target=lambda: result_holder.append(app_clone.get_latest_results())
    )
    thread.daemon = True  # let the thread stop with the test process
    thread.start()
    thread.join(timeout=0.2)
    assert thread.is_alive()  # i.e. app_clone is still waiting on free buffer
    with app.mp_manager["lock"]:
        app._shared_arrays["in_use_flag"][:] = 0
    time.sleep(0.01)
    assert len(result_holder) == 1
    assert not thread.is_alive()


@pytest.mark.slow
@pytest.mark.parametrize("clone", [True, False])
def test_multiprocessing_func__w_shapes_available_not_set(app, app_list, clone) -> None:
    app.prepare_run()
    if clone:
        _main = app
        app = _main.copy(clone_mode=True)
        app_list.append(app)
    assert not app.mp_manager["shapes_available"].is_set()
    _ret_val = app.multiprocessing_func(1)
    for _id, _res in TREE.get_current_results().items():
        assert app.mp_manager["shapes_dict"][_id] == _res.shape
        assert _id in app.mp_manager["metadata_dict"]
        assert app.mp_manager["shapes_available"].is_set()
    assert RESULTS._config["metadata_complete"] == (not clone)


@pytest.mark.slow
@pytest.mark.parametrize("clone", [True, False])
def test_multiprocessing_func__w_shapes_not_set(app, app_list, clone) -> None:
    app.prepare_run()
    if clone:
        _main = app
        app = _main.copy(clone_mode=True)
        app_list.append(app)
    assert not app.mp_manager["shapes_set"].is_set()
    # manually patch a result to include a non-Dataset return value:
    TREE.execute_process(1)
    _tree_res = TREE.get_current_results()
    _tree_res[1] = np.array(_tree_res[1])
    with patch.object(TREE, "get_current_results", lambda: _tree_res):
        _ret_val = app.multiprocessing_func(1)
    if app.clone_mode:
        assert _ret_val is None
        for _id, _res in TREE.get_current_results().items():
            assert _id in app._config["latest_results"]
    else:  # main app:
        assert app.mp_manager["shapes_set"].is_set()
        assert "in_use_flag" in app._locals["shared_memory_buffers"]
        assert "in_use_flag" in app._shared_arrays
        for _id in TREE.get_current_results().keys():
            assert f"node_{_id:03d}" in app._locals["shared_memory_buffers"]
            assert _id in app._shared_arrays


@pytest.mark.slow
def test_multiprocessing_func__w_buffer_too_small(app) -> None:
    SCAN.set_param_value("scan_dim", 1)
    TREE.root.plugin.set_param_value("image_width", 5000)
    TREE.root.plugin.set_param_value("image_height", 5000)
    app.prepare_run()
    app.q_settings_set("global/mp_n_workers", 30)
    with pytest.raises(UserConfigError):
        app.multiprocessing_func(0)


@pytest.mark.slow
@pytest.mark.parametrize("clone", [True, False])
@pytest.mark.parametrize("used_buffers", [0, 4])
def test_multiprocessing_func__all_ready(app, app_list, clone, used_buffers) -> None:
    app.prepare_run()
    app.multiprocessing_func(0)
    app._shared_arrays["in_use_flag"][:] = 0
    if used_buffers:
        app._shared_arrays["in_use_flag"][:used_buffers] = 1
    if clone:
        _main = app
        app = _main.copy(clone_mode=True)
        app_list.append(app)
    _ret_val = app.multiprocessing_func(1)
    assert _ret_val == used_buffers
    for _id, _tree_res in TREE.get_current_results().items():
        assert np.allclose(app._shared_arrays[_id][used_buffers], _tree_res)


@pytest.mark.slow
@pytest.mark.parametrize("shapes_set", [True, False])
@pytest.mark.parametrize("message", ["::shapes_not_set::", "::other_message::"])
def test_received_signal_message(app, shapes_set, message) -> None:
    if shapes_set:
        app.mp_manager["shapes_set"].set()
    else:
        app.mp_manager["shapes_set"].clear()
    _mock = MagicMock()
    with patch.object(app, "_create_shared_memory", _mock):
        app.received_signal_message(message)
    assert _mock.called == (message == "::shapes_not_set::" and not shapes_set)


@pytest.mark.slow
def test_multiprocessing_post_run(app) -> None:
    app.prepare_run()
    app.multiprocessing_func(0)
    assert len(app._shared_arrays) > 0
    app.multiprocessing_post_run()
    assert app._shared_arrays == {}
    assert app._locals["shared_memory_buffers"] == {}


@pytest.mark.slow
@pytest.mark.parametrize("clone", [True, False])
@pytest.mark.parametrize("shapes_set", [True, False])
def test_must_send_signal_and_wait_for_response(
    app, app_clone, clone, shapes_set
) -> None:
    if clone:
        app = app_clone
    app.prepare_run()
    if shapes_set:
        app.mp_manager["shapes_set"].set()
    else:
        app.mp_manager["shapes_set"].clear()
    _ret_val = app.must_send_signal_and_wait_for_response()
    if shapes_set:
        assert _ret_val is None
    else:
        assert _ret_val == "::shapes_not_set::"


@pytest.mark.slow
@pytest.mark.parametrize("clone", [True, False])
@pytest.mark.parametrize("shapes_set", [True, False])
def test_get_latest_results(app, clone, shapes_set) -> None:
    app.prepare_run()
    app.multiprocessing_func(0)
    TREE.execute_process(1)
    if not shapes_set:
        app.mp_manager["shapes_set"].clear()
        assert app.get_latest_results() is None
    else:
        _buffer_pos = app.get_latest_results()
        for _id, _res in TREE.get_current_results().items():
            assert np.allclose(app._shared_arrays[_id][_buffer_pos], _res)


@pytest.mark.slow
def test_multiprocessing_store_results__as_clone(app_clone) -> None:
    app_clone.prepare_run()
    _i_buffer = app_clone.multiprocessing_func(0)
    assert app_clone.multiprocessing_store_results(0, _i_buffer) is None


@pytest.mark.slow
def test_multiprocessing_store_results__w_o_shared_arrays(app, app_list) -> None:
    app.prepare_run()
    _clone = app.copy(clone_mode=True)
    app_list.append(_clone)
    assert app._shared_arrays == {}


@pytest.mark.slow
def test_multiprocessing_store_results__w_invalid_index(app):
    app.prepare_run()
    app.multiprocessing_func(0)
    _mock = MagicMock()
    with patch.object(PydidasQApplication, "set_status_message", _mock):
        app.multiprocessing_store_results(0, -1)
    assert _mock.called


@pytest.mark.slow
@pytest.mark.parametrize("metadata_set", [True, False])
def test_multiprocessing_store_results__check_metadata_set(app, metadata_set):
    app.prepare_run()
    _index = app.multiprocessing_func(0)
    if not metadata_set:
        app._config["result_metadata_set"] = metadata_set
        RESULTS._config["metadata_complete"] = metadata_set
    app.multiprocessing_store_results(0, _index)
    assert app._config["result_metadata_set"]
    assert RESULTS._config["metadata_complete"]


@pytest.mark.slow
def test_multiprocessing_store_results__from_clone(app, app_list):
    app.prepare_run()
    _clone = app.copy(clone_mode=True)
    app_list.append(_clone)
    _res = _clone.multiprocessing_func(0)
    assert _res is None  # because shared memory is not yet set up
    app._create_shared_memory()  # simulates main app creating shared memory after signal
    _index = _clone.get_latest_results()  # clone writes results and returns buffer pos
    app.multiprocessing_store_results(0, _index)
    assert app._config["result_metadata_set"]
    assert RESULTS._config["metadata_complete"]


@pytest.mark.slow
def test_multiprocessing_store_results__results_correctly_updated(app):
    spy = SignalSpy(app.sig_results_updated)
    app.prepare_run()
    _index = app.multiprocessing_func(0)
    app.multiprocessing_store_results(0, _index)
    assert app._shared_arrays["in_use_flag"][_index] == 0
    for _id, _result in TREE.get_current_results().items():
        _full_res = RESULTS.get_results(_id)
        _stored = _full_res[(0,) * SCAN.ndim]
        assert np.allclose(_stored, _result)
    assert spy.n == 1


@pytest.mark.slow
def test_multiprocessing_store_results__w_autosave(app, empty_temp_path):
    app.set_param_value("autosave_results", True)
    app.set_param_value("autosave_directory", empty_temp_path)
    app.prepare_run()
    _scan_index = (0,) * SCAN.ndim
    _index = app.multiprocessing_func(0)
    app.multiprocessing_store_results(0, _index)
    assert app._shared_arrays["in_use_flag"][_index] == 0
    for _id, _result in TREE.get_current_results().items():
        _full_res = RESULTS.get_results(_id)
        _stored = _full_res[_scan_index]
        assert np.allclose(_stored, _result)
        with h5py.File(empty_temp_path / f"node_{_id:02d}.nxs", "r") as _h5file:
            _data = _h5file["entry/data/data"][_scan_index]
        assert np.allclose(_data, _result)


@pytest.mark.slow
def test_multiprocessing_store_results__w_None(app):
    app.prepare_run()
    with pytest.raises(RuntimeError):
        app.multiprocessing_store_results(0, None)


@pytest.mark.slow
@pytest.mark.parametrize("clone_mode", [True, False])
def test_deleteLater(clone_mode):
    app = ExecuteWorkflowApp(clone_mode=clone_mode)
    app._store_context()
    app.prepare_run()
    app.deleteLater()
    assert app._locals["shared_memory_buffers"] == {}


@pytest.mark.parametrize("clone_mode", [True, False])
def test_deleteLater__repeated_calls(clone_mode):
    app = ExecuteWorkflowApp(clone_mode=clone_mode)
    app._store_context()
    app.prepare_run()
    app.deleteLater()
    app.deleteLater()
    assert app._locals["shared_memory_buffers"] == {}


@pytest.mark.parametrize("clone_mode", [True, False])
def test_deleteLater__on_uninitialized_app(clone_mode):
    app = ExecuteWorkflowApp(clone_mode=clone_mode)
    app.deleteLater()
    assert app._locals["shared_memory_buffers"] == {}


@pytest.mark.slow
@pytest.mark.parametrize("autosave", [True, False])
def test__full_run(app, app_list, autosave, empty_temp_path):
    SCAN.set_param_value("scan_dim0_n_points", 2)
    SCAN.set_param_value("scan_dim1_n_points", 3)
    SCAN.set_param_value("scan_dim2_n_points", 4)
    app.set_param_value("autosave_results", autosave)
    app.set_param_value("autosave_directory", empty_temp_path)
    app.prepare_run()
    app_clone = app.copy(clone_mode=True)
    for _task in app.multiprocessing_get_tasks():
        _res = app_clone.multiprocessing_func(_task)
        if _task == 0:
            _signal = app_clone.must_send_signal_and_wait_for_response()
            assert _res is None
            assert _signal == "::shapes_not_set::"
            app.received_signal_message(_signal)
            assert app_clone.signal_processed_and_can_continue()
            _res = app_clone.get_latest_results()
        app.multiprocessing_store_results(_task, _res)
    for _id in RESULTS.shapes:
        _arr = RESULTS.get_results(_id)
        assert np.count_nonzero(_arr) == _arr.size
        if autosave:
            with h5py.File(empty_temp_path / f"node_{_id:02d}.nxs", "r") as _h5file:
                _file_data = _h5file["entry/data/data"][:]
            assert np.allclose(_file_data, _arr)


if __name__ == "__main__":
    pytest.main([__file__])

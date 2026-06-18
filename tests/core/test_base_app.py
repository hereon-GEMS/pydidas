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
import shutil
import tempfile
from multiprocessing import managers
from pathlib import Path
from unittest.mock import Mock

import pytest
import yaml

from pydidas.core import (
    BaseApp,
    ParameterCollection,
    get_generic_parameter,
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    _tempdir = Path(tempfile.mkdtemp())
    yield _tempdir
    shutil.rmtree(_tempdir)


@pytest.fixture
def base_app():
    """Create a basic BaseApp instance."""
    return BaseApp()


@pytest.fixture
def test_app_with_mocks():
    """Create a BaseApp with mocked multiprocessing methods."""
    app = BaseApp()
    app.multiprocessing_get_tasks = Mock(return_value=[1, 2, 3])
    app.multiprocessing_carryon = Mock(return_value=True)
    app.multiprocessing_func = Mock(return_value=(1,))
    app.multiprocessing_store_results = Mock()
    app.multiprocessing_pre_cycle = Mock()
    app.multiprocessing_post_run = Mock()
    app.stored = []
    app._config = {
        "item1": 1,
        "item2": slice(0, 5),
        "item3": "dummy",
        "item4": range(35),
        "item5": range(3, 42, 7),
        "carryon_counter": -1,
    }
    return app


@pytest.fixture
def params() -> ParameterCollection:
    _nx = get_generic_parameter("composite_nx")
    _nx.value = 10
    _ny = get_generic_parameter("composite_ny")
    _ny.value = 5
    _label = get_generic_parameter("label")
    _label.value = "start label"
    return ParameterCollection(_nx, _ny, _label)


def test_creation():
    """Test BaseApp creation."""
    app = BaseApp()
    assert isinstance(app, BaseApp)


def test_creation_with_args(params):
    app = BaseApp(params)
    for _key, _param in params.items():
        assert app.get_param_value(_key) == _param.value


def test_multiprocessing_pre_run(base_app):
    assert not base_app._config["run_prepared"]
    base_app.multiprocessing_pre_run()
    assert base_app._config["run_prepared"]


def test_multiprocessing_pre_cycle(base_app):
    result = base_app.multiprocessing_pre_cycle(0)
    assert result is None  # assert method runs without Exception


def test_multiprocessing_store_results__not_implemented(base_app):
    with pytest.raises(NotImplementedError):
        base_app.multiprocessing_store_results(0, 0)


def test_multiprocessing_get_tasks__not_implemented(base_app):
    with pytest.raises(NotImplementedError):
        base_app.multiprocessing_get_tasks()


def test_multiprocessing_func__not_implemented(base_app):
    with pytest.raises(NotImplementedError):
        base_app.multiprocessing_func(1)


def test_multiprocessing_carryon(base_app):
    result = base_app.multiprocessing_carryon()
    assert result is True


def test_get_config(base_app):
    config = base_app.get_config()
    assert config == {"run_prepared": False}


def test_get_config__verify_returns_copy(base_app):
    config = base_app.get_config()
    config["new_key"] = "modified"
    assert "new_key" not in base_app._config


def test_copy(base_app):
    _mgr = mp.Manager()
    _items = {
        "dummy": 42,
        "test_func": lambda x: x,
        "some_kwargs": {"a": 1, "b": 2},
    }
    base_app.mp_manager = {"lock": _mgr.Lock(), "shared_dict": _mgr.dict()}
    for _key, _val in _items.items():
        setattr(base_app, _key, _val)
    _copy = base_app.copy()
    assert base_app != _copy
    assert isinstance(_copy, BaseApp)
    for _key in _items.keys():
        assert hasattr(_copy, _key)
    assert base_app.mp_manager["lock"] == _copy.mp_manager["lock"]
    assert base_app.mp_manager["shared_dict"] == _copy.mp_manager["shared_dict"]


def test_copy__clone_mode(base_app):
    base_app.attributes_not_to_copy_to_app_clone = ["clone_att"]
    base_app.clone_att = 12
    base_app.non_clone_att = 42
    _copy = base_app.copy(clone_mode=True)
    assert base_app != _copy
    assert hasattr(_copy, "non_clone_att")
    assert not hasattr(_copy, "clone_att")
    assert _copy.clone_mode is True


def test_export_state(temp_dir, params):
    app = BaseApp(params)
    _nx = 42
    _ny = 17
    _label = "updated label"
    app.set_param_value("label", _label)
    app.set_param_value("composite_nx", _nx)
    app.set_param_value("composite_ny", _ny)
    app._config["new_key"] = True
    app._config["item1"] = "item1"
    app._config["item2"] = slice(0, 5)
    app._config["item4"] = range(35)
    _state = app.export_state()
    assert _state["params"]["label"] == _label
    assert _state["params"]["composite_nx"] == _nx
    assert _state["params"]["composite_ny"] == _ny
    assert _state["config"]["new_key"] is True
    assert _state["config"]["item1"] == "item1"
    assert _state["config"]["item2"] == "::slice::0::5::None"
    assert _state["config"]["item4"] == "::range::0::35::1"
    # Verify YAML serialization works
    with (temp_dir / "dummy.yaml").open("w") as _file:
        yaml.dump(_state, _file, Dumper=yaml.SafeDumper)
    assert (temp_dir / "dummy.yaml").exists()


def test_import_state(params):
    app = BaseApp(params)
    _state = {
        "params": {"composite_nx": 13, "composite_ny": 7, "label": "spam"},
        "config": {
            "item1": 55,
            "item2": "::slice::1::7::2",
            "item3": "new_dummy",
            "item4": "::range::0::10::1",
            "item5": "::None::",
        },
    }
    app.import_state(_state)
    for _key, _val in _state["params"].items():
        assert app.get_param_value(_key) == _val
    for _key in ["item1", "item3"]:
        assert app._config[_key] == _state["config"][_key]
    assert app._config["item2"] == slice(1, 7, 2)
    assert app._config["item4"] == range(10)
    assert app._config["item5"] is None


@pytest.mark.parametrize(
    "item_str,expected",
    [
        ("::range::0::10::1", range(0, 10, 1)),
        ("::range::5::20::2", range(5, 20, 2)),
        ("::slice::None::5::None", slice(None, 5, None)),
        ("::slice::2::None::3", slice(2, None, 3)),
        ("::None::", None),
    ],
)
def test_import_state__w_serialization_formats(item_str, expected):
    app = BaseApp()
    _state = {
        "params": {},
        "config": {"test_item": item_str},
    }
    app.import_state(_state)
    assert app._config["test_item"] == expected


def test_import_state__w_invalid_range():
    app = BaseApp()
    _state = {
        "params": {},
        "config": {"item": "::range::invalid::10::1"},
    }
    with pytest.raises(ValueError):
        app.import_state(_state)


def test_run(test_app_with_mocks):
    """Test BaseApp.run() executes tasks with mocked methods."""
    _tasks = [1, 2, 3]
    test_app_with_mocks.multiprocessing_get_tasks.return_value = _tasks
    test_app_with_mocks.multiprocessing_func.side_effect = [10, 20, 30]

    test_app_with_mocks.run()

    assert test_app_with_mocks._config["run_prepared"] is True
    test_app_with_mocks.multiprocessing_get_tasks.assert_called_once()
    assert test_app_with_mocks.multiprocessing_pre_cycle.call_count == len(_tasks)
    assert test_app_with_mocks.multiprocessing_func.call_count == len(_tasks)
    assert test_app_with_mocks.multiprocessing_store_results.call_count == len(_tasks)


def test_run__with_wait_condition(test_app_with_mocks):
    tasks = [1, 2]
    test_app_with_mocks.multiprocessing_get_tasks.return_value = tasks
    test_app_with_mocks.multiprocessing_carryon.side_effect = [False, True, False, True]

    test_app_with_mocks.run()

    # First task: carryon returns False then True (one wait cycle)
    # Second task: carryon returns True immediately
    assert test_app_with_mocks.multiprocessing_carryon.call_count == 4
    assert test_app_with_mocks.multiprocessing_func.call_count == 2


def test_parse_func():
    assert BaseApp.parse_func() == {}


def test_parse_func__w_implementation(params):
    def dummy_parser():
        return {"label": "Spam & Eggs"}

    original_parse_func = BaseApp.parse_func
    try:
        BaseApp.parse_func = staticmethod(dummy_parser)  # type: ignore
        app = BaseApp(params)
        assert app.get_param_value("label") == "Spam & Eggs"
    finally:
        BaseApp.parse_func = staticmethod(original_parse_func)  # type: ignore


def test_deleteLater__no_manager(base_app):
    _did_not_raise = base_app.deleteLater()
    assert _did_not_raise is None


def test_deleteLater__w_mp_manager():
    _mgr = mp.Manager()
    app = BaseApp()
    app._mp_manager_instance = _mgr  # type: ignore
    app._locals = {"lock": _mgr.Lock(), "shared_dict": _mgr.dict()}
    app.deleteLater()
    assert app._mp_manager_instance._state.value == managers.State.SHUTDOWN  # type: ignore


def test_must_send_signal_and_wait_for_response(base_app):
    result = base_app.must_send_signal_and_wait_for_response()
    assert result is None


def test_signal_processed_and_can_continue(base_app):
    result = base_app.signal_processed_and_can_continue()
    assert result is True


def test_get_latest_results(base_app):
    result = base_app.get_latest_results()
    assert result is None


def test_get_latest_results__w_data(base_app):
    base_app._config["latest_results"] = "some_data"
    result = base_app.get_latest_results()
    assert result == "some_data"


if __name__ == "__main__":
    pytest.main([__file__])

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


import io
import multiprocessing as mp
import queue
import sys
import threading
import time
from typing import Any, Callable

import numpy as np
import pytest

from pydidas.multiprocessing import processor_func


_N_TEST = 20


def _test_func(
    number: float, fixed_arg: float, fixed_arg2: float, kw_arg: float = 0
) -> float:
    return (number - fixed_arg) / fixed_arg2 + kw_arg


class _ProcThread(threading.Thread):
    """Simple Thread to test blocking input / output."""

    def __init__(
        self, func: Callable, mp_config: dict, *args: Any, **kwargs: Any
    ) -> None:
        super().__init__()
        self._kwargs = kwargs
        self._args = args
        self.func = func
        self._mp_config = mp_config

    def run(self) -> None:
        processor_func(
            self.func,
            self._mp_config,
            *self._args,
            **self._kwargs,
        )


class _ClassForMethodTest:
    def __init__(self) -> None:
        self.offset = 5

    def test_func(
        self, number: float, fixed_arg: float, fixed_arg2: float, kw_arg: float = 0
    ) -> float:
        return (number - fixed_arg) / fixed_arg2 + kw_arg + self.offset


@pytest.fixture
def mp_config() -> dict[str, Any]:  # type: ignore[return-value]
    """Create multiprocessing mp_config with queues for testing."""
    _mp_config = {
        "queue_input": mp.Queue(),
        "queue_output": mp.Queue(),
        "queue_stop": mp.Queue(),
        "queue_shutting_down": mp.Queue(),
    }
    yield _mp_config  # type: ignore[misc]
    for _queue in _mp_config.values():
        _queue.close()


def put_ints_in_queue(mp_config: dict[str, mp.Queue]) -> None:
    """Put integers in the input queue."""
    for i in range(_N_TEST):
        mp_config["queue_input"].put(i)
    mp_config["queue_input"].put(None)


def get_results(mp_config: dict[str, mp.Queue]) -> tuple[np.ndarray, np.ndarray]:
    """Get results from the output queue."""
    _return = np.array([mp_config["queue_output"].get() for _ in range(_N_TEST)])
    _res = _return[:, 1]
    _input = _return[:, 0]
    return _input, _res


def test_run__plain(mp_config) -> None:
    """Test basic processor_func with identity function."""
    put_ints_in_queue(mp_config, _N_TEST)
    processor_func(lambda x: x, mp_config)
    _input, _output = get_results(mp_config, _N_TEST)
    assert (_input == _output).all()  # type: ignore[union-attr]


def test_run__with_empty_queue(mp_config) -> None:
    """Test processor_func with empty queue handling."""
    _thread = _ProcThread(lambda x: x, mp_config)
    _thread.start()
    time.sleep(0.08)
    mp_config["queue_input"].put(None)
    time.sleep(0.08)
    assert mp_config["queue_output"].get(timeout=1) == [None, None]


def test_run__with_stop_signal(mp_config) -> None:
    """Test processor_func with stop signal."""
    _thread = _ProcThread(lambda x: x, mp_config)
    mp_config["queue_stop"].put(1)
    _thread.start()
    with pytest.raises(queue.Empty):
        mp_config["queue_output"].get(timeout=0.1)
    assert mp_config["queue_shutting_down"].get() == 1


def test_run__with_args(mp_config) -> None:
    """Test processor_func with additional arguments."""
    _args = (0, 1)
    put_ints_in_queue(mp_config, _N_TEST)
    processor_func(_test_func, mp_config, *_args)
    _input, _output = get_results(mp_config, _N_TEST)
    _direct_out = _test_func(_input, *_args)  # type: ignore[arg-type]
    assert (_output == _direct_out).all()  # type: ignore[union-attr]
    assert mp_config["queue_output"].get(timeout=1) == [None, None]


def test_run__exception_in_func(mp_config) -> None:
    """Test processor_func with exception in function."""
    put_ints_in_queue(mp_config, _N_TEST)
    old_stdout = sys.stdout
    sys.stdout = my_stdout = io.StringIO()
    processor_func(_test_func, mp_config)
    sys.stdout = old_stdout
    # Assert that the processor_func returned directly and did not wait
    # for any queue timeouts.
    assert len(my_stdout.getvalue()) > 0
    assert mp_config["queue_shutting_down"].get() == 1


def test_run__with_kwargs(mp_config) -> None:
    """Test processor_func with keyword arguments."""
    _args = (0, 1)
    _kwargs = dict(kw_arg=12)
    put_ints_in_queue(mp_config, _N_TEST)
    processor_func(
        _test_func,
        mp_config,
        *_args,
        **_kwargs,
    )
    _input, _output = get_results(mp_config, _N_TEST)
    _direct_out = _test_func(_input, *_args, **_kwargs)  # type: ignore[arg-type]
    assert (_output == _direct_out).all()  # type: ignore[union-attr]
    assert mp_config["queue_output"].get(timeout=1) == [None, None]


def test_run__with_class_method(mp_config) -> None:
    """Test processor_func with class method."""
    _args = (0, 1)
    put_ints_in_queue(mp_config, _N_TEST)
    app = _ClassForMethodTest()
    processor_func(app.test_func, mp_config, *_args)
    _input, _output = get_results(mp_config, _N_TEST)
    _direct_out = app.test_func(_input, *_args)  # type: ignore[arg-type]
    assert (_output == _direct_out).all()  # type: ignore[union-attr]
    assert mp_config["queue_output"].get(timeout=1) == [None, None]


if __name__ == "__main__":
    pytest.main([__file__])

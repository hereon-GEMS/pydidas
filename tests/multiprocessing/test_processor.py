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
import unittest
from typing import Any, Callable

import numpy as np

from pydidas.multiprocessing import processor


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
        processor(
            self.func,
            self._mp_config,
            *self._args,
            **self._kwargs,
        )


class AppWithFunc:
    def __init__(self) -> None:
        self.offset = 5

    def test_func(
        self, number: float, fixed_arg: float, fixed_arg2: float, kw_arg: float = 0
    ) -> float:
        return (number - fixed_arg) / fixed_arg2 + kw_arg + self.offset


class Test_processor(unittest.TestCase):
    def setUp(self) -> None:
        self._queues = {
            "queue_input": mp.Queue(),
            "queue_output": mp.Queue(),
            "queue_stop": mp.Queue(),
            "queue_shutting_down": mp.Queue(),
        }
        self.n_test = 20

    def tearDown(self) -> None:
        for _queue in self._queues.values():
            _queue.close()

    def put_ints_in_queue(self) -> None:
        for i in range(self.n_test):
            self._queues["queue_input"].put(i)
        self._queues["queue_input"].put(None)

    def get_results(self) -> tuple[np.ndarray, np.ndarray]:
        _return = np.array(
            [self._queues["queue_output"].get() for i in range(self.n_test)]
        )
        _res = _return[:, 1]
        _input = _return[:, 0]
        return _input, _res

    def test_run__plain(self) -> None:
        self.put_ints_in_queue()
        processor(lambda x: x, self._queues)
        _input, _output = self.get_results()
        self.assertTrue((_input == _output).all())  # type: ignore[union-attr]

    def test_run__with_empty_queue(self) -> None:
        _thread = _ProcThread(lambda x: x, self._queues)
        _thread.start()
        time.sleep(0.08)
        self._queues["queue_input"].put(None)
        time.sleep(0.08)
        self.assertEqual(self._queues["queue_output"].get(timeout=1), [None, None])

    def test_run__with_stop_signal(self) -> None:
        _thread = _ProcThread(lambda x: x, self._queues)
        self._queues["queue_stop"].put(1)
        _thread.start()
        with self.assertRaises(queue.Empty):
            self._queues["queue_output"].get(timeout=0.1)
        self.assertEqual(self._queues["queue_shutting_down"].get(), 1)

    def test_run__with_args(self) -> None:
        _args = (0, 1)
        self.put_ints_in_queue()
        processor(_test_func, self._queues, *_args)
        _input, _output = self.get_results()
        _direct_out = _test_func(_input, *_args)
        self.assertTrue((_output == _direct_out).all())  # type: ignore[union-attr]
        self.assertEqual(self._queues["queue_output"].get(timeout=1), [None, None])

    def test_run__exception_in_func(self) -> None:
        self.put_ints_in_queue()
        old_stdout = sys.stdout
        sys.stdout = mystdout = io.StringIO()
        processor(_test_func, self._queues)
        sys.stdout = old_stdout
        # Assert that the processor returned directly and did not wait for any
        # queue timeouts.
        self.assertTrue(len(mystdout.getvalue()) > 0)
        self.assertEqual(self._queues["queue_shutting_down"].get(), 1)

    def test_run__with_kwargs(self) -> None:
        _args = (0, 1)
        _kwargs = dict(kw_arg=12)
        self.put_ints_in_queue()
        processor(
            _test_func,
            self._queues,
            *_args,
            **_kwargs,
        )
        _input, _output = self.get_results()
        _direct_out = _test_func(_input, *_args, **_kwargs)
        self.assertTrue((_output == _direct_out).all())  # type: ignore[union-attr]
        self.assertEqual(self._queues["queue_output"].get(timeout=1), [None, None])

    def test_run__with_class_method(self) -> None:
        _args = (0, 1)
        self.put_ints_in_queue()
        app = AppWithFunc()
        processor(app.test_func, self._queues, *_args)
        _input, _output = self.get_results()
        _direct_out = app.test_func(_input, *_args)
        self.assertTrue((_output == _direct_out).all())  # type: ignore[union-attr]
        self.assertEqual(self._queues["queue_output"].get(timeout=1), [None, None])


if __name__ == "__main__":
    unittest.main()

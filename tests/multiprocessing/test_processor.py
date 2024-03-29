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
import multiprocessing as mp
import queue
import sys
import threading
import time
import unittest

import numpy as np
from qtpy import QtWidgets

from pydidas.multiprocessing import processor


def test_func(number, fixed_arg, fixed_arg2, kw_arg=0):
    return (number - fixed_arg) / fixed_arg2 + kw_arg


class _ProcThread(threading.Thread):
    """Simple Thread to test blocking input / output."""

    def __init__(self, input_queue, output_queue, stop_queue, aborted_queue, func):
        super().__init__()
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.stop_queue = stop_queue
        self.aborted_queue = aborted_queue
        self.func = func

    def run(self):
        processor(
            self.input_queue,
            self.output_queue,
            self.stop_queue,
            self.aborted_queue,
            self.func,
        )


class AppWithFunc:
    def __init__(self):
        self.offset = 5

    def test_func(self, number, fixed_arg, fixed_arg2, kw_arg=0):
        return (number - fixed_arg) / fixed_arg2 + kw_arg + self.offset


class Test_processor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._qtapp = QtWidgets.QApplication.instance()
        if cls._qtapp is None:
            cls._qtapp = QtWidgets.QApplication([])

    @classmethod
    def tearDownClass(cls):
        cls._qtapp.deleteLater()

    def setUp(self):
        self.input_queue = mp.Queue()
        self.output_queue = mp.Queue()
        self.stop_queue = mp.Queue()
        self.aborted_queue = mp.Queue()
        self.n_test = 20

    def tearDown(self):
        self.input_queue.close()
        self.output_queue.close()
        self.stop_queue.close()
        self.aborted_queue.close()

    def put_ints_in_queue(self):
        for i in range(self.n_test):
            self.input_queue.put(i)
        self.input_queue.put(None)

    def get_results(self):
        _return = np.array([self.output_queue.get() for i in range(self.n_test)])
        _res = _return[:, 1]
        _input = _return[:, 0]
        return _input, _res

    def test_run__plain(self):
        self.put_ints_in_queue()
        processor(
            self.input_queue,
            self.output_queue,
            self.stop_queue,
            self.aborted_queue,
            lambda x: x,
        )
        _input, _output = self.get_results()
        self.assertTrue((_input == _output).all())

    def test_run__with_empty_queue(self):
        _thread = _ProcThread(
            self.input_queue,
            self.output_queue,
            self.stop_queue,
            self.aborted_queue,
            lambda x: x,
        )
        _thread.start()
        time.sleep(0.08)
        self.input_queue.put(None)
        time.sleep(0.08)
        self.assertEqual(self.output_queue.get(timeout=1), [None, None])

    def test_run__with_stop_signal(self):
        _thread = _ProcThread(
            self.input_queue,
            self.output_queue,
            self.stop_queue,
            self.aborted_queue,
            lambda x: x,
        )
        self.stop_queue.put(1)
        _thread.start()
        with self.assertRaises(queue.Empty):
            self.output_queue.get(timeout=0.1)
        self.assertEqual(self.aborted_queue.get(), 1)

    def test_run__with_args(self):
        _args = (0, 1)
        self.put_ints_in_queue()
        processor(
            self.input_queue,
            self.output_queue,
            self.stop_queue,
            self.aborted_queue,
            test_func,
            *_args,
        )
        _input, _output = self.get_results()
        _direct_out = test_func(_input, *_args)
        self.assertTrue((_output == _direct_out).all())
        self.assertEqual(self.output_queue.get(timeout=1), [None, None])

    def test_run__exception_in_func(self):
        self.put_ints_in_queue()
        old_stdout = sys.stdout
        sys.stdout = mystdout = io.StringIO()
        processor(
            self.input_queue,
            self.output_queue,
            self.stop_queue,
            self.aborted_queue,
            test_func,
        )
        sys.stdout = old_stdout
        # Assert that the processor returned directly and did not wait for any
        # queue timeouts.
        self.assertTrue(len(mystdout.getvalue()) > 0)
        self.assertEqual(self.aborted_queue.get(), 1)

    def test_run__with_kwargs(self):
        _args = (0, 1)
        _kwargs = dict(kw_arg=12)
        self.put_ints_in_queue()
        processor(
            self.input_queue,
            self.output_queue,
            self.stop_queue,
            self.aborted_queue,
            test_func,
            *_args,
            **_kwargs,
        )
        _input, _output = self.get_results()
        _direct_out = test_func(_input, *_args, **_kwargs)
        self.assertTrue((_output == _direct_out).all())
        self.assertEqual(self.output_queue.get(timeout=1), [None, None])

    def test_run__with_class_method(self):
        _args = (0, 1)
        self.put_ints_in_queue()
        app = AppWithFunc()
        processor(
            self.input_queue,
            self.output_queue,
            self.stop_queue,
            self.aborted_queue,
            app.test_func,
            *_args,
        )
        _input, _output = self.get_results()
        _direct_out = app.test_func(_input, *_args)
        self.assertTrue((_output == _direct_out).all())
        self.assertEqual(self.output_queue.get(timeout=1), [None, None])


if __name__ == "__main__":
    unittest.main()

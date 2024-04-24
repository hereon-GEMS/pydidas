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


import multiprocessing as mp
import sys
import time
import unittest

import numpy as np
from qtpy import QtCore, QtTest, QtWidgets

from pydidas import IS_QT6
from pydidas.multiprocessing import WorkerController


def local_test_func(index, *args, **kwargs):
    index = (
        index
        + np.sum(np.fromiter([arg for arg in args], float))
        + np.sum(np.fromiter([kwargs[key] for key in kwargs], float))
    )
    return 3 * index


def get_spy_values(spy, index=0):
    return [spy[_index][index] for _index in range(len(spy))]


class TestWorkerController(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._app = QtWidgets.QApplication.instance()
        if cls._app is None:
            cls._app = QtWidgets.QApplication(sys.argv)

    @classmethod
    def tearDownClass(cls):
        cls._app.deleteLater()

    def wait_for_finish_signal(self, wc, timeout=8):
        t0 = time.time()
        _spy = QtTest.QSignalSpy(wc.finished)
        t0 = time.time()
        while len(_spy) == 0 and time.time() - t0 < timeout:
            time.sleep(0.05)
        if time.time() - t0 >= timeout:
            raise TimeoutError

    def wait_for_finish_signal_qt6(self, wc, timeout=8):
        t0 = time.time()
        _spy = QtTest.QSignalSpy(wc.finished)
        t0 = time.time()
        while _spy.count() == 0 and time.time() - t0 < timeout:
            time.sleep(0.05)
        if time.time() - t0 >= timeout:
            raise TimeoutError

    def test_main_object(self):
        # this will only test the setup method
        ...

    def test_test_func_i(self):
        index = 0
        args = (0, 0, 0)
        kwargs = dict(a=0, b=0)
        self.assertEqual(local_test_func(index, *args, **kwargs), 0)

    def test_creation(self):
        wc = WorkerController()
        self.assertIsInstance(wc, QtCore.QThread)

    def test_n_workers__get(self):
        num_workers = 5
        wc = WorkerController(num_workers)
        self.assertEqual(wc.n_workers, num_workers)

    def test_n_workers__set(self):
        wc = WorkerController()
        num_workers = 5
        wc.n_workers = num_workers
        self.assertEqual(wc.n_workers, num_workers)

    def test_n_workers__set_wrong(self):
        wc = WorkerController()
        num_workers = 5.5
        with self.assertRaises(ValueError):
            wc.n_workers = num_workers

    def test_progress__no_target(self):
        wc = WorkerController()
        self.assertEqual(wc.progress, -1)

    def test_progress__no_computations(self):
        wc = WorkerController()
        wc._progress_target = 12
        self.assertEqual(wc.progress, 0)

    def test_progress__in_run(self):
        _target = 12
        _current = 7
        wc = WorkerController()
        wc._progress_target = _target
        wc._progress_done = _current
        self.assertAlmostEqual(wc.progress, _current / _target)

    def test_stop(self):
        wc = WorkerController()
        wc.stop()
        self.assertEqual(wc.flags["thread_alive"], False)

    def test_suspend(self):
        wc = WorkerController()
        wc.suspend()
        self.assertEqual(wc.flags["running"], False)

    def test_run_qt5(self):
        if IS_QT6:
            return
        _tasks = [1, 2, 3, 4]
        wc = WorkerController(n_workers=2)
        wc.change_function(local_test_func, *(0, 0))
        wc.add_tasks(_tasks)
        wc.finalize_tasks()
        _spy = QtTest.QSignalSpy(wc.finished)
        wc.start()
        self.wait_for_finish_signal(wc)
        self.assertEqual(len(_spy), 1)

    def test_run_qt6(self):
        if not IS_QT6:
            return
        _tasks = [1, 2, 3, 4]
        wc = WorkerController(n_workers=2)
        wc.change_function(local_test_func, *(0, 0))
        wc.add_tasks(_tasks)
        wc.finalize_tasks()
        _spy = QtTest.QSignalSpy(wc.finished)
        wc.start()
        self.wait_for_finish_signal_qt6(wc)
        self.assertEqual(_spy.count(), 1)

    def test_restart(self):
        wc = WorkerController()
        wc.suspend()
        wc.restart()
        self.assertEqual(wc.flags["running"], True)

    def test_change_function(self):
        _args = (0, 0)
        wc = WorkerController()
        wc.change_function(local_test_func, *_args)
        self.assertEqual(wc._processor["args"][4], local_test_func)
        self.assertEqual(wc._processor["args"][5:], _args)

    def testcycle_pre_run(self):
        wc = WorkerController()
        wc.cycle_pre_run()
        wc.cycle_post_run()
        self.assertEqual(wc._progress_done, 0)

    def testcycle_post_run__no_stop_signal(self):
        wc = WorkerController()
        wc.flags["stop_after_run"] = False
        wc.flags["thread_alive"] = True
        wc.cycle_post_run(timeout=0.01)
        self.assertTrue(wc.flags["thread_alive"])

    def testcycle_post_run__stop_signal(self):
        wc = WorkerController()
        wc.flags["stop_after_run"] = True
        wc.flags["thread_alive"] = True
        wc.cycle_post_run(timeout=0.01)
        self.assertFalse(wc.flags["thread_alive"])

    def test_create_and_start_workers(self):
        wc = WorkerController()
        wc._create_and_start_workers()
        for worker in wc._workers:
            self.assertIsInstance(worker, mp.Process)
        wc.cycle_post_run()

    def test_add_task(self):
        wc = WorkerController()
        wc.suspend()
        wc.add_task(1)
        self.assertEqual(wc._to_process, [1])

    def test_wait_for_processes_to_finish(self):
        _timeout = 0.2
        wc = WorkerController()
        wc.flags["active"] = True
        t0 = time.time()
        wc._wait_for_processes_to_finish(timeout=_timeout)
        self.assertTrue(time.time() - t0 >= _timeout)

    def test_add_tasks(self):
        _tasks = [1, 2, 3]
        wc = WorkerController()
        wc.suspend()
        wc.add_tasks(_tasks)
        self.assertEqual(wc._to_process, _tasks)

    def test_add_tasks__previous_tasks(self):
        _tasks = [1, 2, 3]
        wc = WorkerController()
        wc.suspend()
        wc.add_task(0)
        wc.add_tasks(_tasks)
        self.assertEqual(wc._to_process, [0] + _tasks)

    def test_put_next_task_in_queue(self):
        wc = WorkerController()
        wc._to_process = [1, 2, 3]
        wc._put_next_task_in_queue()
        self.assertEqual(wc._queues["send"].qsize(), 1)

    def test_get_and_emit_all_queue_items(self):
        _res1 = 3
        _res2 = [1, 1]
        wc = WorkerController()
        wc._queues["recv"].put([0, _res1])
        wc._queues["recv"].put([0, _res2])
        wc._progress_target = 2
        _spy = QtTest.QSignalSpy(wc.sig_results)
        time.sleep(0.005)
        wc._get_and_emit_all_queue_items()
        if IS_QT6:
            self.assertEqual(_spy.count(), 2)
            self.assertEqual(_spy.at(0)[1], _res1)
            self.assertEqual(_spy.at(1)[1], _res2)
        else:
            self.assertEqual(len(_spy), 2)
            self.assertEqual(_spy[0][1], _res1)
            self.assertEqual(_spy[1][1], _res2)

    def test_check_if_workers_done__no_signal(self):
        wc = WorkerController(n_workers=2)
        wc.flags["running"] = True
        wc._workers = [1, 2, 3, 4]
        wc._check_if_workers_finished()
        self.assertEqual(wc._workers_done, 0)
        self.assertTrue(wc.flags["running"])

    def test_check_if_workers_done__get_numbers(self):
        wc = WorkerController(n_workers=2)
        wc._workers = [1, 2, 3, 4]
        _nfinished = 3
        for i in range(_nfinished):
            wc._queues["aborted"].put(1)
        time.sleep(0.005)
        wc._check_if_workers_finished()
        self.assertEqual(wc._workers_done, _nfinished)

    def test_wait_for_worker_finished_signals__not_running(self):
        wc = WorkerController(n_workers=2)
        wc._wait_for_worker_finished_signals(0.1)
        # assert: does not raise TimeoutError

    def test_wait_for_worker_finished_signals__running_not_done(self):
        wc = WorkerController(n_workers=2)
        wc.flags["running"] = True
        wc._workers = [1, 2, 3, 4]
        with self.assertRaises(TimeoutError):
            wc._wait_for_worker_finished_signals(0.2)

    def test_wait_for_worker_finished_signals__running_done(self):
        wc = WorkerController(n_workers=2)
        wc.flags["running"] = True
        wc._workers = [1, 2, 3, 4]
        for i in range(len(wc._workers)):
            wc._queues["aborted"].put(1)
        # assert: does not raise TimeoutError
        wc._wait_for_worker_finished_signals(0.2)


if __name__ == "__main__":
    unittest.main()

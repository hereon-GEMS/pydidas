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

    def tearDown(self):
        if hasattr(self, "_wc") and isinstance(self._wc, WorkerController):
            self._wc.exit()

    def wait_for_finish_signal(self, wc, timeout=8):
        t0 = time.time()
        _spy = QtTest.QSignalSpy(self._wc.finished)
        t0 = time.time()
        while len(_spy) == 0 and time.time() - t0 < timeout:
            time.sleep(0.05)
        if time.time() - t0 >= timeout:
            raise TimeoutError

    def wait_for_finish_signal_qt6(self, wc, timeout=8):
        t0 = time.time()
        _spy = QtTest.QSignalSpy(self._wc.finished)
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
        self._wc = WorkerController()
        self.assertIsInstance(self._wc, QtCore.QThread)

    def test_n_workers__get(self):
        num_workers = 5
        self._wc = WorkerController(num_workers)
        self.assertEqual(self._wc.n_workers, num_workers)

    def test_n_workers__set(self):
        self._wc = WorkerController()
        num_workers = 5
        self._wc.n_workers = num_workers
        self.assertEqual(self._wc.n_workers, num_workers)

    def test_n_workers__set_wrong(self):
        self._wc = WorkerController()
        num_workers = 5.5
        with self.assertRaises(ValueError):
            self._wc.n_workers = num_workers

    def test_progress__no_target(self):
        self._wc = WorkerController()
        self.assertEqual(self._wc.progress, -1)

    def test_progress__no_computations(self):
        self._wc = WorkerController()
        self._wc._progress_target = 12
        self.assertEqual(self._wc.progress, 0)

    def test_progress__in_run(self):
        _target = 12
        _current = 7
        self._wc = WorkerController()
        self._wc._progress_target = _target
        self._wc._progress_done = _current
        self.assertAlmostEqual(self._wc.progress, _current / _target)

    def test_stop(self):
        self._wc = WorkerController()
        self._wc.stop()
        self.assertEqual(self._wc.flags["thread_alive"], False)

    def test_suspend(self):
        self._wc = WorkerController()
        self._wc.suspend()
        self.assertEqual(self._wc.flags["running"], False)

    def test_run_qt5(self):
        if IS_QT6:
            return
        _tasks = [1, 2, 3, 4]
        self._wc = WorkerController(n_workers=2)
        self._wc.change_function(local_test_func, *(0, 0))
        self._wc.add_tasks(_tasks)
        self._wc.finalize_tasks()
        _spy = QtTest.QSignalSpy(self._wc.finished)
        self._wc.start()
        self.wait_for_finish_signal(self._wc)
        self.assertEqual(len(_spy), 1)

    def test_run_qt6(self):
        if not IS_QT6:
            return
        _tasks = [1, 2, 3, 4]
        self._wc = WorkerController(n_workers=2)
        self._wc.change_function(local_test_func, *(0, 0))
        self._wc.add_tasks(_tasks)
        self._wc.finalize_tasks()
        _spy = QtTest.QSignalSpy(self._wc.finished)
        self._wc.start()
        self.wait_for_finish_signal_qt6(self._wc)
        self.assertEqual(_spy.count(), 1)

    def test_restart(self):
        self._wc = WorkerController()
        self._wc.suspend()
        self._wc.restart()
        self.assertEqual(self._wc.flags["running"], True)

    def test_change_function(self):
        _args = (0, 0)
        self._wc = WorkerController()
        self._wc.change_function(local_test_func, *_args)
        self.assertEqual(self._wc._processor["args"][0], local_test_func)
        self.assertEqual(self._wc._processor["args"][2:], _args)

    def testcycle_pre_run(self):
        self._wc = WorkerController()
        self._wc.cycle_pre_run()
        self._wc.cycle_post_run()
        self.assertEqual(self._wc._progress_done, 0)

    def testcycle_post_run__no_stop_signal(self):
        self._wc = WorkerController()
        self._wc.flags["stop_after_run"] = False
        self._wc.flags["thread_alive"] = True
        self._wc.cycle_post_run(timeout=0.01)
        self.assertTrue(self._wc.flags["thread_alive"])

    def testcycle_post_run__stop_signal(self):
        self._wc = WorkerController()
        self._wc.flags["stop_after_run"] = True
        self._wc.flags["thread_alive"] = True
        self._wc.cycle_post_run(timeout=0.01)
        self.assertFalse(self._wc.flags["thread_alive"])

    def test_create_and_start_workers(self):
        self._wc = WorkerController()
        self._wc._create_and_start_workers()
        for worker in self._wc._workers:
            self.assertIsInstance(worker, mp.Process)
        self._wc.cycle_post_run()

    def test_add_task(self):
        self._wc = WorkerController()
        self._wc.suspend()
        self._wc.add_task(1)
        self.assertEqual(self._wc._to_process, [1])

    def test_wait_for_processes_to_finish(self):
        _timeout = 0.2
        self._wc = WorkerController()
        self._wc.flags["active"] = True
        t0 = time.time()
        self._wc._wait_for_processes_to_finish(timeout=_timeout)
        self.assertTrue(time.time() - t0 >= _timeout)

    def test_add_tasks(self):
        _tasks = [1, 2, 3]
        self._wc = WorkerController()
        self._wc.suspend()
        self._wc.add_tasks(_tasks)
        self.assertEqual(self._wc._to_process, _tasks)

    def test_add_tasks__previous_tasks(self):
        _tasks = [1, 2, 3]
        self._wc = WorkerController()
        self._wc.suspend()
        self._wc.add_task(0)
        self._wc.add_tasks(_tasks)
        self.assertEqual(self._wc._to_process, [0] + _tasks)

    def test_put_next_task_in_queue(self):
        self._wc = WorkerController()
        self._wc._to_process = [1, 2, 3]
        self._wc._put_next_task_in_queue()
        self.assertEqual(self._wc._queues["queue_input"].qsize(), 1)

    def test_get_and_emit_all_queue_items(self):
        _res1 = 3
        _res2 = [1, 1]
        self._wc = WorkerController()
        self._wc._queues["queue_output"].put([0, _res1])
        self._wc._queues["queue_output"].put([0, _res2])
        self._wc._queues["queue_signal"].put("::test::")
        self._wc._progress_target = 2
        _spy = QtTest.QSignalSpy(self._wc.sig_results)
        _spy_signal = QtTest.QSignalSpy(self._wc.sig_message_from_worker)
        time.sleep(0.005)
        self._wc._get_and_emit_all_queue_items()
        if IS_QT6:
            self.assertEqual(_spy.count(), 2)
            self.assertEqual(_spy.at(0)[1], _res1)
            self.assertEqual(_spy.at(1)[1], _res2)
            self.assertEqual(_spy_signal.count(), 1)
            self.assertEqual(_spy_signal.at(0)[0], "::test::")
        else:
            self.assertEqual(len(_spy), 2)
            self.assertEqual(_spy[0][1], _res1)
            self.assertEqual(_spy[1][1], _res2)
            self.assertEqual(len(_spy_signal), 1)
            self.assertEqual(_spy_signal[0][0], "::test::")

    def test_check_if_workers_done__no_signal(self):
        self._wc = WorkerController(n_workers=2)
        self._wc.flags["running"] = True
        self._wc._workers = [1, 2, 3, 4]
        self._wc._check_if_workers_finished()
        self.assertEqual(self._wc._workers_done, 0)
        self.assertTrue(self._wc.flags["running"])

    def test_check_if_workers_done__get_numbers(self):
        self._wc = WorkerController(n_workers=2)
        self._wc._workers = [1, 2, 3, 4]
        _nfinished = 3
        for i in range(_nfinished):
            self._wc._queues["queue_aborted"].put(1)
        time.sleep(0.005)
        self._wc._check_if_workers_finished()
        self.assertEqual(self._wc._workers_done, _nfinished)

    def test_wait_for_worker_finished_signals__not_running(self):
        self._wc = WorkerController(n_workers=2)
        self._wc._wait_for_worker_finished_signals(0.1)
        # assert: does not raise TimeoutError

    def test_wait_for_worker_finished_signals__running_not_done(self):
        self._wc = WorkerController(n_workers=2)
        self._wc.flags["running"] = True
        self._wc._workers = [1, 2, 3, 4]
        with self.assertRaises(TimeoutError):
            self._wc._wait_for_worker_finished_signals(0.2)

    def test_wait_for_worker_finished_signals__running_done(self):
        self._wc = WorkerController(n_workers=2)
        self._wc.flags["running"] = True
        self._wc._workers = [1, 2, 3, 4]
        for i in range(len(self._wc._workers)):
            self._wc._queues["queue_aborted"].put(1)
        # assert: does not raise TimeoutError
        self._wc._wait_for_worker_finished_signals(0.2)


if __name__ == "__main__":
    unittest.main()

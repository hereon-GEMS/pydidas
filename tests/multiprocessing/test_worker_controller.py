# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
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
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import unittest
import time
import sys
import multiprocessing as mp

import numpy as np
from qtpy import QtCore, QtWidgets, QtTest

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
        self.assertEqual(wc._flag_thread_alive, False)

    def test_suspend(self):
        wc = WorkerController()
        wc.suspend()
        self.assertEqual(wc._flag_running, False)

    def test_run(self):
        _tasks = [1, 2, 3, 4]
        wc = WorkerController(n_workers=4)
        wc.change_function(local_test_func, *(0, 0))
        wc.add_tasks(_tasks)
        wc.finalize_tasks()
        _spy = QtTest.QSignalSpy(wc.finished)
        wc.start()
        # wc.stop()
        self.wait_for_finish_signal(wc)
        # time.sleep(0.3)
        self.assertEqual(len(_spy), 1)

    def test_restart(self):
        wc = WorkerController()
        wc.suspend()
        wc.restart()
        self.assertEqual(wc._flag_running, True)

    def test_change_function(self):
        _args = (0, 0)
        wc = WorkerController()
        wc.change_function(local_test_func, *_args)
        self.assertEqual(wc._processor["args"][4], local_test_func)
        self.assertEqual(wc._processor["args"][5:], _args)

    def test_cycle_pre_run(self):
        wc = WorkerController()
        wc._cycle_pre_run()
        wc._cycle_post_run()
        self.assertEqual(wc._progress_done, 0)

    def test_cycle_post_run__no_stop_signal(self):
        wc = WorkerController()
        wc._flag_stop_after_run = False
        wc._flag_thread_alive = True
        wc._cycle_post_run(timeout=0.01)
        self.assertTrue(wc._flag_thread_alive)

    def test_cycle_post_run__stop_signal(self):
        wc = WorkerController()
        wc._flag_stop_after_run = True
        wc._flag_thread_alive = True
        wc._cycle_post_run(timeout=0.01)
        self.assertFalse(wc._flag_thread_alive)

    def test_create_and_start_workers(self):
        wc = WorkerController()
        wc._create_and_start_workers()
        for worker in wc._workers:
            self.assertIsInstance(worker, mp.Process)
        wc._cycle_post_run()

    def test_add_task(self):
        wc = WorkerController()
        wc.suspend()
        wc.add_task(1)
        self.assertEqual(wc._to_process, [1])

    def test_wait_for_processes_to_finish(self):
        _timeout = 0.2
        wc = WorkerController()
        wc._flag_active = True
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
        self.assertEqual(len(_spy), 2)
        self.assertEqual(_spy[0][1], _res1)
        self.assertEqual(_spy[1][1], _res2)

    # def test_results_signal(self):
    #     _tasks = [1, 2, 3, 4]
    #     _target = {local_test_func(item, 0, 0) for item in _tasks}
    #     wc = WorkerController(n_workers=4)
    #     wc.change_function(local_test_func, *(0, 0))
    #     result_spy = QtTest.QSignalSpy(wc.sig_results)
    #     progress_spy = QtTest.QSignalSpy(wc.sig_progress)
    #     wc.add_tasks(_tasks)
    #     wc.finalize_tasks()
    #     wc.start()
    #     self.wait_for_finish_signal(wc)
    #     time.sleep(0.1)
    #     _results = get_spy_values(result_spy, index=1)
    #     _progress = get_spy_values(progress_spy)
    #     _exp_progress = [index / len(_tasks) for index in range(1, len(_tasks) + 1)]
    #     self.assertEqual(set(_results), _target)
    #     self.assertEqual(_progress, _exp_progress)

    def test_check_if_workers_done__no_signal(self):
        wc = WorkerController(n_workers=4)
        wc._flag_running = True
        wc._workers = [1, 2, 3, 4]
        wc._check_if_workers_done()
        self.assertEqual(wc._workers_done, 0)
        self.assertTrue(wc._flag_running)

    def test_check_if_workers_done__get_numbers(self):
        wc = WorkerController(n_workers=4)
        wc._workers = [1, 2, 3, 4]
        _nfinished = 3
        for i in range(_nfinished):
            wc._queues["finished"].put(1)
        time.sleep(0.005)
        wc._check_if_workers_done()
        self.assertEqual(wc._workers_done, _nfinished)

    def test_wait_for_worker_finished_signals__not_running(self):
        wc = WorkerController(n_workers=4)
        wc._wait_for_worker_finished_signals(0.1)
        # assert: does not raise TimeoutError

    def test_wait_for_worker_finished_signals__running_not_done(self):
        wc = WorkerController(n_workers=4)
        wc._flag_running = True
        wc._workers = [1, 2, 3, 4]
        with self.assertRaises(TimeoutError):
            wc._wait_for_worker_finished_signals(0.2)

    def test_wait_for_worker_finished_signals__running_done(self):
        wc = WorkerController(n_workers=4)
        wc._flag_running = True
        wc._workers = [1, 2, 3, 4]
        for i in range(len(wc._workers)):
            wc._queues["finished"].put(1)
        # assert: does not raise TimeoutError
        wc._wait_for_worker_finished_signals(0.2)


if __name__ == "__main__":
    unittest.main()

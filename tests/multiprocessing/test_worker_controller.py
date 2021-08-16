# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""Unit tests for pydidas modules."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import threading
import unittest
import time
import sys
import multiprocessing as mp

import numpy as np

from PyQt5 import QtCore, QtWidgets, QtTest
from pydidas.multiprocessing import WorkerController, processor


def local_test_func(index, *args, **kwargs):
    index = (index
              + np.sum(np.fromiter([arg for arg in args], float))
              + np.sum(np.fromiter([kwargs[key] for key in kwargs], float))
              )
    return 3 * index


def get_spy_values(spy, index=0):
    return [spy[_index][index] for _index in range(len(spy))]


# class _ProcThread(threading.Thread):
#     """ Simple Thread to test blocking input / output. """
#     def __init__(self, input_queue, output_queue, func, *args, **kwargs):
#         super().__init__()
#         self.input_queue = input_queue
#         self.output_queue = output_queue
#         self.func = func
#         self.func_args = args
#         self.func_kwargs = kwargs
#         self.daemon = True

#     def run(self):
#         processor(self.input_queue, self.output_queue,
#                   self.func, *self.func_args, **self.func_kwargs)


# class WorkerControl(WorkerController):
#     """Subclass WorkerController to remove multiprocessing."""
#     def _create_and_start_workers(self):
#         """
#         Create and start worker processes.
#         """
#         self._workers = [_ProcThread(*self._processor['args'],
#                                      **self._processor['kwargs'])
#                          for i in range(self._n_workers)]
#         for _worker in self._workers:
#             _worker.start()
#         self._flag_active = True


class TestWorkerController(unittest.TestCase):

    def setUp(self):
        self._app = QtWidgets.QApplication(sys.argv)

    def tearDown(self):
        self._app.quit()

    def wait_for_queue(self, wc):
        t0 = time.time()
        while time.time() - t0 < 10:
            time.sleep(0.05)
            if wc._queues['send'].qsize() ==0:
                break
        time.sleep(0.1)

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

    def test_n_workers_get(self):
        num_workers = 5
        wc = WorkerController(num_workers)
        self.assertEqual(wc.n_workers, num_workers)

    def test_n_workers_set(self):
        wc = WorkerController()
        num_workers = 5
        wc.n_workers = num_workers
        self.assertEqual(wc.n_workers, num_workers)

    def test_n_workers_set_wrong(self):
        wc = WorkerController()
        num_workers = 5.5
        with self.assertRaises(ValueError):
            wc.n_workers = num_workers

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
        self.wait_for_queue(wc)
        wc.stop()
        time.sleep(0.3)
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
        self.assertEqual(wc._processor['args'][3], local_test_func)
        self.assertEqual(wc._processor['args'][4:], _args)

    def test_cycle_pre_run(self):
        wc = WorkerController()
        wc._cycle_pre_run()
        wc._cycle_post_run()
        self.assertEqual(wc._WorkerController__progress_done, 0)

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

    def test_put_next_task_in_queue(self):
        wc = WorkerController()
        wc._to_process = [1, 2, 3]
        wc._put_next_task_in_queue()
        self.assertEqual(wc._queues['send'].qsize(), 1)

    def test_get_and_emit_all_queue_items(self):
        _res1 = 3
        _res2 = [1, 1]
        wc = WorkerController()
        wc._queues['recv'].put([0, _res1])
        wc._queues['recv'].put([0, _res2])
        wc._WorkerController__progress_target = 2
        _spy = QtTest.QSignalSpy(wc.results)
        wc._get_and_emit_all_queue_items()
        self.assertEqual(len(_spy), 2)
        self.assertEqual(_spy[0][1], _res1)
        self.assertEqual(_spy[1][1], _res2)

    def test_results_signal(self):
        _tasks = [1, 2, 3, 4]
        _target = {local_test_func(item, 0, 0) for item in _tasks}
        wc = WorkerController(n_workers=4)
        wc.change_function(local_test_func, *(0, 0))
        result_spy = QtTest.QSignalSpy(wc.results)
        progress_spy = QtTest.QSignalSpy(wc.progress)
        wc.add_tasks(_tasks)
        wc.finalize_tasks()
        wc.start()
        self.wait_for_queue(wc)
        wc.stop()
        time.sleep(0.1)
        _results = get_spy_values(result_spy, index=1)
        _progress = get_spy_values(progress_spy)
        _exp_progress = [index / len(_tasks)
                          for index in range(1, len(_tasks) + 1)]
        self.assertEqual(set(_results), _target)
        self.assertEqual(_progress, _exp_progress)


if __name__ == "__main__":
    unittest.main()

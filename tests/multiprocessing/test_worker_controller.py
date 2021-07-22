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

import numpy as np

from PyQt5 import QtCore, QtWidgets, QtTest
from pydidas.multiprocessing import WorkerController, processor


def test_func(index, *args, **kwargs):
    index = (index
             + np.sum(np.fromiter([arg for arg in args], float))
             + np.sum(np.fromiter([kwargs[key] for key in kwargs], float))
             )
    return 3 * index


def get_spy_values(spy):
    return [spy[index][0] for index in range(len(spy))]


class _ProcThread(threading.Thread):
    """ Simple Thread to test blocking input / output. """
    def __init__(self, input_queue, output_queue, func, *args, **kwargs):
        super().__init__()
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.func = func
        self.func_args = args
        self.func_kwargs = kwargs
        self.daemon = True

    def run(self):
        processor(self.input_queue, self.output_queue,
                  self.func, *self.func_args, **self.func_kwargs)


class WorkerControl(WorkerController):
    """Subclass WorkerController to remove multiprocessing."""
    def _create_and_start_workers(self):
        """
        Create and start worker processes.
        """
        self._workers = [_ProcThread(*self._processor['args'],
                                     **self._processor['kwargs'])
                         for i in range(self._n_workers)]
        for _worker in self._workers:
            _worker.start()
        self._flag_active = True


class TestWorkerController(unittest.TestCase):

    def setUp(self):
        self._app = QtWidgets.QApplication(sys.argv)

    def tearDown(self):
        self._app.quit()

    def test_main_object(self):
        # this will only test the setup method
        ...

    def test_test_func_i(self):
        index = 0
        args = (0, 0, 0)
        kwargs = dict(a=0, b=0)
        self.assertEqual(test_func(index, *args, **kwargs), 0)

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

    def test_restart(self):
        wc = WorkerController()
        wc.suspend()
        wc.restart()
        self.assertEqual(wc._flag_running, True)

    def test_change_function(self):
        _args = (0, 0)
        wc = WorkerController()
        wc.change_function(test_func, *_args)
        self.assertEqual(wc._processor['args'][2], test_func)
        self.assertEqual(wc._processor['args'][3:], _args)

    def test_add_task(self):
        wc = WorkerController()
        wc.suspend()
        wc.add_task(1)
        self.assertEqual(wc._to_process, [1])

    def test_add_tasks(self):
        _tasks = [1, 2, 3]
        wc = WorkerController()
        wc.suspend()
        wc.add_tasks(_tasks)
        self.assertEqual(wc._to_process, _tasks)

    def test_results_signal(self):
        _tasks = [1, 2, 3, 4]
        wc = WorkerControl(n_workers=4)
        result_spy = QtTest.QSignalSpy(wc.results)
        progress_spy = QtTest.QSignalSpy(wc.progress)
        wc.add_tasks(_tasks)
        wc.finalize_tasks()
        wc.start()
        time.sleep(0.4)
        wc.stop()
        time.sleep(0.1)
        del wc
        _results = get_spy_values(result_spy)
        _progress = get_spy_values(progress_spy)
        _exp_progress = [index / len(_tasks)
                          for index in range(1, len(_tasks) + 1)]
        self.assertEqual(_progress, _exp_progress)
        self.assertEqual(_results, _tasks)


if __name__ == "__main__":
    unittest.main()

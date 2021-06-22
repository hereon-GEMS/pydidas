
import threading
import unittest
import time
import sys
import numpy as np

from PyQt5 import QtCore, QtWidgets, QtTest
from pydidas.multiprocess import WorkerController, processor


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

    def _join_workers(self):
        """
        Join the workers back to the thread and free their resources.
        """
        for _worker in self._workers:
            self._queues['send'].put(None)
            _worker.join()
        self._flag_active = False


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
        wc.start()
        time.sleep(0.4)
        wc.stop()
        time.sleep(0.05)
        _results = get_spy_values(result_spy)
        _progress = get_spy_values(progress_spy)
        _exp_progress = [index / len(_tasks)
                          for index in range(1, len(_tasks) + 1)]
        self.assertEqual(_progress, _exp_progress)
        self.assertEqual(_results, _tasks)


if __name__ == "__main__":
    unittest.main()

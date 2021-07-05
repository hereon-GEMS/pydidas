
import unittest
import time
import threading
import queue
import numpy as np
import multiprocessing as mp

from pydidas.multiprocessing import processor
from pydidas.multiprocessing.app_processor_func import app_processor
from pydidas.apps.mp_test_app import MpTestApp


class _ProcThread(threading.Thread):

    """ Simple Thread to test blocking input / output. """

    def __init__(self, input_queue, output_queue, stop_queue, app, app_params,
                 app_config):
        super().__init__()
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.stop_queue = stop_queue
        self.app = app
        self.app_params = app_params
        self.app_config = app_config

    def run(self):
       app_processor(self.input_queue, self.output_queue, self.stop_queue,
                     self.app, self.app_params, self.app_config)


class Test_app_processor(unittest.TestCase):

    def setUp(self):
        self.input_queue = mp.Queue()
        self.output_queue = mp.Queue()
        self.stop_queue = mp.Queue()
        self.app = MpTestApp()
        self.n_test = 100
        self.app.multiprocessing_pre_run(0, self.n_test)

    def tearDown(self):
        ...

    def put_ints_in_queue(self, finalize=True):
        for i in range(self.n_test):
            self.input_queue.put(i)
        if finalize:
            self.input_queue.put(None)

    def get_results(self):
        _tasks = []
        _results = []
        for i in range(self.n_test):
            item = self.output_queue.get()
            _tasks.append(item[0])
            _results.append(item[1])
        return _tasks, _results

    def test_run_plain(self):
        self.put_ints_in_queue()
        app_processor(self.input_queue, self.output_queue, self.stop_queue,
                      self.app.__class__, self.app.params.get_copy(),
                      self.app._config)

        _tasks, _results = self.get_results()
        self.assertEqual(_tasks, list( self.app.multiprocessing_get_tasks()))

    def test_run_with_empty_queue(self):
        _thread = _ProcThread(self.input_queue, self.output_queue,
                              self.stop_queue, self.app.__class__,
                              self.app.params.get_copy(),
                              self.app._config)
        _thread.start()
        time.sleep(0.05)
        self.input_queue.put(None)
        time.sleep(0.05)
        with self.assertRaises(queue.Empty):
            self.output_queue.get_nowait()

    def test_stop_signal(self):
        self.put_ints_in_queue(finalize=False)
        _thread = _ProcThread(self.input_queue, self.output_queue,
                              self.stop_queue, self.app.__class__,
                              self.app.params.get_copy(),
                              self.app._config)
        _thread.start()
        _tasks, _results = self.get_results()
        time.sleep(0.1)
        self.assertTrue(_thread.is_alive())
        self.stop_queue.put(1)

if __name__ == "__main__":
    unittest.main()

# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import multiprocessing as mp
import threading
import time
import unittest

from qtpy import QtWidgets

from pydidas.multiprocessing import app_processor
from pydidas.unittest_objects.mp_test_app import MpTestApp


class _ProcThread(threading.Thread):
    """Simple Thread to test blocking input / output."""

    def __init__(
        self,
        input_queue,
        output_queue,
        stop_queue,
        aborted_queue,
        app,
        app_params,
        app_config,
    ):
        super().__init__()
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.stop_queue = stop_queue
        self.aborted_queue = aborted_queue
        self.app = app
        self.app_params = app_params
        self.app_config = app_config

    def run(self):
        app_processor(
            self.input_queue,
            self.output_queue,
            self.stop_queue,
            self.aborted_queue,
            self.app,
            self.app_params,
            self.app_config,
            wait_for_output_queue=False,
        )


class Test_app_processor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._qtapp = QtWidgets.QApplication.instance()
        if cls._qtapp is None:
            cls._qtapp = QtWidgets.QApplication([])

    @classmethod
    def tearDownClass(cls):
        cls._qtapp.quit()

    def setUp(self):
        self.input_queue = mp.Queue()
        self.output_queue = mp.Queue()
        self.stop_queue = mp.Queue()
        self.aborted_queue = mp.Queue()
        self.app = MpTestApp()
        self.n_test = self.app._config["max_index"]
        self.app.multiprocessing_pre_run()

    def tearDown(self):
        self.input_queue.close()
        self.output_queue.close()
        self.stop_queue.close()
        self.aborted_queue.close()

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
        app_processor(
            self.input_queue,
            self.output_queue,
            self.stop_queue,
            self.aborted_queue,
            self.app.__class__,
            self.app.params.copy(),
            self.app._config,
            wait_for_output_queue=False,
        )
        time.sleep(0.1)
        _tasks, _results = self.get_results()
        self.assertEqual(_tasks, list(self.app.multiprocessing_get_tasks()))
        _stopper = self.output_queue.get()
        self.assertEqual(_stopper, [None, None])

    def test_run_with_empty_queue(self):
        _thread = _ProcThread(
            self.input_queue,
            self.output_queue,
            self.stop_queue,
            self.aborted_queue,
            self.app.__class__,
            self.app.params.copy(),
            self.app._config,
        )
        _thread.start()
        time.sleep(0.05)
        self.input_queue.put(None)
        time.sleep(0.05)
        _stopper = self.output_queue.get_nowait()
        self.assertEqual(_stopper, [None, None])

    def test_stop_signal(self):
        self.put_ints_in_queue(finalize=False)
        _thread = _ProcThread(
            self.input_queue,
            self.output_queue,
            self.stop_queue,
            self.aborted_queue,
            self.app.__class__,
            self.app.params.copy(),
            self.app._config,
        )
        _thread.start()
        _tasks, _results = self.get_results()
        time.sleep(0.1)
        self.assertTrue(_thread.is_alive())
        self.stop_queue.put(1)
        time.sleep(0.1)
        self.assertEqual(self.aborted_queue.get(), 1)


if __name__ == "__main__":
    unittest.main()

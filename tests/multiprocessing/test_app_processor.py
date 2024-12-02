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
import queue
import threading
import time
import unittest

from pydidas.multiprocessing import app_processor
from pydidas.unittest_objects.mp_test_app import MpTestApp
from pydidas.unittest_objects.mp_test_app_wo_tasks import MpTestAppWoTasks
from qtpy import QtWidgets


class _ProcThread(threading.Thread):
    """Simple Thread to test blocking input / output."""

    def __init__(
        self, mp_config: dict, app, app_params, app_config, use_tasks: bool = True
    ):
        super().__init__()
        self._mp_config = mp_config
        self.app = app
        self.app_params = app_params
        self.app_config = app_config
        self._use_tasks = use_tasks

    def run(self):
        app_processor(
            self._mp_config,
            self.app,
            self.app_params,
            self.app_config,
            wait_for_output_queue=False,
            use_tasks=self._use_tasks,
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
        self._lock_manager = mp.Manager()
        self._mp_config = {
            "queue_input": mp.Queue(),
            "queue_output": mp.Queue(),
            "queue_stop": mp.Queue(),
            "queue_finished": mp.Queue(),
            "queue_signal": mp.Queue(),
            "logging_level": 10,
            "lock": self._lock_manager.Lock(),
        }

    def tearDown(self):
        self._mp_config["queue_input"].close()
        self._mp_config["queue_output"].close()
        self._mp_config["queue_stop"].close()
        self._mp_config["queue_finished"].close()
        self._mp_config["queue_signal"].close()
        self._lock_manager.shutdown()

    def put_ints_in_queue(self, finalize=True):
        for i in range(self.app._config["max_index"]):
            self._mp_config["queue_input"].put(i)
        if finalize:
            self._mp_config["queue_input"].put(None)

    def get_task_results(self):
        _tasks = []
        _results = []
        for i in range(self.app._config["max_index"]):
            item = self._mp_config["queue_output"].get()
            _tasks.append(item[0])
            _results.append(item[1])
        return _tasks, _results

    def get_taskless_results(self):
        _results = []
        _tasks = []
        while True:
            try:
                _index, _item = self._mp_config["queue_output"].get_nowait()
                _results.append(_item)
                _tasks.append(_index)
            except queue.Empty:
                break
        return _tasks, _results

    def test_run__w_tasks(self):
        self.app = MpTestApp()
        self.app.multiprocessing_pre_run()
        self.put_ints_in_queue()
        app_processor(
            self._mp_config,
            self.app.__class__,
            self.app.params.copy(),
            self.app._config,
            wait_for_output_queue=False,
        )
        time.sleep(0.1)
        _tasks, _results = self.get_task_results()
        self.assertEqual(_tasks, list(self.app.multiprocessing_get_tasks()))
        _stopper = self._mp_config["queue_output"].get()
        self.assertEqual(_stopper, [None, None])

    def test_run__w_tasks_and_empty_queue(self):
        self.app = MpTestApp()
        self.app.multiprocessing_pre_run()
        _thread = _ProcThread(
            self._mp_config,
            self.app.__class__,
            self.app.params.copy(),
            self.app._config,
            use_tasks=True,
        )
        _thread.start()
        time.sleep(0.05)
        self._mp_config["queue_input"].put(None)
        time.sleep(0.05)
        _stopper = self._mp_config["queue_output"].get_nowait()
        self.assertEqual(_stopper, [None, None])

    def test_run__stop_signal(self):
        self.app = MpTestApp()
        self.app.multiprocessing_pre_run()
        self.put_ints_in_queue(finalize=False)
        _thread = _ProcThread(
            self._mp_config,
            self.app.__class__,
            self.app.params.copy(),
            self.app._config,
            use_tasks=True,
        )
        _thread.start()
        _tasks, _results = self.get_task_results()
        time.sleep(0.1)
        self.assertTrue(_thread.is_alive())
        self._mp_config["queue_stop"].put(1)
        time.sleep(0.1)
        self.assertEqual(self._mp_config["queue_finished"].get(), 1)

    def test_run__wo_tasks(self):
        self.app = MpTestAppWoTasks()
        self.app.multiprocessing_pre_run()
        _thread = _ProcThread(
            self._mp_config,
            self.app.__class__,
            self.app.params.copy(),
            self.app._config,
            use_tasks=False,
        )
        _thread.start()
        time.sleep(0.1)
        self._mp_config["queue_stop"].put(1)
        time.sleep(0.05)
        _tasks, _results = self.get_taskless_results()
        time.sleep(0.01)
        self.assertTrue(len(_tasks) > 0)
        self.assertEqual(self._mp_config["queue_finished"].get_nowait(), 1)

    def test_run__stop_signal_wo_tasks(self):
        self.app = MpTestAppWoTasks()
        self.app.multiprocessing_pre_run()
        _thread = _ProcThread(
            self._mp_config,
            self.app.__class__,
            self.app.params.copy(),
            self.app._config,
            use_tasks=False,
        )
        _thread.start()
        time.sleep(0.05)
        self._mp_config["queue_stop"].put(1)
        time.sleep(0.05)
        self.assertEqual(self._mp_config["queue_finished"].get(), 1)
        _thread.join()


if __name__ == "__main__":
    unittest.main()

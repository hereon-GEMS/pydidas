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

from qtpy import QtWidgets

from pydidas.multiprocessing import app_processor_without_tasks
from pydidas.unittest_objects.mp_test_app_wo_tasks import MpTestAppWoTasks


class _ProcThread(threading.Thread):
    """Simple Thread to test blocking input / output."""

    def __init__(
        self,
        mp_config: dict,
        app,
        app_params,
        app_config,
    ):
        super().__init__()
        self._mp_config = mp_config
        self.app = app
        self.app_params = app_params
        self.app_config = app_config

    def run(self):
        app_processor_without_tasks(
            self._mp_config,
            self.app,
            self.app_params,
            self.app_config,
            wait_for_output_queue=False,
        )


class Test_app_processor_without_tasks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._qtapp = QtWidgets.QApplication.instance()
        if cls._qtapp is None:
            cls._qtapp = QtWidgets.QApplication([])

    @classmethod
    def tearDownClass(cls):
        cls._qtapp.quit()

    def setUp(self):
        self._mp_config = {
            "queue_input": mp.Queue(),
            "queue_output": mp.Queue(),
            "queue_stop": mp.Queue(),
            "queue_aborted": mp.Queue(),
        }
        self.app = MpTestAppWoTasks()
        self.n_test = self.app._config["max_index"]
        self.app.multiprocessing_pre_run()

    def tearDown(self):
        self._mp_config["queue_input"].close()
        self._mp_config["queue_output"].close()
        self._mp_config["queue_stop"].close()
        self._mp_config["queue_aborted"].close()

    def create_thread(self):
        return _ProcThread(
            self._mp_config,
            self.app.__class__,
            self.app.params.copy(),
            self.app._config,
        )

    def get_results(self):
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

    def test_run_plain(self):
        _thread = self.create_thread()
        _thread.start()
        time.sleep(0.05)
        self._mp_config["queue_stop"].put(1)
        time.sleep(0.05)
        _tasks, _results = self.get_results()
        time.sleep(0.01)
        self.assertTrue(len(_tasks) > 0)
        self.assertEqual(self._mp_config["queue_aborted"].get_nowait(), 1)

    def test_stop_signal(self):
        _thread = self.create_thread()
        _thread.start()
        time.sleep(0.05)
        self.assertTrue(_thread.is_alive())
        self._mp_config["queue_stop"].put(1)
        time.sleep(0.05)
        self.assertEqual(self._mp_config["queue_aborted"].get(), 1)


if __name__ == "__main__":
    unittest.main()

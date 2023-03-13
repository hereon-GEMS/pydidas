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

import time
import unittest

from qtpy import QtTest, QtWidgets

from pydidas.core import BaseApp
from pydidas.multiprocessing import AppRunner
from pydidas.unittest_objects.mp_test_app import MpTestApp


class TestAppRunner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt_app = QtWidgets.QApplication.instance()
        if cls.qt_app is None:
            cls.qt_app = QtWidgets.QApplication([])

    @classmethod
    def tearDownClass(cls):
        if cls.qt_app is not None:
            cls.qt_app.quit()

    def setUp(self):
        self.app = MpTestApp()
        self._runner = None

    def tearDown(self):
        if self._runner is not None:
            self._runner.exit()

    def wait_for_spy_signal(self, spy, timeout=8):
        _t0 = time.time()
        while True:
            QtTest.QTest.qWait(100)
            if len(spy) == 1:
                break
            if time.time() > _t0 + 6:
                raise TimeoutError("Waiting too long for final app state.")
        time.sleep(0.1)

    def test_setUp(self):
        # this will only test the setup method
        ...

    def test_call_app_method(self):
        self._runner = AppRunner(self.app)
        self._runner.call_app_method("multiprocessing_post_run")
        self.assertTrue(self._runner._AppRunner__app._config["mp_post_run_called"])

    def test_set_app_param(self):
        _num = 12345
        self._runner = AppRunner(self.app)
        self._runner.set_app_param("hdf5_last_image_num", _num)
        _appnum = self._runner._AppRunner__app.get_param_value("hdf5_last_image_num")
        self.assertEqual(_num, _appnum)

    def test_run(self):
        self._runner = AppRunner(self.app)
        _spy = QtTest.QSignalSpy(self._runner.sig_final_app_state)
        _spy2 = QtTest.QSignalSpy(self._runner.finished)
        self._runner.start()
        time.sleep(0.1)
        self.wait_for_spy_signal(_spy)
        _new_app = _spy[0][0]
        _image = _new_app._composite.image
        self.assertTrue((_image > 0).all())
        self.assertEqual(len(_spy2), 1)

    def test_get_app(self):
        self._runner = AppRunner(self.app)
        _app = self._runner.get_app()
        self.assertIsInstance(_app, BaseApp)

    def test_cycle_pre_run(self):
        self._runner = AppRunner(self.app)
        self._runner._cycle_pre_run()
        self._runner._cycle_post_run()
        self.assertEqual(self._runner.receivers(self._runner.sig_results), 1)
        self.assertEqual(self._runner.receivers(self._runner.sig_progress), 1)

    def test_cycle_post_run(self):
        self._runner = AppRunner(self.app)
        _spy = QtTest.QSignalSpy(self._runner.sig_final_app_state)
        self._runner._workers = []
        self._runner._cycle_post_run()
        self.assertIsInstance(_spy[0][0], MpTestApp)

    def test_check_if_running_false(self):
        self._runner = AppRunner(self.app)
        self._runner._AppRunner__check_is_running()

    def test_check_if_running_true(self):
        self._runner = AppRunner(self.app)
        self._runner._flag_running = True
        with self.assertRaises(RuntimeError):
            self._runner._AppRunner__check_is_running()

    def test_check_app_method_name(self):
        self._runner = AppRunner(self.app)
        with self.assertRaises(KeyError):
            self._runner._AppRunner__check_app_method_name("no_such_method")

    def test_check_app_is_set(self):
        self._runner = AppRunner(self.app)
        self._runner._AppRunner__app = None
        with self.assertRaises(TypeError):
            self._runner._AppRunner__check_app_is_set()

    def test_get_app_arguments(self):
        self._runner = AppRunner(self.app)
        _args = self._runner._AppRunner__get_app_arguments()
        self.assertIsInstance(_args, tuple)


if __name__ == "__main__":
    unittest.main()

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


import time
import unittest

from qtpy import QtCore, QtTest, QtWidgets

from pydidas import IS_QT6
from pydidas.core import BaseApp, PydidasQsettings
from pydidas.multiprocessing import AppRunner
from pydidas.unittest_objects.mp_test_app import MpTestApp


class TestAppRunner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt_app = QtWidgets.QApplication.instance()
        if cls.qt_app is None:
            cls.qt_app = QtWidgets.QApplication([])
        cls.q_settings = PydidasQsettings()
        cls._mosaic_border_width = cls.q_settings.value("user/mosaic_border_width")
        cls._mosaic_border_value = cls.q_settings.value("user/mosaic_border_value")
        cls.q_settings.set_value("user/mosaic_border_width", 0)
        cls.q_settings.set_value("user/mosaic_border_value", 1)

    @classmethod
    def tearDownClass(cls):
        cls.q_settings.set_value("user/mosaic_border_width", cls._mosaic_border_width)
        cls.q_settings.set_value("user/mosaic_border_value", cls._mosaic_border_value)
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

    def wait_for_spy_signal_qt6(self, spy, timeout=10):
        _t0 = time.time()
        while True:
            time.sleep(0.1)
            QtTest.QTest.qWait(1)
            if spy.count() >= 1:
                break
            if time.time() > _t0 + timeout:
                raise TimeoutError("Waiting too long for final app state.")
        time.sleep(0.1)

    def test_setUp(self):
        # this will only test the setup method
        ...

    def test_init(self):
        self._runner = AppRunner(self.app)
        self.assertTrue(self.app._config["run_prepared"])

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
        self._runner = AppRunner(self.app, n_workers=2)
        _spy = QtTest.QSignalSpy(self._runner.sig_final_app_state)
        _spy2 = QtTest.QSignalSpy(self._runner.finished)
        self._runner.start()
        time.sleep(0.1)
        if IS_QT6:
            self.wait_for_spy_signal_qt6(_spy2)
        else:
            self.wait_for_spy_signal(_spy2)
        time.sleep(1)
        _new_app = _spy.at(0)[0] if IS_QT6 else _spy[0][0]
        _image = _new_app._composite.image
        self.assertTrue((_image > 0).all())
        if IS_QT6:
            self.assertTrue(_spy2.count() >= 1)
        else:
            self.assertEqual(len(_spy2), 1)

    def test_get_app(self):
        self._runner = AppRunner(self.app)
        _app = self._runner.get_app()
        self.assertIsInstance(_app, BaseApp)

    def testcycle_pre_run(self):
        self._runner = AppRunner(self.app)
        self._runner.cycle_pre_run()
        if IS_QT6:
            _sig_results = QtCore.QMetaMethod.fromSignal(self._runner.sig_results)
            _sig_progress = QtCore.QMetaMethod.fromSignal(self._runner.sig_progress)
            self.assertTrue(self._runner.isSignalConnected(_sig_results))
            self.assertTrue(self._runner.isSignalConnected(_sig_progress))
        else:
            self.assertEqual(self._runner.receivers(self._runner.sig_results), 2)
            self.assertEqual(self._runner.receivers(self._runner.sig_progress), 1)

    def testcycle_post_run(self):
        self._runner = AppRunner(self.app)
        _spy = QtTest.QSignalSpy(self._runner.sig_final_app_state)
        self._runner._workers = []
        self._runner.cycle_post_run()
        if IS_QT6:
            self.assertIsInstance(_spy.at(0)[0], MpTestApp)
        else:
            self.assertIsInstance(_spy[0][0], MpTestApp)

    def test_check_if_running_false(self):
        self._runner = AppRunner(self.app)
        self._runner._AppRunner__check_is_running()

    def test_check_if_running_true(self):
        self._runner = AppRunner(self.app)
        self._runner.flags["running"] = True
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

    def test_copy__app_with_composite(self):
        self.app.multiprocessing_pre_run()
        self.app._composite.image[0, 0] = -1.23
        app2 = self.app.copy()
        self.assertEqual(app2._composite.image[0, 0], self.app._composite.image[0, 0])


if __name__ == "__main__":
    unittest.main()

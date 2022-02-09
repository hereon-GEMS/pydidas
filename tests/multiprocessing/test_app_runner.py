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
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import unittest
import sys

from PyQt5 import QtCore, QtTest

from pydidas.core import BaseApp
from pydidas.multiprocessing import AppRunner
from pydidas.unittest_objects.mp_test_app import MpTestApp


def quit_app():
    """Terminate the headless app."""
    _qtapp = QtCore.QCoreApplication.instance()
    _qtapp.deleteLater()
    _qtapp.exit()


class TestAppRunnerner(unittest.TestCase):

    def setUp(self):
        self.qt_app = QtCore.QCoreApplication(sys.argv)
        self.app = MpTestApp()

    def tearDown(self):
        self.qt_app.quit()

    def store_app(self, app):
        self.new_app = app

    def test_setUp(self):
        # this will only test the setup method
        ...

    def test_call_app_method(self):
        runner = AppRunner(self.app)
        runner.call_app_method('multiprocessing_post_run')
        self.assertTrue(runner._AppRunner__app._config['mp_post_run_called'])

    def test_set_app_param(self):
        _num = 12345
        runner = AppRunner(self.app)
        runner.set_app_param('hdf5_last_image_num', _num)
        _appnum = runner._AppRunner__app.get_param_value('hdf5_last_image_num')
        self.assertEqual(_num, _appnum)

    def test_run(self):
        runner = AppRunner(self.app)
        _spy = QtTest.QSignalSpy(runner.sig_finished)
        runner.sig_finished.connect(quit_app)
        runner.start()
        self.qt_app.exec_()
        self.assertEqual(len(_spy), 1)

    def test_final_app_state(self):
        runner = AppRunner(self.app)
        runner.sig_final_app_state.connect(self.store_app)
        runner.sig_finished.connect(quit_app)
        runner.start()
        self.qt_app.exec_()
        _image = self.new_app._composite.image
        self.assertTrue((_image > 0).all())

    def test_get_app(self):
        runner = AppRunner(self.app)
        _app = runner.get_app()
        self.assertIsInstance(_app, BaseApp)

    def test_cycle_pre_run(self):
        runner = AppRunner(self.app)
        runner._cycle_pre_run()
        runner._cycle_post_run()
        self.assertEqual(runner.receivers(runner.sig_results), 1)
        self.assertEqual(runner.receivers(runner.sig_progress), 1)

    def test_cycle_post_run(self):
        runner = AppRunner(self.app)
        _spy = QtTest.QSignalSpy(runner.sig_final_app_state)
        runner._workers = []
        runner._cycle_post_run()
        self.assertIsInstance(_spy[0][0], MpTestApp)

    def test_check_if_running_false(self):
        runner = AppRunner(self.app)
        runner._AppRunner__check_is_running()

    def test_check_if_running_true(self):
        runner = AppRunner(self.app)
        runner._flag_running = True
        with self.assertRaises(RuntimeError):
            runner._AppRunner__check_is_running()

    def test_check_app_method_name(self):
        runner = AppRunner(self.app)
        with self.assertRaises(KeyError):
            runner._AppRunner__check_app_method_name('no_such_method')

    def test_check_app_is_set(self):
        runner = AppRunner(self.app)
        runner._AppRunner__app = None
        with self.assertRaises(TypeError):
            runner._AppRunner__check_app_is_set()

    def test_get_app_arguments(self):
        runner = AppRunner(self.app)
        _args = runner._AppRunner__get_app_arguments()
        self.assertIsInstance(_args, tuple)


if __name__ == "__main__":
    unittest.main()

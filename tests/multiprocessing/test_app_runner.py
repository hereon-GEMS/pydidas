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
import sys
import numpy as np

from PyQt5 import QtCore, QtWidgets
from pydidas.multiprocessing import AppRunner, app_processor
from pydidas.multiprocessing.mp_test_app import MpTestApp

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
    def __init__(self, *app_args):
        super().__init__()
        self.app_args = app_args

    def run(self):
       app_processor(*self.app_args)


class AppRun(AppRunner):
    """Subclass WorkerController to remove multiprocessing."""
    def _create_and_start_workers(self):
        """
        Create and start worker processes.
        """
        self._workers = [_ProcThread(*self._processor['args'])
                         for i in range(self._n_workers)]
        for _worker in self._workers:
            _worker.start()
        self._flag_active = True


def quit_app():
    """Terminate the headless app."""
    _qtapp = QtCore.QCoreApplication.instance()
    _qtapp.exit()


@QtCore.pyqtSlot(object)
def final_app(_app):
    global app
    app = _app


class TestAppRunner(unittest.TestCase):

    def setUp(self):
        # self.qt_app = QtWidgets.QApplication(sys.argv)
        self.qt_app = QtCore.QCoreApplication(sys.argv)
        self.app = MpTestApp()

    def tearDown(self):
        self.qt_app.quit()

    def test_setUp(self):
        # this will only test the setup method
        ...

    def test_call_app_method(self):
        runner = AppRun(self.app)
        runner.call_app_method('multiprocessing_post_run')
        self.assertTrue(runner._AppRunner__app._config['mp_post_run_called'])

    def test_set_app_param(self):
        _num = 12345
        runner = AppRun(self.app)
        runner.set_app_param('hdf5_last_image_num', _num)
        _appnum = runner._AppRunner__app.get_param_value('hdf5_last_image_num')
        self.assertEqual(_num, _appnum)

    def test_run(self):
        runner = AppRun(self.app)
        runner.finished.connect(quit_app)
        runner.final_app_state.connect(final_app)
        runner.start()
        self.qt_app.exec_()
        _image = app._composite.image
        self.assertTrue((_image > 0).all())


if __name__ == "__main__":
    unittest.main()


import threading
import unittest
import time
import sys
import numpy as np

from PyQt5 import QtCore, QtWidgets, QtTest
from pydidas.multiprocessing import AppRunner, app_processor
from pydidas.apps.mp_test_app import MpTestApp

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
        runner.set_app_param('hdf_last_image_num', _num)
        _appnum = runner._AppRunner__app.get_param_value('hdf_last_image_num')
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

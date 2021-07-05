
import unittest
import time
import threading
import queue
import numpy as np
import multiprocessing as mp

from pydidas.apps.mp_test_app import MpTestApp
from pydidas.apps import BaseApp


class TestMpTestApp(unittest.TestCase):

    def setUp(self):
        self._indices = (3, 57)

    def tearDown(self):
        ...

    def test_create(self):
        app = MpTestApp()
        self.assertIsInstance(app, BaseApp)

    def test_mp_pre_run(self):
        app = MpTestApp()
        app.multiprocessing_pre_run()
        self.assertTrue(app._config['mp_pre_run_called'])

    def test_mp_get_tasks(self):
        app = MpTestApp()
        app.multiprocessing_pre_run(*self._indices)
        _tasks = app.multiprocessing_get_tasks()
        self.assertEqual(_tasks, range(*self._indices))

    def test_mp_func(self):
        self._indices = (3, 57)
        app = MpTestApp()
        app.multiprocessing_pre_run(*self._indices)
        _index, _image = app.multiprocessing_func(self._indices[0])
        self.assertEqual(_index, 0)
        self.assertIsInstance(_image, np.ndarray)

    def test_mp_post_run(self):
        app = MpTestApp()
        app.multiprocessing_post_run()
        self.assertTrue(app._config['mp_post_run_called'])

    def test_mp_store_results(self):
        self._indices = (3, 57)
        app = MpTestApp()
        app.multiprocessing_pre_run(*self._indices)
        _index, _image = app.multiprocessing_func(self._indices[0])
        app.multiprocessing_store_results(_index, _image)
        self.assertTrue((app._composite.image[:100, :100] > 0).all())

    def test_mp_wait(self):
        app = MpTestApp()
        self.assertEqual(app.multiprocessing_carryon(), False)
        self.assertEqual(app.multiprocessing_carryon(), True)




if __name__ == "__main__":
    unittest.main()

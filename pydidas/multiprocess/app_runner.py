# MIT License
#
# Copyright (c) 2021 Malte Storm, Helmholtz-Zentrum Hereon.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Module with the processor function which can be used for iterating over
multiprocessing function calls."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['AppRunner']

import copy
import time
import multiprocessing as mp
from numbers import Integral
from queue import Empty

from PyQt5 import QtCore

from .worker_controller import WorkerController
from .processor_func import processor
from ..apps import BaseApp

class AppRunner(WorkerController):
    """
    The WorkerController is a QThread which can spawn a number of processes
    to perform computations in parallel.

    A function with defined args and kwargs can be called in separate
    processes with the first function argument as the variable that differs
    between function calls.
    """
    progress = QtCore.pyqtSignal(float)
    results = QtCore.pyqtSignal(object)
    finished = QtCore.pyqtSignal()

    def __init__(self, app=None, n_workers=4):
        """
        Create a WorkerController.

        Parameters
        ----------
        n_workers : int, optional
            The number of spawned worker processes. The default is 4.
        """
        super().__init__(n_workers)
        self.__app = copy.copy(app)

    def call_app_method(self, method_name, *args, **kwargs):
        """
        Change a method of the app.


        Parameters
        ----------
        method_name : str
            The name of the Application.method.
        *args : type
            Any arguments which need to be passed to the method..
        **kwargs : kwargs
            Any keyword arguments which need to be passed to the method.

        Raises
        ------
        RuntimeError
            If the Application is currently running.

        Returns
        -------
        result : type
            The return object(s) from the App.method call.
        """
        self.__check_is_running()
        self.__check_app_method_name(method_name)
        method = getattr(self.__app, method_name)
        _result = method(*args, **kwargs)
        return _result

    def set_app_param(self, param_name, value):
        """
        Set a Parameter of the Application.

        Parameters
        ----------
        param_name : str
            The name of the Application Parameter.
        value : type
            The new value for the selected Parameter.
        """
        self.__check_app_is_set()
        self.__app.set_param_value(param_name, value)

    def run(self):
        """
        Run the thread event loop.

        This method is automatically called upon starting the thread.
        """
        while self._flag_thread_alive:
            if self._flag_running:
                self._create_and_start_workers()
            while self._flag_running:
                while len(self.__to_process) > 0:
                    self._put_next_task_in_queue()
                time.sleep(0.02)
                self._get_and_emit_all_queue_items()
            if self._flag_active:
                self._join_workers()
            time.sleep(0.02)
        self.finished.emit()

    def _wait_for_processes_to_finish(self, timeout=10):
        """
        Wait for the processes to finish their calculations.

        Parameters
        ----------
        timeout : float, optional
            The maximum time to wait (in seconds). The default is 10.
        """
        _t0 = time.time()
        while self._flag_active:
            time.sleep(0.05)
            if time.time() - _t0 >= timeout:
                break

    def _create_and_start_workers(self):
        """
        Create and start worker processes.
        """
        _worker_args= (self.__queues['send'], self.__queues['recv'],
                       self.__function['func'], *self.__function['args'])
        self.__workers = [mp.Process(target=processor, args=_worker_args,
                                    kwargs=self.__function['kwargs'])
                         for i in range(self.__n_workers)]
        for _worker in self.__workers:
            _worker.start()
        self._flag_active = True
        self.__progress_done = 0

    def _join_workers(self):
        """
        Join the workers back to the thread and free their resources.
        """
        for _worker in self.__workers:
            self.__queues['send'].put(None)
            _worker.join()
        self._flag_active = False

    def _put_next_task_in_queue(self):
        """
        Get the next task from the list and put it into the queue.
        """
        self._write_lock.lockForWrite()
        _arg = self.__to_process.pop(0)
        self._write_lock.unlock()
        self.__queues['send'].put(_arg)

    def _reset_task_list(self):
        """
        Reset and clear the list of tasks.
        """
        self._write_lock.lockForWrite()
        self.__to_process = []
        self._write_lock.unlock()

    def _update_function(self, func, *args, **kwargs):
        """
        Store the new function and its calling (keyword) arguments
        internally.

        Parameters
        ----------
        func : object
            The function.
        *args : object
            The function arguments
        **kwargs : object
            The function keyword arguments.
        """
        self.__function['func'] = func
        self.__function['args'] = args
        self.__function['kwargs'] = kwargs

    def _get_and_emit_all_queue_items(self):
        """
        Get all items from the queue and emit them as signals.
        """
        while True:
            try:
                res = self.__queues['recv'].get_nowait()
                self.results.emit(res)
                self.__progress_done += 1
                self.progress.emit(self.__progress_done
                                   / self.__progress_target)
                time.sleep(0.002)
            except Empty:
                break

    def __check_is_running(self):
        """Verify that the Thread is not actively running."""
        if self._flag_running:
            raise RuntimeError('Cannot call Application methods while the'
                               ' Application is running. Please call .stop()'
                               ' on the AppRunner first.')

    def __check_app_method_name(self, method_name):
        """Verify the Application has a method with the given name."""
        if not hasattr(self.__app, method_name):
            raise KeyError('The App does not have a method with name '
                           f'"{method_name}".')

    def __check_app_is_set(self):
        if not isinstance(self.__app, BaseApp):
            raise TypeError('Application is not an instance of BaseApp.'
                            ' Please set application first.')

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
__all__ = ['WorkerController']

import time
import multiprocessing as mp
from numbers import Integral
from queue import Empty

from PyQt5 import QtCore

from .processor_func import processor

class WorkerController(QtCore.QThread):
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

    def __init__(self, n_workers=4):
        """
        Create a WorkerController.

        Parameters
        ----------
        n_workers : int, optional
            The number of spawned worker processes. The default is 4.
        """
        super().__init__()
        self._flag_running = True
        self._flag_thread_alive = True
        self._flag_active = False
        self.__n_workers = n_workers
        self.__to_process = []
        self._write_lock = QtCore.QReadWriteLock()
        self.__workers = None
        self.__queues = dict(send=mp.Queue(), recv=mp.Queue())
        self.__function = dict(func=lambda x: x, args=(), kwargs={})
        self.__progress_done = 0
        self.__progress_target = 0

    @property
    def n_workers(self):
        """
        Get the number of worker processes.

        Returns
        -------
        int
            The number of workers.
        """
        return self.__n_workers

    @n_workers.setter
    def n_workers(self, number):
        """
        Change the number of worker processes.

        *Note*: This change does not take effect until the next time a new
        worker pool is created.

        Parameters
        ----------
        number : int
            The new number of workers

        Raises
        ------
        ValueError
            If number is not of type Integral.
        """
        if not isinstance(number, Integral):
            raise ValueError('The number of workers must be an integer '
                             'number.')
        self.__n_workers = number

    def stop(self):
        """
        Stop the thread from running and clean up.
        """
        self.suspend()
        self._flag_thread_alive = False

    def suspend(self):
        """
        Suspend the event loop.

        This method effectively suspends the event loop and calls for the
        workers to be joined again. New calculations can be performed by
        using the :py:meth`WorkerController.restart` method.
        """
        self._flag_running = False

    def restart(self):
        """
        Restart the event loop.

        This method allow the event loop to run and to submit tasks via the
        queue to the workers.
        """
        self._flag_running = True

    def change_function(self, func, *args, **kwargs):
        """
        Change the function called by the workers.

        This method stops any active processing and resets the queue. Then,
        the function is changed and new workers are spawned. To run the new
        function, new tasks must be submitted.

        Parameters
        ----------
        func : object
            The function to be called by the workers.
        *args : type
            Any arguments which need to be passed to the function.
        **kwargs : kwargs
            Any keyword arguments which need to be passed to the function.
        """
        self.suspend()
        self.__wait_for_processes_to_finish()
        self.__reset_task_list()
        self.__update_function(func, *args, **kwargs)
        self.restart()

    def add_task(self, task_arg):
        """
        Add a task to the worker pool.

        This will add a task to the worker pool to call the function defined
        in :py:meth`WorkerController.change_function` method. Note that the
        task_arg given here will be interpreted as the first argument
        required by the function.

        Parameters
        ----------
        task_arg : object
            The first argument for the processing function.
        """
        self._write_lock.lockForWrite()
        self.__to_process.append(task_arg)
        self._write_lock.unlock()
        self.__progress_target += 1

    def add_tasks(self, task_args):
        """
        Add tasks to the worker pool.

        This will add tasks to the worker pool to call the function defined
        in :py:meth`WorkerController.change_function` method. Note that the
        task_arg given here will be interpreted as the first argument
        required by the function.

        Parameters
        ----------
        task_args : Union[list, tuple, set]
            An iterable of the first argument for the processing function.
        """
        self._write_lock.lockForWrite()
        for task in task_args:
            self.__to_process.append(task)
        self._write_lock.unlock()
        self.__progress_target = len(task_args)

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
                    self.__put_next_task_in_queue()
                time.sleep(0.02)
                self.__get_and_emit_all_queue_items()
            if self._flag_active:
                self._join_workers()
            time.sleep(0.02)
        self.finished.emit()

    def __wait_for_processes_to_finish(self, timeout=10):
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

    def __put_next_task_in_queue(self):
        """
        Get the next task from the list and put it into the queue.
        """
        self._write_lock.lockForWrite()
        _arg = self.__to_process.pop(0)
        self._write_lock.unlock()
        self.__queues['send'].put(_arg)

    def __reset_task_list(self):
        """
        Reset and clear the list of tasks.
        """
        self._write_lock.lockForWrite()
        self.__to_process = []
        self._write_lock.unlock()

    def __update_function(self, func, *args, **kwargs):
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

    def __get_and_emit_all_queue_items(self):
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

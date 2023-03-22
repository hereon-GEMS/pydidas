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

"""
Module with the WorkerController class which is a subclassed QThread to
control multiprocessing of computations.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["WorkerController"]

import time
import multiprocessing as mp
from numbers import Integral
from queue import Empty
from contextlib import contextmanager

from qtpy import QtCore

from .processor_ import processor
from ..core import PydidasQsettings
from ..core.utils import pydidas_logger

logger = pydidas_logger()


class WorkerController(QtCore.QThread):
    """
    The WorkerController is a QThread which can spawn a number of processes
    to perform computations in parallel.

    A function with defined args and kwargs can be called in separate
    processes with the first function argument as the variable that differs
    between function calls.

    Parameters
    ----------
    n_workers : int, optional
        The number of spawned worker processes. The default is None which will
        use the globally defined pydidas setting for the number of workers.
    function : Union[type, None], optional
        The function to be called by the workers. If not specified at init, it must
        be set later for the workers to actually perform tasks.
    """

    sig_progress = QtCore.Signal(float)
    sig_results = QtCore.Signal(object, object)

    def __init__(self, n_workers=None, function=None):
        super().__init__()
        self._flag_running = False
        self._flag_thread_alive = True
        self._flag_active = False
        self._flag_stop_after_run = False
        if n_workers is None:
            _settings = PydidasQsettings()
            n_workers = _settings.value("global/mp_n_workers", int)
        self._n_workers = n_workers
        self._to_process = []
        self._write_lock = QtCore.QReadWriteLock()
        self._workers = []
        self._workers_done = 0
        self._queues = dict(
            send=mp.Queue(), recv=mp.Queue(), stop=mp.Queue(), finished=mp.Queue()
        )
        _worker_args = (
            self._queues["send"],
            self._queues["recv"],
            self._queues["stop"],
            self._queues["finished"],
            None,
        )
        self._processor = dict(func=processor, args=_worker_args, kwargs={})
        self._progress_done = 0
        self._progress_target = 0

    @contextmanager
    def write_lock(self):
        """
        Set up the write lock which adding tasks to the list.
        """
        try:
            self._write_lock.lockForWrite()
            yield
        finally:
            self._write_lock.unlock()

    @property
    def n_workers(self):
        """
        Get the number of worker processes.

        Returns
        -------
        int
            The number of workers.
        """
        return self._n_workers

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
            raise ValueError("The number of workers must be an integer number.")
        self._n_workers = number

    @property
    def progress(self):
        """
        Get the progress level of the current computations.

        Returns
        -------
        float
            The progress, normalized to the range [0, 1]. A value of -1
            means that no tasks have been defined.
        """
        if self._progress_target == 0:
            return -1
        return self._progress_done / self._progress_target

    def stop(self):
        """
        Stop the thread from running and clean up.
        """
        self.add_tasks([None] * self.n_workers, are_stop_tasks=True)
        self.suspend()
        self.send_stop_signal()
        self._flag_thread_alive = False

    def suspend(self):
        """
        Suspend the event loop.

        This method effectively suspends the event loop and calls for the
        workers to be joined again. New calculations can be performed by
        using the :py:meth`WorkerController.restart` method.
        """
        self._flag_running = False
        self._wait_for_processes_to_finish()

    def _wait_for_processes_to_finish(self, timeout=2):
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
        *args : tuple
            Any additional arguments which need to be passed to the function. The first
            function argument will always the the task.
        **kwargs : dict
            Any keyword arguments which need to be passed to the function.
        """
        self.suspend()
        self.reset_task_list()
        self._update_function(func, *args, **kwargs)
        self.restart()

    def reset_task_list(self):
        """
        Reset and clear the list of tasks.
        """
        with self.write_lock():
            self._to_process = []

    def _update_function(self, func, *args, **kwargs):
        """
        Store the new function and its calling (keyword) arguments
        internally.

        Parameters
        ----------
        func : object
            The function.
        *args : tuple
            The function arguments
        **kwargs : dict
            The function keyword arguments.
        """
        self._processor["args"] = (
            self._queues["send"],
            self._queues["recv"],
            self._queues["stop"],
            self._queues["finished"],
            func,
            *args,
        )
        self._processor["kwargs"] = kwargs

    def restart(self):
        """
        Restart the event loop.

        This method allow the event loop to run and to submit tasks via the
        queue to the workers.
        """
        self._flag_running = True

    def add_task(self, task):
        """
        Add a task to the worker pool.

        This will add a task to the worker pool to call the function defined
        in :py:meth`WorkerController.change_function` method. Note that the
        task_arg given here will be interpreted as the first argument
        required by the function.

        Parameters
        ----------
        task : object
            The first argument for the processing function.
        """
        with self.write_lock():
            self._to_process.append(task)

    def add_tasks(self, tasks, are_stop_tasks=False):
        """
        Add tasks to the worker pool.

        This will add tasks to the worker pool to call the function defined
        in :py:meth`WorkerController.change_function` method. Note that the
        task_arg given here will be interpreted as the first argument
        required by the function.

        Parameters
        ----------
        tasks : Union[list, tuple, set]
            An iterable of the first argument for the processing function.
        are_stop_tasks : bool
            Keyword to signal that the added tasks are stop tasks. This flag will
            disable updating the task target number.
        """
        with self.write_lock():
            for task in tasks:
                self._to_process.append(task)
            self._write_lock.unlock()
        if not are_stop_tasks:
            self._progress_target += len(tasks)

    def finalize_tasks(self):
        """
        Finalize the task list.

        This will add tasks to tell the workers to shut down and set a flag
        to quit the loop once processing is done.
        """
        with self.write_lock():
            for task in [None] * self._n_workers:
                self._to_process.append(task)
        self._flag_stop_after_run = True

    def send_stop_signal(self):
        """
        Send stop signal to workers.

        This method will send stop signals to all workers.
        Note that the runtime of the workers will be determined by the runtime
        of the called function. the currrent call will be finished before the stop
        signal will be processed.
        """
        for _ in self._workers:
            self._queues["stop"].put(1)

    def run(self):
        """
        Run the thread event loop.

        This method is automatically called upon starting the thread.
        """
        self._workers_done = 0
        self._flag_running = True
        while self._flag_thread_alive:
            if self._flag_running and not self._flag_active:
                self._cycle_pre_run()
            while self._flag_running:
                while len(self._to_process) > 0:
                    self._put_next_task_in_queue()
                time.sleep(0.001)
                self._get_and_emit_all_queue_items()
                self._check_if_workers_done()
            if self._flag_active:
                logger.debug("Starting post run")
                self._cycle_post_run()
            time.sleep(0.001)
        logger.debug("finished worker_controller loop")

    def _cycle_pre_run(self):
        """
        Perform operations before entering the main processing loop.
        """
        self._flag_active = True
        self._progress_done = 0
        _tmp_to_process = self._to_process[:]
        while None in _tmp_to_process:
            _tmp_to_process.remove(None)
        self._progress_target = len(_tmp_to_process)
        self._create_and_start_workers()

    def _create_and_start_workers(self):
        """
        Create and start worker processes.
        """
        _pid = mp.current_process().pid
        self._workers = [
            mp.Process(
                target=self._processor["func"],
                args=self._processor["args"],
                kwargs=self._processor["kwargs"],
                name=f"pydidas_{_pid}_worker-{i}",
                daemon=True,
            )
            for i in range(self._n_workers)
        ]
        for _worker in self._workers:
            _worker.start()

    def _put_next_task_in_queue(self):
        """
        Get the next task from the list and put it into the queue.
        """
        with self.write_lock():
            _arg = self._to_process.pop(0)
        self._queues["send"].put(_arg)

    def _get_and_emit_all_queue_items(self):
        """
        Get all items from the queue and emit them as signals.
        """
        while True:
            try:
                _task, _results = self._queues["recv"].get_nowait()
                self.sig_results.emit(_task, _results)
                logger.debug("Emitted results %s" % _task)
                self._progress_done += 1
                self.sig_progress.emit(self.progress)
            except Empty:
                break
            time.sleep(0.001)

    def _check_if_workers_done(self):
        """
        Check if workers are all done.
        """
        try:
            for _worker in self._workers:
                self._queues["finished"].get_nowait()
                self._workers_done += 1
                logger.debug("Worker done")
        except Empty:
            pass
        if self._workers_done >= len(self._workers):
            self._flag_running = False
            logger.debug("Stopped running")

    def _cycle_post_run(self, timeout=10):
        """
        Perform operations after the the main processing loop.

        Parameters
        ----------
        timeout : float
            The waiting time to wait on the workers to send the finished
            signal before raising a TimeoutError.
        """
        logger.debug("Calling join on workers")
        self._join_workers()
        logger.debug("Joined on workers")
        if self._flag_stop_after_run:
            self._flag_thread_alive = False
        logger.debug("Waiting for finished signals from workers")
        self._wait_for_worker_finished_signals(timeout)
        logger.debug("finished cycle post run")

    def _join_workers(self):
        """
        Join the workers back to the thread and free their resources.
        """
        for _worker in self._workers:
            self._queues["stop"].put(1)
        for _worker in self._workers:
            _worker.terminate()
            _worker.join()
        self._workers = []
        self._flag_active = False
        while True:
            try:
                self._queues["stop"].get_nowait()
            except Empty:
                break

    def _wait_for_worker_finished_signals(self, timeout=10):
        """
        Wait for the worker finished signals for a maximum of "timeout"
        seconds.

        Parameters
        ----------
        timeout : float, optional
            The maximum wait time in seconds.. The default is 10.

        Raises
        ------
        TimeoutError
            If the maximum wait time is passed.
        """
        if not self._flag_running:
            return
        _tstart = time.time()
        while time.time() - _tstart <= timeout:
            self._check_if_workers_done()
            if not self._flag_running:
                return
        raise TimeoutError("Waiting too long for workers to finish.")

    def exit(self, code=None):
        """
        Call the exit method.

        This exit method adds shutdown calls to the Queue threads.
        """
        for _queue in self._queues.values():
            _queue.close()
            _queue.join_thread()
        if code is not None:
            super().exit(code)
        else:
            super().exit()

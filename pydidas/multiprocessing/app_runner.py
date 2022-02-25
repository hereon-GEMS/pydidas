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
Module with the AppRunner class which is a QThread which can spawn and control
worker processes and run in parallel to an event thread.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['AppRunner']

import multiprocessing as mp

from qtpy import QtCore

from ..core import BaseApp
from ..core.utils import pydidas_logger, LOGGING_LEVEL
from .worker_controller import WorkerController
from .app_processor_ import app_processor


logger = pydidas_logger()
logger.setLevel(LOGGING_LEVEL)


class AppRunner(WorkerController):
    """
    The AppRunner is a subclassed WorkerController (QThread) which can
    spawn a number of processes to perform computations in parallel.

    The App runner requires a BaseApp (or subclass) instance with a
    defined method layout as defined in the BaseApp.

    The AppRunner will create a local copy of the Application and only
    modify the local version.

    Notes
    -----

    The AppRunner has the following signals which can be connected to:

    progress : QtCore.Signal(float)
        This singal emits the current relative progress in the interval (0..1)
        in the computations, based on the number of returned results relative
        to the total tasks.
    results : QtCore.Signal(int, object)
        The results as returned from the multiprocessing Processes.
    finished : QtCore.Signal()
        This signal is emitted when the computations are finished. If the
        AppRunner is running headless, it needs to be connected to the
        app.exit slot to finish the event loop.
    final_app_state : QtCore.Signal(object)
        This signal emits a copy of the App after all the calculations have
        been performed if it needs to be used in another context.

    Parameters
    ----------
    app : pydidas.core.BaseApp
        The instance of the application to be run.
    n_workers : int, optional
        The number of spawned worker processes. The default is None which will
        use the globally defined pydidas setting for the number of workers.
    processor : Union[pydidas.multiprocessing.app_processor,
                      pydidas.multiprocessing.app_processor_without_tasks]
        The processor to be used. The generic 'app_processor' requires input
        tasks whereas the 'app_processor_without_tasks' can run indefinite
        without any defined tasks. The app itself is responsible for managing
        tasks on the fly. The default is app_processor.
    """
    sig_progress = QtCore.Signal(float)
    sig_results = QtCore.Signal(int, object)
    sig_finished = QtCore.Signal()
    sig_final_app_state = QtCore.Signal(object)

    def __init__(self, app, n_workers=None, processor=app_processor):
        logger.debug('Starting AppRunner')
        super().__init__(n_workers)
        self.__app = app.get_copy(slave_mode=True)
        self.__check_app_is_set()
        self._processor['func'] = processor
        logger.debug('Finished init')

    def call_app_method(self, method_name, *args, **kwargs):
        """
        Call a method of the app on the AppRunner's copy.

        Parameters
        ----------
        method_name : str
            The name of the Application method.
        *args : tuple
            Any arguments which need to be passed to the method.
        **kwargs : kwargs
            Any keyword arguments which need to be passed to the method.

        Raises
        ------
        RuntimeError
            If the Application is currently running.

        Returns
        -------
        result : type
            The return object(s) from the App method call.
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

    def get_app(self):
        """
        Get the reference to the interally stored app.

        Note
        ----
        This method will only provide a copy of the app and keep the internal
        instance for further use.

        Returns
        -------
        pydidas.core.BaseApp
            The application instance.
        """
        return self.__app.get_copy()

    def _cycle_pre_run(self):
        """
        Perform pre-multiprocessing operations.

        This time slot is used to prepare the App by running the
        :my:meth:`app.multiprocessing_pre_run`, settings the tasks and
        starting the workers.
        """
        self.__app.multiprocessing_pre_run()
        self._processor['args'] = (self._queues['send'],
                                   self._queues['recv'],
                                   self._queues['stop'],
                                   self._queues['finished'],
                                   *self.__get_app_arguments())
        _tasks = self.__app.multiprocessing_get_tasks()
        self.add_tasks(_tasks)
        self.finalize_tasks()
        self.sig_results.connect(self.__app.multiprocessing_store_results)
        self.sig_progress.connect(self.__check_progress)
        self._create_and_start_workers()

    def _create_and_start_workers(self):
        """
        Create and start worker processes.
        """
        self._workers = [mp.Process(target=self._processor['func'],
                                    args=self._processor['args'], daemon=True)
                          for i in range(self._n_workers)]
        for _worker in self._workers:
            logger.debug('Starting Worker')
            _worker.start()
        self._flag_active = True
        self._progress_done = 0

    def _cycle_post_run(self, timeout=10):
        """
        Perform finishing operations of the App and close the multiprocessing
        Processes.
        """
        self._join_workers()
        self._wait_for_worker_finished_signals(timeout)
        self.__app.multiprocessing_post_run()
        self.sig_final_app_state.emit(self.__app.get_copy())

    @QtCore.Slot(float)
    def __check_progress(self, progress):
        """
        Check the progress and send the signal to stop the loop if all
        results have been received.

        Parameters
        ----------
        progress : float
            The relative progress of the calculations.
        """
        if progress >= 1:
            self.send_stop_signal()
            self.suspend()
            self.stop()

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
        """
        Verify that the App passed to the AppRunner is a
        :py:class:`pydidas.apps.BaseApp`.
        """
        if not isinstance(self.__app, BaseApp):
            raise TypeError('Application is not an instance of BaseApp.'
                            ' Please set application first.')

    def __get_app_arguments(self):
        """Get the App arguments to pass to the processor."""
        return (self.__app.__class__, self.__app.params.get_copy(),
                self.__app.get_config())

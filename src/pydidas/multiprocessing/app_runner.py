# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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

"""
Module with the AppRunner class which is a QThread which can spawn and control
worker processes and run in parallel to an event thread.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["AppRunner"]


from typing import Union

from qtpy import QtCore

from pydidas.core import BaseApp
from pydidas.core.utils import LOGGING_LEVEL, pydidas_logger
from pydidas.multiprocessing.app_processor_ import app_processor
from pydidas.multiprocessing.worker_controller import WorkerController


logger = pydidas_logger()
logger.setLevel(LOGGING_LEVEL)


class AppRunner(WorkerController):
    """
    The AppRunner is a subclassed WorkerController for running pydidas applications.

    The App runner requires a BaseApp (or subclass) instance with a
    defined method layout as defined in the BaseApp.

    The AppRunner will create a local copy of the Application and only
    modify the local version.

    Notes
    -----
    The AppRunner has the following signals which can be connected to:

    sig_final_app_state : QtCore.Signal(object)
        This signal emits a copy of the App after all the calculations have
        been performed if it needs to be used in another context.

    Parameters
    ----------
    app : pydidas.core.BaseApp
        The instance of the application to be run.
    n_workers : int, optional
        The number of spawned worker processes. The default is None which will
        use the globally defined pydidas setting for the number of workers.
    use_app_tasks : bool, optional
        Flag to toggle if the app works with tasks. The default is True.
    """

    sig_final_app_state = QtCore.Signal(object)
    sig_post_run_called = QtCore.Signal()

    def __init__(
        self,
        app: BaseApp,
        n_workers: Union[None, int] = None,
        use_app_tasks: bool = True,
    ):
        logger.debug("AppRunner: Starting AppRunner")
        WorkerController.__init__(self, n_workers=n_workers)
        if not app._config["run_prepared"]:
            app.multiprocessing_pre_run()
        self.sig_results.connect(app.multiprocessing_store_results)
        self.sig_post_run_called.connect(app.multiprocessing_post_run)
        self.__app = app.copy(clone_mode=True)
        self.__check_app_is_set()
        self._use_app_tasks = use_app_tasks
        self._processor["func"] = app_processor

    def call_app_method(self, method_name: str, *args: tuple, **kwargs: dict) -> object:
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
        result : object
            The return object(s) from the App method call.
        """
        self.__check_is_running()
        self.__check_app_method_name(method_name)
        method = getattr(self.__app, method_name)
        _result = method(*args, **kwargs)
        return _result

    def set_app_param(self, param_name: str, value: object):
        """
        Set a Parameter of the Application.

        Parameters
        ----------
        param_name : str
            The name of the Application Parameter.
        value : object
            The new value for the selected Parameter.
        """
        self.__check_app_is_set()
        self.__app.set_param_value(param_name, value)

    def get_app(self) -> BaseApp:
        """
        Get a copy of the internally stored app.

        Returns
        -------
        pydidas.core.BaseApp
            A copy of the application instance.
        """
        return self.__app.copy()

    def cycle_pre_run(self):
        """
        Perform pre-multiprocessing operations.

        This time slot is used to prepare the App by running the
        :py:meth:`app.multiprocessing_pre_run`, settings the tasks and
        starting the workers.
        """
        self.__app.multiprocessing_pre_run()
        self._processor["args"] = (
            self._mp_kwargs,
            self.__app.__class__,
            self.__app.params.copy(),
            self.__app.get_config(),
        )
        self._processor["kwargs"] = {
            "use_tasks": self._use_app_tasks,
            "app_mp_manager": self.__app.mp_manager,
        }
        self.add_tasks(self.__app.multiprocessing_get_tasks())
        self.finalize_tasks()
        self.sig_results.connect(self.__app.multiprocessing_store_results)
        self.sig_progress.connect(self.__check_progress)
        WorkerController.cycle_pre_run(self)

    def cycle_post_run(self, timeout: float = 10):
        """
        Perform the app's final operations and shut down the workers.

        Parameters
        ----------
        timeout: float
            The timeout while waiting for the worker processes.
        """
        WorkerController.cycle_post_run(self, timeout)
        self.__app.multiprocessing_post_run()
        self.sig_final_app_state.emit(self.__app.copy())
        self.sig_post_run_called.emit()
        logger.debug("AppRunner: Finished cycle post run")

    @QtCore.Slot(float)
    def __check_progress(self, progress: float):
        """
        Check the progress and finish processing if all results have been received.

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
        """
        Verify that the Thread is not actively running.
        """
        if self.flags["running"]:
            raise RuntimeError(
                "Cannot call Application methods while the"
                " Application is running. Please call .stop()"
                " on the AppRunner first."
            )

    def __check_app_method_name(self, method_name: str):
        """
        Verify the Application has a method with the given name.

        Parameters
        ----------
        method_name : str
            The name of the method.
        """
        if not hasattr(self.__app, method_name):
            raise KeyError(f"The App does not have a method with name '{method_name}'.")

    def __check_app_is_set(self):
        """
        Verify that the stored app is a BaseApp instance.
        """
        if not isinstance(self.__app, BaseApp):
            raise TypeError(
                "Application is not an instance of BaseApp. "
                "Please set application first."
            )

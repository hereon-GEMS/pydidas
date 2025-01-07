# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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
Module with the app_processor function which can be used for iterating over
multiprocessing calls to a pydidas Application.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["app_processor"]


import queue
import time
from typing import Union

from pydidas.core import BaseApp, ParameterCollection
from pydidas.core.utils import LOGGING_LEVEL, pydidas_logger


logger = pydidas_logger()


def _run_taskless_cycle(app: BaseApp, output_queue: queue.Queue) -> bool:
    app.multiprocessing_pre_cycle(-1)
    _app_carryon = app.multiprocessing_carryon()
    if _app_carryon:
        _index, _results = app.multiprocessing_func(-1)
        output_queue.put([_index, _results])
    return _app_carryon


def _wait_for_app_response(app: BaseApp, results: Union[None, object]):
    while not app.signal_processed_and_can_continue():
        time.sleep(0.005)
    if results is None:
        results = app.get_latest_results()
    return results


def app_processor(
    multiprocessing_config: dict,
    app: type,
    app_params: ParameterCollection,
    app_config: dict,
    **kwargs: dict,
):
    """
    Start a loop to process function calls on individual frames.

    This function starts a while loop to call the supplied function with
    indices supplied by the queue. Results will be written to the output
    queue in a format [input_arg, results]

    Parameters
    ----------
    multiprocessing_config : dict
        The multiprocessing configuration dictionary. It includes information
        about the logging level as well as queue objects.
    app : type
        The Application class to be called in the process. The App must have a
        multiprocessing_func method.
    app_params : ParameterCollection
        The App ParameterCollection used for creating the app.
    app_config : dict
        The dictionary which is used for overwriting the app._config
        dictionary.
    **kwargs : dict
        Supported keyword arguments are:

        wait_for_output_queue : bool, optional
            Flag to wait for the output queue to be empty before shutting down the
            worker. The default is True.
        use_tasks : bool, optional
            Flag that the app uses tasks instead of running continuously. The default
            is True.
        app_mp_manager : dict, optional
            Additional multiprocessing configuration or attributes for the
            app. The default is None.
    """
    logger.setLevel(multiprocessing_config.get("logging_level", LOGGING_LEVEL))

    _wait_for_output = kwargs.get("wait_for_output_queue", True)
    _use_tasks = kwargs.get("use_tasks", True)

    _input_queue = multiprocessing_config.get("queue_input")
    _output_queue = multiprocessing_config.get("queue_output")
    _stop_queue = multiprocessing_config.get("queue_stop")
    _finished_queue = multiprocessing_config.get("queue_finished")
    _signal_queue = multiprocessing_config.get("queue_signal")
    _io_lock = multiprocessing_config.get("lock")

    def _debug_message(msg: str):
        with _io_lock:
            logger.debug(msg)

    _debug_message("Started process")

    _app = app(app_params, clone_mode=True)
    _app._config = app_config
    _app_mp_manager = kwargs.get("app_mp_manager", None)
    if _app_mp_manager:
        _app.mp_manager = _app_mp_manager
    _app.multiprocessing_pre_run()

    _app_carryon = True
    while True:
        # check for stop signal
        try:
            _stop_queue.get_nowait()
            _debug_message("Received stop queue signal")
            _wait_for_output = False
            break
        except queue.Empty:
            pass
        # run processing step
        if _use_tasks:
            if _app_carryon:
                try:
                    _arg = _input_queue.get_nowait()
                except queue.Empty:
                    time.sleep(0.005)
                    continue
                if _arg is None:
                    _debug_message("Received queue empty signal in input queue.")
                    _output_queue.put([None, None])
                    break
                _debug_message('Received item "%s" from queue' % _arg)
                _app.multiprocessing_pre_cycle(_arg)
            _app_carryon = _app.multiprocessing_carryon()
            if _app_carryon:
                _debug_message("Starting computation of item %s" % _arg)
                _results = _app.multiprocessing_func(_arg)
                _signal = _app.must_send_signal_and_wait_for_response()
                if _signal is not None:
                    _signal_queue.put(_signal)
                    _results = _wait_for_app_response(_app, _results)
                _output_queue.put([_arg, _results])
                _debug_message("Finished computation of item %s" % _arg)
        else:
            _app_carryon = _run_taskless_cycle(_app, _output_queue)
        if not _app_carryon:
            time.sleep(0.005)
    _debug_message("Worker finished with all tasks.")

    _app_carryon = False
    while _wait_for_output and not _output_queue.empty():
        if not _app_carryon:
            _debug_message("Waiting for output queue to empty.")
            _app_carryon = True
        time.sleep(0.005)
    _debug_message("Worker shutting down.")
    _finished_queue.put(1)
    _app.deleteLater()

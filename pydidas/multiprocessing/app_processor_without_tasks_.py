# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
Module with the app_processor_without_tasks function which can be used for
iterating over multiprocessing calls to a pydidas Application without a
pre-defined task list.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["app_processor_without_tasks"]


import queue
import time
from multiprocessing import Queue

from ..core import ParameterCollection
from ..core.utils import LOGGING_LEVEL, pydidas_logger


logger = pydidas_logger()
logger.setLevel(LOGGING_LEVEL)


def app_processor_without_tasks(
    input_queue: Queue,
    output_queue: Queue,
    stop_queue: Queue,
    aborted_queue: Queue,
    app: type,
    app_params: ParameterCollection,
    app_config: dict,
    **kwargs: dict,
):
    """
    Start a loop to process function calls on individual frames.

    This function starts a while loop to call the supplied function without
    actually using the input queue (but the input queue is kept for
    compatibility). Results will be written to the output
    queue in a format [item, results]

    Parameters
    ----------
    input_queue : multiprocessing.Queue
        The input queue which supplies the processor with indices to be
        processed.
    output_queue : multiprocessing.Queue
        The queue for transmissing the results to the controlling thread.
    stop_queue : multiprocessing.Queue
        The queue for sending a termination signal to the worker.
    aborted_queue : multiprocessing.Queue
        The queue which is used by the processor to signal the calling
        thread that it has aborted its cycle.
    app : BaseApp
        The Application class to be called in the process. The App must have a
        multiprocessing_func method.
    app_params : ParameterCollection
        The App ParameterCollection used for creating the app.
    app_config : dict
        The dictionary which is used for overwriting the app._config
        dictionary.
    **kwargs : dict
        Any keyword arguments passed to the app processor.
    """
    _wait_for_output = kwargs.get("wait_for_output_queue", True)
    _app_carryon = True
    logger.debug("Started process")
    _app = app(app_params, slave_mode=True)
    logger.debug("Started app")
    _app._config = app_config
    _app.multiprocessing_pre_run()
    logger.debug("Starting processing")
    while True:
        # check for stop signal
        try:
            stop_queue.get_nowait()
            aborted_queue.put(1)
            logger.debug("Received stop queue signal")
            break
        except queue.Empty:
            pass
        # run processing
        _app.multiprocessing_pre_cycle(-1)
        _app_carryon = _app.multiprocessing_carryon()
        if _app_carryon:
            _index, _results = _app.multiprocessing_func(-1)
            output_queue.put([_index, _results])
        else:
            time.sleep(0.005)
    logger.debug("App processor finished.")
    logger.debug("Worker finished with all tasks. Waiting for output queue to empty.")
    while _wait_for_output and not output_queue.empty():
        time.sleep(0.05)
    logger.debug("Output queue empty. Worker shutting down.")

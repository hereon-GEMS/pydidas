# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["app_processor_without_tasks"]


import queue
import time

from ..core import ParameterCollection
from ..core.utils import LOGGING_LEVEL, pydidas_logger


logger = pydidas_logger()


def app_processor_without_tasks(
    multiprocessing_config: dict,
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
    multiprocessing_config : dict
        The multiprocessing configuration dictionary. It includes  information
        about the logging level as well as queue objects.
    app : BaseApp
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
        logging_level : int, optional
            The logger's logging level. The default is the pydidas default logging
            level.
    """
    _wait_for_output = kwargs.get("wait_for_output_queue", True)
    logger.setLevel(multiprocessing_config.get("logging_level", LOGGING_LEVEL))
    _input_queue = multiprocessing_config.get("queue_input")
    _output_queue = multiprocessing_config.get("queue_output")
    _stop_queue = multiprocessing_config.get("queue_stop")
    _aborted_queue = multiprocessing_config.get("queue_aborted")
    _app_carryon = True
    logger.debug("Started process")
    _app = app(app_params, slave_mode=True)
    _app._config = app_config
    _app.multiprocessing_pre_run()
    while True:
        # check for stop signal
        try:
            _stop_queue.get_nowait()
            logger.debug("Received stop queue signal")
            _aborted_queue.put(1)
            _wait_for_output = False
            break
        except queue.Empty:
            pass
        # run processing
        _app.multiprocessing_pre_cycle(-1)
        _app_carryon = _app.multiprocessing_carryon()
        if _app_carryon:
            _index, _results = _app.multiprocessing_func(-1)
            _output_queue.put([_index, _results])
        else:
            time.sleep(0.005)
    logger.debug("Worker finished with all tasks.")
    _carry_on = False
    while _wait_for_output and not _output_queue.empty():
        if not _carry_on:
            logger.debug("Waiting for output queue to empty.")
            _carry_on = True
        time.sleep(0.05)
    logger.debug("Worker shutting down.")

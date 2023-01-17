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
Module with the app_processor function which can be used for iterating over
multiprocessing calls to a pydidas Application.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["app_processor"]

import queue
import random
import string
import time

from ..core.utils import pydidas_logger, LOGGING_LEVEL


logger = pydidas_logger()
logger.setLevel(LOGGING_LEVEL)

NO_ITEM = "".join(
    random.choice(string.ascii_letters + string.digits) for i in range(64)
)


def app_processor(
    input_queue,
    output_queue,
    stop_queue,
    finished_queue,
    app,
    app_params,
    app_config,
    **kwargs,
):
    """
    Start a loop to process function calls on individual frames.

    This function starts a while loop to call the supplied function with
    indices supplied by the queue. Results will be written to the output
    queue in a format [input_arg, results]

    Parameters
    ----------
    input_queue : multiprocessing.Queue
        The input queue which supplies the processor with indices to be
        processed.
    output_queue : multiprocessing.Queue
        The queue for transmissing the results to the controlling thread.
    stop_queue : multiprocessing.Queue
        The queue for sending a termination signal to the worker.
    finished_queue : multiprocessing.Queue
        The queue which is used by the processor to signal the calling
        thread that it has finished its cycle.
    app : BaseApp
        The Application class to be called in the process. The App must have a
        multiprocessing_func method.
    app_params : ParameterCollection
        The App ParameterCollection used for creating the app.
    app_config : dict
        The dictionary which is used for overwriting the app._config
        dictionary.
    """
    _app_carryon = True
    logger.debug("Started process")
    _app = app(app_params, slave_mode=True)
    _app._config = app_config
    _app.multiprocessing_pre_run()
    while True:
        # check for stop signal
        try:
            stop_queue.get_nowait()
            break
        except queue.Empty:
            pass
        # run processing step
        if _app_carryon:
            try:
                _arg = input_queue.get_nowait()
            except queue.Empty:
                time.sleep(0.005)
                continue
            if _arg is None:
                break
            logger.debug('Received item "%s" from queue' % _arg)
            _app.multiprocessing_pre_cycle(_arg)
        _app_carryon = _app.multiprocessing_carryon()
        if _app_carryon:
            logger.debug("Starting computation")
            _results = _app.multiprocessing_func(_arg)
            logger.debug("Finished computation")
            output_queue.put([_arg, _results])
    finished_queue.put(1)

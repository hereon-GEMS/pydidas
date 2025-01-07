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
Module with the processor function which can be used for iterating over
multiprocessing function calls.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["processor"]


import queue
import time
from typing import Callable


def processor(
    function: Callable,
    multiprocessing_config: dict,
    *func_args: tuple,
    **func_kwargs: dict,
):
    """
    Start a loop to process function calls on individual frames.

    This function starts a while loop to call the supplied function with
    indices supplied by the queue. Results will be written to the output
    queue in a format [input_arg, results]

    Parameters
    ----------
    function : Callable
        The function to be called in the process. The function must accept
        the first argument from the queue and all additional arguments and
        keyword arguments from the calling arguments of processor.
    multiprocessing_config : dict
        The multiprocessing configuration dictionary. It includes information
        about the logging level as well as queue objects
    *func_args : tuple
        The function calling arguments save the first.
    **func_kwargs : dict
        The keyword arguments for the function.
    """
    input_queue = multiprocessing_config.get("queue_input")
    output_queue = multiprocessing_config.get("queue_output")
    stop_queue = multiprocessing_config.get("queue_stop")
    _finished_queue = multiprocessing_config.get("queue_finished")

    while True:
        # check for stop signal
        try:
            stop_queue.get_nowait()
            _finished_queue.put(1)
            break
        except queue.Empty:
            pass
        # run processing step
        try:
            _arg1 = input_queue.get(timeout=0.005)
            if _arg1 is None:
                output_queue.put([None, None])
                break
            try:
                _results = function(_arg1, *func_args, **func_kwargs)
            except Exception as ex:
                print(f"Exception occurred during function call to: {function}: {ex}")
                # For some arcane reason, sleep time required to stop queues from
                # becoming corrupted.
                time.sleep(0.02)
                _finished_queue.put(1)
                break
            output_queue.put([_arg1, _results])
        except queue.Empty:
            time.sleep(0.01)

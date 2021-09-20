# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Module with the processor function which can be used for iterating over
multiprocessing function calls."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['processor']

import time
import queue

def processor(input_queue, output_queue, stop_queue, finished_queue,
              function, *func_args, **func_kwargs):
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
    function : object
        The function to be called in the process. The function must accept
        the first argument from the queue and all additional arguments and
        keyword arguments from the calling arguments of processor.
    *func_args : tuple
        The function calling arguments save the first.
    **func_kwargs : dict
        The keyword arguments for the function.
    """
    while True:
        # check for stop signal
        try:
            stop_queue.get_nowait()
            break
        except queue.Empty:
            pass
        # run processing step
        try:
            _arg1 = input_queue.get(timeout=0.005)
            if _arg1 is None:
                break
            try:
                _results = function(_arg1, *func_args, **func_kwargs)
            except Exception as ex:
                print('Exception occured during function call to: '
                      f'{function}: {ex}')
                # Sleep time required to stop queues from becoming corrupted.
                time.sleep(0.02)
                break
            output_queue.put([_arg1, _results])
        except queue.Empty:
            pass
        time.sleep(0.01)
    finished_queue.put(1)

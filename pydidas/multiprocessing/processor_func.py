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
__all__ = ['processor']

import time
import queue

def processor(input_queue, output_queue, function, *func_args,
               **func_kwargs):
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
        try:
            _arg1 = input_queue.get(timeout=0.5)
            if _arg1 is None:
                break
            try:
                _results = function(_arg1, *func_args, **func_kwargs)
            except Exception as ex:
                print('Exception occured during function call to: '
                      f'{function}: {ex}')
                break
            output_queue.put([_arg1, _results])
        except queue.Empty:
            pass
        time.sleep(0.01)

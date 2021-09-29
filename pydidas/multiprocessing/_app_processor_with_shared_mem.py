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
__all__ = ['app_processor_with_shared_mem']


import queue
import random
import string
import time

from numpy import frombuffer, float32, uint16


NO_ITEM = ''.join(random.choice(string.ascii_letters + string.digits)
                  for i in range(64))


def app_processor_with_shared_mem(queues, shared_memory, app,
                                  app_params, app_config):
    """
    Start a loop to process function calls on individual frames.

    This function starts a while loop to call the supplied function with
    indices supplied by the queue. Results will be written to the output
    queue in a format [input_arg, results]

    Parameters
    ----------
    queues : tuple
        queues must be a tuple of exactly four multiprocessingQueues:
        - input_queue : The input queue which supplies the processor with
                        indices to be processed.
        - output_queue : The queue for transmissing the results to the
                         controlling thread.
        -  stop_queue : The queue for sending a termination signal to the
                        worker.
        - finished_queue : The queue which is used by the processor to signal
                           the calling thread that it has finished its cycle.
    shared_memory : tuple
        shared_memory is a tuple with information about the shared_memory used
        for transporting results between processes. It must consist of the
        following four entries:
        - mp_data_array : The multiprocessing.Array instance which is used
                          to create the local buffered numpy arrays.
        - array_shape : The shape of mp_data_array to set up the numpy array
                        in the correct shape.
        - mp_index_array : The multiprocessing.Array instance which holds the
                           the array which is used to specify the indexes in
                           which data is buffered.
    app : BaseApp
        The Application class to be called in the process. The App must have a
        multiprocessing_func method.
    app_params : ParameterCollection
        The App ParameterCollection used for creating the app.
    app_config : dict
        The dictionary which is used for overwriting the app._config
        dictionary.
    """
    input_queue, output_queue, stop_queue, finished_queue = queues
    _mp_data_array, _data_shape, _mp_index_arr = shared_memory
    _array = frombuffer(_mp_data_array.get_obj(),
                        dtype=float32).reshape(_data_shape)
    _index_flags = frombuffer(_mp_index_arr.get_obj(), dtype=uint16)

    _carryon_cycle = True
    _app = app(app_params)
    _app.slave_mode = True
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
        if _carryon_cycle:
            try:
                _arg = input_queue.get(timeout=0.01)
            except queue.Empty:
                _arg = NO_ITEM
        if _arg is None:
            break
        if _arg is not NO_ITEM:
            _app.multiprocessing_pre_cycle(_arg)
            _carryon_cycle = _app.multiprocessing_carryon()
            if _carryon_cycle:
                _results = _app.multiprocessing_func(_arg)
                output_queue.put([_arg, _results.copy()])
        time.sleep(0.005)
    finished_queue.put(1)

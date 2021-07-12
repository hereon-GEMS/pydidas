# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""Module with the processor function which can be used for iterating over
multiprocessing function calls."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['app_processor']


import queue
import random
import string

NO_ITEM = ''.join(random.choice(string.ascii_letters + string.digits)
                  for i in range(64))


def app_processor(input_queue, output_queue, stop_queue, app, app_params,
                  app_config):
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
    _app = app(app_params)
    _app.slave_mode = True
    _app._config = app_config
    _app.multiprocessing_pre_run()
    while True:
        # check for stop signal
        try:
            stop_queue.get_nowait()
            return
        except queue.Empty:
            pass
        # run processing step
        if _app_carryon:
            try:
                _arg = input_queue.get(timeout=0.01)
                if _arg is None:
                    return
            except queue.Empty:
                _arg = NO_ITEM
        if _arg is not NO_ITEM:
            _app.multiprocessing_pre_cycle(_arg)
            _app_carryon = _app.multiprocessing_carryon()
            if _app_carryon:
                _results = _app.multiprocessing_func(_arg)
                output_queue.put([_arg, _results])

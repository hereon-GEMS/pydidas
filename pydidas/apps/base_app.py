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

"""Module with the BaseApp from which all apps should inherit.."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['BaseApp']


import copy

from pydidas.core import ObjectWithParameterCollection


class BaseApp(ObjectWithParameterCollection):
    """
    The BaseApp.

    TO DO
    """
    def __init__(self, *args, **kwargs):
        """
        Create a Base instance.

        Parameters
        ----------
        *args : list
            Any arguments. Defined by the concrete
            implementation of the app.
        **kwargs : dict
            A dictionary of keyword arguments. Defined by the concrete
            implementation of the app.

        Returns
        -------
        None.
        """
        super().__init__()
        self.add_params(*args, **kwargs)
        self._config = {}

    def run(self):
        """
        Run the app without multiprocessing.
        """
        self.multiprocessing_pre_run()
        tasks = self.multiprocessing_get_tasks()
        for task in tasks:
            _results = self.multiprocessing_func(task)
            self.multiprocessing_store_results(*_results)
        self.multiprocessing_post_run()

    def multiprocessing_pre_run(self):
        """
        Perform operations prior to running main parallel processing function.
        """
        raise NotImplementedError

    def multiprocessing_post_run(self):
        """
        Perform operatinos after running main parallel processing function.
        """
        raise NotImplementedError

    def multiprocessing_get_tasks(self):
        """
        Return all tasks required in multiprocessing.
        """
        raise NotImplementedError

    def multiprocessing_func(self, *args):
        """
        Perform key operation with parallel processing.
        """
        raise NotImplementedError

    def multiprocessing_store_results(self, *args):
        """
        Store the results of the multiprocessing operation.
        """
        raise NotImplementedError

    def get_config(self):
        """
        Get the App configuration.

        Returns
        -------
        dict
            The App configuration stored in the _config dictionary.
        """
        return copy.copy(self._config)

    def copy(self):
        """
        Get a copy of the App.

        Returns
        -------
        App : BaseApp
            A copy of the App instance.
        """
        return copy.copy(self)

    def __copy__(self):
        _obj_copy = type(self)()
        for _key in self.__dict__:
            _obj_copy.__dict__[_key] = copy.copy(self.__dict__[_key])
        return _obj_copy

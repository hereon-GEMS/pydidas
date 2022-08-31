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
Module with the BaseApp class from which all apps should inherit.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["BaseApp"]

from copy import copy

from .parameter_collection import ParameterCollection
from .object_with_parameter_collection import ObjectWithParameterCollection


class BaseApp(ObjectWithParameterCollection):
    """
    The BaseApp is the base class for all pydidas applications. It includes
    core functionalities and pre-defines the template of required methods
    for Apps to allow running the multiprocessing
    :py:class:`pydidas.multiprocessing.AppRunner`.

    Parameters
    ----------
    *args : list
        Any arguments. Defined by the concrete
        implementation of the app.
    **kwargs : dict
        A dictionary of keyword arguments. Defined by the concrete
        implementation of the app.
    """

    default_params = ParameterCollection()
    parse_func = lambda self: {}
    attributes_not_to_copy_to_slave_app = []

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.slave_mode = kwargs.get("slave_mode", False)
        if "slave_mode" in kwargs:
            del kwargs["slave_mode"]
        self.add_params(*args, **kwargs)
        self._config = {}
        self.set_default_params()
        self.parse_args_and_set_params()

    def parse_args_and_set_params(self):
        """
        Parse the command line arguments and update the corresponding
        Parameter values.
        """
        if self.parse_func is None:
            return
        _cmdline_args = self.parse_func()
        for _key in self.params:
            if _key in _cmdline_args and _cmdline_args[_key] is not None:
                self.params.set_value(_key, _cmdline_args[_key])

    def run(self):
        """
        Run the app without multiprocessing.
        """
        self.multiprocessing_pre_run()
        tasks = self.multiprocessing_get_tasks()
        for task in tasks:
            self.multiprocessing_pre_cycle(task)
            _carryon = self.multiprocessing_carryon()
            if _carryon:
                _results = self.multiprocessing_func(task)
                self.multiprocessing_store_results(task, _results)
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

    def multiprocessing_pre_cycle(self, index):
        """
        Perform operations in the pre-cycle of every task.
        """
        return

    def multiprocessing_func(self, index):
        """
        Perform key operation with parallel processing.
        """
        raise NotImplementedError

    def multiprocessing_carryon(self):
        """
        Wait for specific tasks to give the clear signal.

        This method is called in the parallel multiprocessing process
        prior to the actual calculation. Apps can specify wait conditions
        that need to be fulfilled before carrying on. The method returns
        a boolean flag whether a timeout was encountered.

        Returns
        -------
        bool
            Flag whether processing can continue or should wait.
        """
        return True

    def multiprocessing_store_results(self, index, *args):
        """
        Store the multiprocessing results for other pydidas apps and processes.

        Parameters
        ----------
        index : int
            The frame index
        args : object
            The results. The specific type depends on the app.
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
        return copy(self._config)

    def get_copy(self, slave_mode=False):
        """
        Get a copy of the App.

        Parameters
        ----------
        slave_mode : bool, optional
            Keyword to toggle creation of a slave app which does not include
            attributes marked in the classes slave_mode attribute.

        Returns
        -------
        App : BaseApp
            A copy of the App instance.
        """
        return self.__copy__(slave_mode)

    def __copy__(self, slave_mode=False):
        _do_not_copy = self.attributes_not_to_copy_to_slave_app
        _obj_copy = type(self)()
        for _key in self.__dict__:
            if not (slave_mode and _key in _do_not_copy):
                _obj_copy.__dict__[_key] = copy(self.__dict__[_key])
        if slave_mode:
            _obj_copy.slave_mode = True
        return _obj_copy

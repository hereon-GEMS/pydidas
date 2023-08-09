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
Module with the BaseApp class from which all Pydidas apps should inherit.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["BaseApp"]


from copy import copy
from pathlib import Path
from typing import Self

from qtpy import QtCore

from .object_with_parameter_collection import ObjectWithParameterCollection
from .parameter_collection import ParameterCollection


class BaseApp(ObjectWithParameterCollection):
    """
    The BaseApp is the base class for all pydidas applications.

    It includes core functionalities and pre-defines the template of required methods
    for Apps to allow running the multiprocessing
    :py:class:`pydidas.multiprocessing.AppRunner`.

    Parameters
    ----------
    *args : tuple
        Any arguments. Defined by the concrete implementation of the app.
    **kwargs : dict
        A dictionary of keyword arguments. Defined by the concrete
        implementation of the app.
    """

    default_params = ParameterCollection()
    parse_func = lambda self: {}
    attributes_not_to_copy_to_slave_app = []

    def __init__(self, *args: tuple, **kwargs: dict):
        super().__init__()
        self.slave_mode = kwargs.get("slave_mode", False)
        if "slave_mode" in kwargs:
            del kwargs["slave_mode"]
        self.add_params(*args)
        self._config = {}
        self.set_default_params()
        self.update_param_values_from_kwargs(**kwargs)
        self.parse_args_and_set_params()

    def parse_args_and_set_params(self):
        """
        Parse the command line arguments and update the corresponding Parameter values.
        """
        if self.parse_func is None:
            return
        _cmdline_args = self.parse_func()
        for _key in self.params:
            if _key in _cmdline_args and _cmdline_args[_key] is not None:
                self.params.set_value(_key, _cmdline_args[_key])

    def run(self):
        """
        Run the app serially without multiprocessing support.
        """
        self.multiprocessing_pre_run()
        tasks = self.multiprocessing_get_tasks()
        for task in tasks:
            self.multiprocessing_pre_cycle(task)
            while True:
                _carryon = self.multiprocessing_carryon()
                if _carryon:
                    _results = self.multiprocessing_func(task)
                    self.multiprocessing_store_results(task, _results)
                    break
        self.multiprocessing_post_run()

    def multiprocessing_pre_run(self):
        """
        Perform operations prior to running main parallel processing function.
        """
        return

    def multiprocessing_post_run(self):
        """
        Perform operations after running main parallel processing function.
        """
        return

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

    def multiprocessing_carryon(self) -> bool:
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

    def multiprocessing_store_results(self, index: int, *args: tuple):
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

    def get_config(self) -> dict:
        """
        Get the App configuration.

        Returns
        -------
        dict
            The App configuration stored in the _config dictionary.
        """
        return copy(self._config)

    def export_state(self) -> dict:
        """
        Get the sanitized app Parameters and configuration for export.

        Returns
        -------
        dict
            The state dictionary.
        """
        _cfg = self.get_config()
        _newcfg = {}
        for _key, _item in self._config.items():
            if isinstance(_item, range):
                _newcfg[_key] = f"::range::{_item.start}::{_item.stop}::{_item.step}"
            if isinstance(_item, slice):
                _newcfg[_key] = f"::slice::{_item.start}::{_item.stop}::{_item.step}"
            if isinstance(_item, Path):
                _newcfg[_key] = str(_item)
            if _key in ["scan_context", "exp_context"]:
                _newcfg[_key] = "::None::"
        _cfg.update(_newcfg)
        if "shared_memory" in _cfg and _cfg["shared_memory"] != {}:
            _cfg["shared_memory"] = "::restore::True"
        return {
            "params": self.get_param_values_as_dict(filter_types_for_export=True),
            "config": _cfg,
        }

    def import_state(self, state: dict):
        """
        Import a stored state including Parameters and configuration.

        Parameters
        ----------
        state : dict
            The stored state.
        """
        for _key, _val in state["params"].items():
            self.set_param_value(_key, _val)
        _newcfg = {}
        for _key, _item in state["config"].items():
            if not isinstance(_item, str):
                continue
            if _item.startswith("::range::") or _item.startswith("::slice::"):
                _, _, _start, _stop, _step = _item.split("::")
                _start = None if _start == "None" else int(_start)
                _stop = None if _stop == "None" else int(_stop)
                _step = None if _step == "None" else int(_step)
            if _item.startswith("::range::"):
                _newcfg[_key] = range(_start, _stop, _step)
            if _item.startswith("::slice::"):
                _newcfg[_key] = slice(_start, _stop, _step)
            if _item == "::None::":
                _newcfg[_key] = None
        self._config = state["config"] | _newcfg
        if self._config.get("shared_memory", False) == "::restore::True":
            self._config["shared_memory"] = {}
            self.initialize_shared_memory()

    def initialize_shared_memory(self):
        """
        Initialize the shared memory array for the master app.

        Note: This method is not required for apps without a shared memory.
        """
        return

    def copy(self, slave_mode: bool = False) -> Self:
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

    def __copy__(self, slave_mode: bool = False) -> Self:
        """
        Reimplement the generic copy method.

        Parameters
        ----------
        slave_mode : bool, optional
            Flag to signal the copy shall be a slave. The default is False.

        Returns
        -------
        BaseApp
            The copy of the app.
        """
        _obj_copy = type(self)()
        _obj_copy.__dict__ = {
            _key: copy(_value)
            for _key, _value in self.__dict__.items()
            if not (
                isinstance(_value, QtCore.SignalInstance)
                or (slave_mode and _key in self.attributes_not_to_copy_to_slave_app)
            )
        }
        if slave_mode:
            _obj_copy.slave_mode = True
        return _obj_copy

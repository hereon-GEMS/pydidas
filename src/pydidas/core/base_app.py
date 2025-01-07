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
Module with the BaseApp class from which all Pydidas apps should inherit.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["BaseApp"]


import multiprocessing as mp
from copy import copy
from pathlib import Path
from typing import Optional, Self

from qtpy import QtCore

from pydidas.core.object_with_parameter_collection import ObjectWithParameterCollection
from pydidas.core.parameter_collection import ParameterCollection


_TYPES_NOT_TO_COPY = (QtCore.SignalInstance, QtCore.QMetaObject, ParameterCollection)
_KEYS_NOT_TO_COPY = ["__METAOBJECT__", "mp_manager", "_locals", "params", "clone_mode"]


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
    parse_func = lambda self: {}  # noqa E731
    attributes_not_to_copy_to_app_clone = ["_mp_manager_instance"]

    def __init__(self, *args: tuple, **kwargs: dict):
        self.clone_mode = kwargs.pop("clone_mode", False)
        ObjectWithParameterCollection.__init__(self)
        self.update_params_from_init(*args, **kwargs)
        self.parse_args_and_set_params()
        self._config["run_prepared"] = False
        self.mp_manager = {}
        self._mp_manager_instance = None

    def parse_args_and_set_params(self):
        """
        Parse the command line arguments and update the corresponding Parameter values.
        """
        if self.parse_func is None:
            return
        _cmdline_args = self.parse_func()
        for _key, _value in _cmdline_args.items():
            if _key in self.params and _value is not None:
                self.params.set_value(_key, _value)

    def deleteLater(self):
        """
        Overwrite the deleteLater method to ensure proper cleanup.

        This method is called by the Qt event loop to delete the app instance.
        """
        if isinstance(self._mp_manager_instance, mp.managers.SyncManager):
            self._mp_manager_instance.shutdown()
        super().deleteLater()

    def must_send_signal_and_wait_for_response(self) -> Optional[str]:
        """
        Check whether the app must send a signal and wait for a response.

        If a signal is required, the method returns the string of the signal to
        send through the multiprocessing signal queue. If no signal is required,
        the method returns None.

        Returns
        -------
        str or None
            The signal to send or None.
        """
        return None

    def signal_processed_and_can_continue(self) -> bool:
        """
        Check whether the app's signal was processed and the app can continue.

        Returns
        -------
        bool
            Flag whether the app can continue processing.
        """
        return True

    def get_latest_results(self) -> Optional[object]:
        """
        Get the latest results from the app.

        Note that the app must store results in the `latest_results` key
        of the config dictionary to be able to retrieve them.

        Returns
        -------
        object or None
            The latest results or None.
        """
        return self._config.get("latest_results", None)

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

        The generic method simple performs no operation and subclasses only
        need to re-implement it when they explicitly need it.
        """
        self._config["run_prepared"] = True

    def prepare_run(self):
        """
        Prepare running the app. This is a wrapper for multiprocessing_pre_run.
        """
        self.multiprocessing_pre_run()

    @QtCore.Slot()
    def multiprocessing_post_run(self):
        """
        Perform operations after running main parallel processing function.

        The generic method simple performs no operation and subclasses only
        need to re-implement it when they explicitly need it.
        """
        return

    def multiprocessing_get_tasks(self):
        """
        Return all tasks required in multiprocessing.

        This method must be implemented by the BaseApp subclasses.
        """
        raise NotImplementedError

    def multiprocessing_pre_cycle(self, index: int):
        """
        Perform operations in the pre-cycle of every task.

        The generic method simple performs no operation and subclasses only
        need to re-implement it when they explicitly need it.

        Parameters
        ----------
        index : int
            The index to be processed.
        """
        return

    def multiprocessing_func(self, index: int):
        """
        Perform key operation with parallel processing.

        This method must be implemented by the BaseApp subclasses.

        Parameters
        ----------
        index : int
            The index to be processed.
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

        This method must be implemented by the BaseApp subclasses.


        Parameters
        ----------
        index : int
            The frame index
        args : tuple
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
        _new_cfg = {}
        for _key, _item in self._config.items():
            if isinstance(_item, range):
                _new_cfg[_key] = f"::range::{_item.start}::{_item.stop}::{_item.step}"
            if isinstance(_item, slice):
                _new_cfg[_key] = f"::slice::{_item.start}::{_item.stop}::{_item.step}"
            if isinstance(_item, Path):
                _new_cfg[_key] = str(_item)
            if _key in ["scan_context", "exp_context"]:
                _new_cfg[_key] = "::None::"
        _cfg.update(_new_cfg)
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
        _new_cfg = {}
        for _key, _item in state["config"].items():
            if not isinstance(_item, str):
                continue
            if _item.startswith("::range::") or _item.startswith("::slice::"):
                _, _, _start, _stop, _step = _item.split("::")
                _start = None if _start == "None" else int(_start)
                _stop = None if _stop == "None" else int(_stop)
                _step = None if _step == "None" else int(_step)
            if _item.startswith("::range::"):
                _new_cfg[_key] = range(_start, _stop, _step)
            if _item.startswith("::slice::"):
                _new_cfg[_key] = slice(_start, _stop, _step)
            if _item == "::None::":
                _new_cfg[_key] = None
        self._config = state["config"] | _new_cfg

    def copy(self, clone_mode: bool = False) -> Self:
        """
        Get a copy of the App.

        Parameters
        ----------
        clone_mode : bool, optional
            Keyword to toggle creation of an app clone which does not include
            attributes marked in the classes clone_mode attribute.

        Returns
        -------
        App : BaseApp
            A copy of the App instance.
        """
        return self.__copy__(clone_mode)

    def __copy__(self, clone_mode: bool = False) -> Self:
        """
        Reimplement the generic copy method.

        Parameters
        ----------
        clone_mode : bool, optional
            Flag to signal the copy shall be a clone. The default is False.

        Returns
        -------
        BaseApp
            The copy of the app.
        """
        _obj_copy = type(self)(clone_mode=clone_mode)
        _obj_copy.__dict__.update(
            {
                _key: copy(_value)
                for _key, _value in self.__dict__.items()
                if not (
                    isinstance(_value, _TYPES_NOT_TO_COPY)
                    or _key in _KEYS_NOT_TO_COPY
                    or (clone_mode and _key in self.attributes_not_to_copy_to_app_clone)
                )
            }
        )
        for _key, _param in self.params.items():
            _obj_copy.set_param_value(_key, _param.value)
        if hasattr(self, "mp_manager"):
            _obj_copy.mp_manager = {k: v for k, v in self.mp_manager.items()}
        return _obj_copy

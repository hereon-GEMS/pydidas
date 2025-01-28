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
Module with the FitFuncMeta class which is used for creating fit function classes.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["FitFuncMeta"]


from typing import TypeVar


FitFuncBase = TypeVar("FitFuncBase")


class FitFuncMeta(type):
    """
    Metaclass for fitting functions to store them in a registry.
    """

    registry = {}

    def __new__(mcls, cls_name: str, bases: tuple, attrs: dict):
        """
        Call the class' __new__ method and register the class with the registry.

        Parameters
        ----------
        mcls : type
            The new class.
        cls_name : str
            The name of the new class
        bases : tuple
            The list of class bases.
        attrs : dict
            The class attributes.

        Returns
        -------
        type
            The new class.
        """
        _new_class = super(FitFuncMeta, mcls).__new__(mcls, cls_name, bases, attrs)
        mcls.register_class(_new_class)
        return _new_class

    @classmethod
    def clear_registry(mcls):
        """
        Clear the registry and remove all items.
        """
        mcls.registry = {}

    @classmethod
    def register_class(mcls, new_class: FitFuncBase, update_registry: bool = False):
        """
        Register a fit function class.

        Parameters
        ----------
        new_class : FitFuncBase
            The class to be registered.
        update_registry : bool, optional
            Keyword to allow updating / overwriting of registered extensions.
            The default is False.

        Raises
        ------
        KeyError
            If an extension associated with new_class has already been
            registered and update_registry is False.
        """
        _name = new_class.name
        if _name == "base fit function":
            return
        if _name in mcls.registry and not update_registry:
            raise KeyError(
                f"A fitting function with the name '{_name}' is already registered."
            )
        mcls.registry[_name] = new_class

    @classmethod
    def get_fitter(mcls, name: str) -> FitFuncBase:
        """
        Get the fit function class referenced by given name.

        Parameters
        ----------
        name : str
            The functions reference name.

        Returns
        -------
        FitFuncBase
            The fitter class.
        """
        return mcls.registry[name]

    @classmethod
    def get_fitter_names_with_num_peaks(mcls, num_peaks: int) -> tuple[str]:
        """
        Get the names of all FitFuncBase classes with the given number of peaks.

        Parameters
        ----------
        num_peaks : int
            The number of peaks.

        Returns
        -------
        tuple[str]
            The tuple with the names of the FitFuncBase classes that have registered
            with the given number of peaks.
        """
        return tuple(
            _key
            for _key, _class in mcls.registry.items()
            if _class.num_peaks == num_peaks
        )

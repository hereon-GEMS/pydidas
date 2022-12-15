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
Module with the FitFuncMeta class which is used for creating fit function classes.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["FitFuncMeta"]


class FitFuncMeta(type):
    """
    Metaclass for fitting functions to store them in a registry.
    """

    registry = {}

    def __new__(cls, clsname, bases, attrs):
        """
        Call the class' (i.e. the WorkflowTree exporter) __new__ method
        and register the class with the registry.

        Parameters
        ----------
        cls : type
            The new class.
        clsname : str
            The name of the new class
        bases : list
            The list of class bases.
        attrs : dict
            The class attributes.

        Returns
        -------
        type
            The new class.
        """
        _new_class = super(FitFuncMeta, cls).__new__(cls, clsname, bases, attrs)
        cls.register_class(_new_class)
        return _new_class

    @classmethod
    def clear_registry(cls):
        """
        Clear the registry and remove all items.
        """
        cls.registry = {}

    @classmethod
    def register_class(cls, new_class, update_registry=False):
        """
        Register a fit function class.

        Parameters
        ----------
        new_class : type
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
        _name = new_class.func_name
        if _name in cls.registry and not update_registry:
            raise KeyError(
                "A fitting function with the name '{_name}' is already registered."
            )
        cls.registry[_name] = new_class

    @classmethod
    def get_fitter(cls, name):
        """
        Get the fit function class referenced by given name.

        Parameters
        ----------
        name : str
            The functions reference name.

        Returns
        -------
        type
            The fitter class.
        """
        return cls.registry[name]

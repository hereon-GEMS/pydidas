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

from PyQt5 import QtCore

from pydidas.core import Parameter, ParameterCollection


class BaseApp(QtCore.QObject):
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
        self.params = ParameterCollection(*args, **kwargs)

    def set_default_params(self, defaults):
        """
        Set default entries.

        This method will go through the supplied defaults iterable
        if there are no entries for the default re

        Parameters
        ----------
        defaults : Union[dict, ParameterCollection, list, tuple, set]
            An iterable with default Parameters.

        Returns
        -------
        None.
        """
        if isinstance(defaults, (dict, ParameterCollection)):
            defaults = defaults.values()
        for param in defaults:
            if param.refkey not in self.params:
                self.params.add_parameter(param)


    def run(self, *args, **kwargs):
        """
        Run the app.
        """
        raise NotImplementedError

    def get_param_value(self, param_name):
        """
        Get a parameter value.

        Parameters
        ----------
        param_name : str
            The key name of the Parameter.

        Returns
        -------
        object
            The value of the Parameter.
        """
        if not param_name in self.params:
            raise KeyError(f'No parameter with the name "{param_name}" '
                           'has been registered.')
        return self.params.get_value(param_name)

    def set_param_value(self, param_name, value):
        """
        Set a parameter value.

        Parameters
        ----------
        param_name : str
            The key name of the Parameter.
        value : *
            The value to be set. This has to be the datatype associated with
            the Parameter.

        Returns
        -------
        None
        """
        if not param_name in self.params:
            raise KeyError(f'No parameter with the name "{param_name}" '
                           'has been registered.')
        self.params.set_value(param_name, value)

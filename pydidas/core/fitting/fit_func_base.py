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
Module with the FitFuncBase class which all fitting functions should inherit from.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["FitFuncBase"]


class FitFuncBase:
    """
    Base class for fit functinos
    """

    func_name = "base fit function"
    param_bounds_low = []
    param_bounds_high = []
    param_labels = []

    @classmethod
    def guess_fit_start_params(cls, x, y):
        """
        Guess the start params for the fit for the given x and y values.

        Parameters
        ----------
        x : nd.ndarray
            The x points of the data.
        y : np.ndarray
            The data values.
        """
        return []

    @classmethod
    def function(cls, c, x):
        """
        The fitting function.

        Parameters
        ----------
        c : tuple
            The function parameters.
        x : np.ndarray
            The x points to compute the function values.

        Returns
        -------
        np.ndarray
            The function values at the positions x.
        """
        return x

    @classmethod
    def delta(cls, c, x, data):
        """
        Get the difference between the fit and the data.

        Parameters
        ----------
        c : tuple
            the tuple with the function parameters
        x : np.ndarray
            The x points to calculate the function values.
        data : np.ndarray
            The data values.

        Returns
        -------
        np.ndarray
            The difference of function - data
        """
        return cls.function(c, x) - data

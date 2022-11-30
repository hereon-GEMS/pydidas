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
Module with the Timer class which allows to time code running and print
the code runtime to the console.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["Timer", "TimerSaveRuntime"]

import time


class Timer:
    """
    The Timer class can be used to time running code.

    Is it designed to be used in a "with Timer():" statement.

    Example
    -------
    >>> with Timer():
    >>>     arr = numpy.random.random((1000, 1000, 100))
    Code runtime is 0.597181800 seconds.
    """

    def __init__(self, msg=None):
        self._tstart = None
        self._msg = msg

    def __enter__(self):
        self._tstart = time.perf_counter()

    def __exit__(self, type_, value, traceback):
        _delta = time.perf_counter() - self._tstart
        _str = f"Code runtime is {_delta:0.9f} seconds."
        if self._msg is not None:
            _str = f"{self._msg}: {_str}"
        print(_str)


class TimerSaveRuntime:
    """
    The TimerSaveRuntime class can be used to time running code and save the result
    to a variable.

    Is it designed to be used in a "with TimerSaveRuntime() as var:" statement.

    Example
    -------
    >>> with TimerSaveRuntime as runtime:
    >>>     arr = numpy.random.random((1000, 1000, 100))
    >>> print(runtime())
    0.597181800
    """

    def __init__(self):
        self._tstart = 0
        self._tend = 0

    def __enter__(self):
        self._tstart = time.perf_counter()
        return lambda: self._tend - self._tstart

    def __exit__(self, type_, value, traceback):
        self._tend = time.perf_counter()

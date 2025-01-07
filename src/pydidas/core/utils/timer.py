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
The Timer context manager allows to time and print code runtimes.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["Timer", "TimerSaveRuntime"]


import time


class Timer:
    """
    The Timer class can be used to time running code and print results.

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
        """Start the context manager."""
        self._tstart = time.perf_counter()

    def __exit__(self, type_, value, traceback):
        """Exit the context manager."""
        _delta = time.perf_counter() - self._tstart
        _str = f"Code runtime is {_delta:0.9f} seconds."
        if self._msg is not None:
            _str = f"{self._msg}: {_str}"
        print(_str)


class TimerSaveRuntime:
    """
    The TimerSaveRuntime context manager can be used to time code runtime.

    When running code with this context manager, the runtime can be accessed
    through a call to the context manager after running it.

    Is it designed to be used in a "with TimerSaveRuntime() as var:" statement.

    Example
    -------
    >>> with TimerSaveRuntime() as runtime:
    >>>     arr = numpy.random.random((1000, 1000, 100))
    >>> print(runtime())
    0.597181800
    """

    def __init__(self):
        self._tstart = 0
        self._tend = 0

    def __enter__(self) -> object:
        """Start the context manager."""
        self._tstart = time.perf_counter()
        return self

    def __exit__(self, type_, value, traceback):
        """Exit the context manager."""
        self._tend = time.perf_counter()

    def __call__(self) -> float:
        """Return the runtime."""
        return self.runtime

    @property
    def runtime(self) -> float:
        """
        Return the runtime.

        Returns
        -------
        float
            The runtime of the code block.
        """
        return self._tend - self._tstart

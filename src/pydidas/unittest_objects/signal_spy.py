# This file is part of pydidas.
#
# Copyright 2025, Helmholtz-Zentrum Hereon
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
The signal_spy module has a convenience class to spy on Qt signals during tests.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["SignalSpy"]


from typing import Any

from qtpy import QtTest

from pydidas.core.utils.qt_utilities import IS_QT6


class SignalSpy(QtTest.QSignalSpy):
    """
    A convenience subclass of QSignalSpy with an added method to get results.

    This class extends QSignalSpy by adding a method to retrieve the results
    in a way that is compatible with both Qt5 and Qt6.
    """

    @property
    def results(self) -> list[Any]:
        """
        Get the results of the signal spy.

        Returns
        -------
        list[Any]
            A list of the signal emissions captured by the spy.
        """
        if IS_QT6:
            return [self.at(i) for i in range(self.count())]
        return [self[i] for i in range(len(self))]

    @property
    def n(self) -> int:
        """
        Get the number of times the signal was emitted.

        Returns
        -------
        int
            The count of signal emissions.
        """
        return len(self.results)

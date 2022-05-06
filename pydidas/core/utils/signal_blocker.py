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
Module with the SignalBlocker class which allows to perform Qt operations
with all Qt signals blocked for the specified object.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["SignalBlocker"]


from qtpy import QtCore


class SignalBlocker:
    """
    The SignalBlocker class can be used to perform Qt operations
    with all Qt signals blocked for the specified object.

    Is it designed to be used in a "with SignalBlocker(object):" statement.

    Example
    -------
    >>> obj = QtWidgets.QComboBox()
    >>> with SignalBlocker(obj):
    >>>     obj.setCurrentText('Test')
    """

    def __init__(self, obj):
        if not isinstance(obj, QtCore.QObject):
            raise TypeError("SignalBlocker can only be used with QObjects.")
        self.obj = obj
        self._blocked = obj.signalsBlocked()

    def __enter__(self):
        self.obj.blockSignals(True)

    def __exit__(self, type_, value, traceback):
        self.obj.blockSignals(self._blocked)

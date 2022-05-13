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
Module with a function to get the pydidas logging directory.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["get_logging_dir"]

import os

from qtpy import QtCore


def get_logging_dir():
    """
    Return the pydidas logging directory.

    Returns
    -------
    str
        The path to the pydidas module.
    """
    _docs_path = QtCore.QStandardPaths.standardLocations(
        QtCore.QStandardPaths.DocumentsLocation
    )[0]
    _log_path = os.path.join(_docs_path, "pydidas", "logs")
    if not os.path.exists(_log_path):
        os.makedirs(_log_path)
    return _log_path

# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
The Hdf5key is a subclassed string to have a unique identifier for Hdf5 dataset
keys.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["Hdf5key", "NXdataKey"]


class Hdf5key(str):
    """
    A class used for referencing keys to HDF5 datasets.

    Inherits from :py:class:`str`. This class is only used for type-checking
    Parameters.
    """


class NXdataKey(str):
    """
    A class used for referencing keys to NXdata datasets.

    Inherits from :py:class:`str`. This class is only used for type-checking
    Parameters.
    """

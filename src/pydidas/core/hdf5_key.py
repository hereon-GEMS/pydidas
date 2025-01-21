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
The Hdf5key is a subclassed string to have a unique identifier for Hdf5 dataset
keys.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["Hdf5key"]


from pathlib import Path
from typing import Union


class Hdf5key(str):
    """
    Inherits from :py:class:`str`.

    A class used for referencing hdf5 keys.
    """

    def __new__(cls, text: str):
        _instance = super().__new__(cls, text)
        _instance.__hdf_fname = None
        return _instance

    @property
    def hdf5_filename(self) -> Path:
        """
        Get the filename of the associated hdf5 file.

        Returns
        -------
        str
            The filename of the associated hdf5 file.
        """
        return self.__hdf_fname

    @hdf5_filename.setter
    def hdf5_filename(self, txt: Union[str, Path]):
        """
        Set the hdf_filename property.

        Parameters
        ----------
        txt : str
            The filename (and path) to the hdf5 file.
        """
        if type(txt) not in (str, Path):
            raise TypeError(
                "`hdf5_filename` property must be of type str or pathlib.Path."
            )
        self.__hdf_fname = Path(txt)

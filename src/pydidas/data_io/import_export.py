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
The import_export module includes wrappers to facilitate the import and export
of data using the pydidas.data_io.IoManager metaclass.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["import_data", "export_data"]


from pathlib import Path
from typing import Union

from numpy import ndarray

from pydidas.core import Dataset
from pydidas.data_io.io_manager import IoManager


def export_data(filename: Union[str, Path], data: ndarray, **kwargs: dict):
    """
    Export data to a file using the pydidas.data_io.IoManager metaclass.

    Parameters
    ----------
    filename : Union[str, pathlib.Path]
        The filename to be used for the exported data.
    data : Union[np.ndarray, pydidas.core.Dataset]
        The data to be exported.
    **kwargs : dict
        Any keyword arguments. These will be passed to the implemented exporter
        and the supported keywords vary depending on the selected file
        extension.
    """
    IoManager.export_to_file(filename, data, **kwargs)


def import_data(filename: Union[str, Path], **kwargs: dict) -> Dataset:
    """
    Import data from a file using the pydidas.data_io.IoManager metaclass.

    Parameters
    ----------
    filename : Union[str, pathlib.Path]
        The filename to be used for the exported data.
    **kwargs : dict
        Any keyword arguments. These will be passed to the implemented importer
        and the supported keywords vary depending on the selected file
        extension.
    """
    _data = IoManager.import_from_file(filename, **kwargs)
    return _data

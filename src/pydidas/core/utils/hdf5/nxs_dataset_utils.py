# This file is part of pydidas.
#
# Copyright 2026, Helmholtz-Zentrum Hereon
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
Module with utility functions for NeXus data files.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "check_nxdata_adherence",
]


from pathlib import Path, PurePosixPath
from typing import NoReturn

import h5py

from pydidas.core.exceptions import UserConfigError


def check_nxdata_adherence(filename: str | Path, dataset: str) -> None | NoReturn:
    """
    Check that the selected dataset in the given file adheres to the NXdata definition.

    This function will raise a UserConfigError if the dataset cannot be read
    or does not adhere to the NXdata definition.

    Parameters
    ----------
    filename : str or Path
            The filename and path to the HDF5 file to be checked.
    dataset : str
            The dataset key to be checked for adherence to the NXdata definition.
    """
    filename = Path(filename)
    if not filename.is_file():
        raise UserConfigError(
            f"The selected data file `{filename}` does not exist. "
            "Please check the Scan configuration and retry."
        )
    _group_name = str(PurePosixPath(dataset).parent)
    try:
        with h5py.File(filename, "r") as f:
            grp = f[_group_name]
            if grp.attrs.get("NX_class") != "NXdata":
                raise AssertionError
            if dataset not in f or not isinstance(f[dataset], h5py.Dataset):
                raise KeyError(dataset)
            _data = f[dataset]
            if grp.attrs.get("signal") != PurePosixPath(dataset).stem:
                raise AssertionError
            _axes = grp.attrs.get("axes")
            if len(_axes) != _data.ndim:
                raise AssertionError
            for _dim, _axis in enumerate(_axes):
                _ax = f[f"{_group_name}/{_axis}"]
                if not isinstance(_ax, h5py.Dataset) or _ax.shape != (_data.shape[_dim],):
                    raise AssertionError
    except (KeyError, ValueError, OSError):
        raise UserConfigError(
            f"Unable to read the selected file `{filename}` as HDF5 file. Please "
            "check the file."
        )
    except AssertionError:
        raise UserConfigError(
            f"The selected file `{filename}` does not adhere to the NXdata standard. "
            "Please select a different file or use a different loader for raw HDF5 "
            "data."
        )

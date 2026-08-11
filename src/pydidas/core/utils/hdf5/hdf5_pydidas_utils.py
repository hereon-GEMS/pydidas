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
Module with utility functions with respect to pydidas and HDF5 files.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["get_exported_pydidas_version"]


import h5py

from pydidas.core.utils.hdf5.hdf5_dataset_utils import read_and_decode_hdf5_dataset


def get_exported_pydidas_version(h5file: h5py.File) -> str:
    """
    Get the exported pydidas version from the HDF5 file.

    This function also allows to retrieve the version from legacy files.

    Parameters
    ----------
    h5file : h5py.File
        The HDF5 file to read the version from.

    Returns
    -------
    str
        The exported pydidas version. If no version is found,
        it returns "0.0.0" as version string.
    """
    if "entry/program_name" in h5file:
        _program_name = read_and_decode_hdf5_dataset(h5file["entry/program_name"])
        _version = h5file["entry/program_name"].attrs.get("version")
        if _program_name == "pydidas" and isinstance(_version, str):
            return _version
    if "entry/pydidas_config/pydidas_version" in h5file:
        return read_and_decode_hdf5_dataset(
            h5file["entry/pydidas_config/pydidas_version"]
        )
    return "0.0.0"

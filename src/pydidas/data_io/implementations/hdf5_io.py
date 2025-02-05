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
Module with the Hdf5Io class for importing and exporting Hdf5 data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []


import os
from numbers import Integral
from pathlib import Path
from typing import Union

import h5py
from numpy import ndarray, squeeze

from pydidas.core import Dataset, UserConfigError
from pydidas.core.constants import HDF5_EXTENSIONS
from pydidas.core.utils import CatchFileErrors
from pydidas.core.utils.hdf5_dataset_utils import (
    create_nxdata_entry,
)
from pydidas.data_io.implementations.io_base import IoBase


def _create_slice_object(entry: object):
    """
    Create a slice object from the entry.

    The input can be None to disable slicing or slices can be given as individual
    slice or integer objects or tuples with (low, high) entries for the boundaries.

    Parameters
    ----------
    entry : object
        The input object.

    Returns
    -------
    slice
        The selection slice.
    """
    if entry is None:
        return slice(None, None)
    if isinstance(entry, slice):
        return entry
    if isinstance(entry, Integral):
        return slice(entry, entry + 1)
    if (
        isinstance(entry, (list, tuple))
        and len(entry) == 1
        and isinstance(entry[0], Integral)
    ):
        return slice(entry[0], entry[0] + 1)
    if isinstance(entry, (list, tuple)) and len(entry) == 2:
        if not (isinstance(entry[0], Integral) or entry[0] is None) or not (
            isinstance(entry[1], Integral) or entry[1] is None
        ):
            raise ValueError(
                "Only integers are allowed for slicing objects. Given input: "
                f"`[{entry[0]}, {entry[1]}]`."
            )
        return slice(entry[0], entry[1])
    raise ValueError(f"Could not convert the entry `{entry}` to a slice object.")


def _get_slice_repr(obj: tuple[slice]) -> str:
    """
    Get a string representation of the tuple of slice objects

    Parameters
    ----------
    obj : tuple[slice]
        The tuple of slice objects.

    Returns
    -------
    str
        The string representation of the slicing objects.
    """
    _repr = []
    for _slice in obj:
        if _slice.start is None and _slice.stop is None:
            _repr.append(":")
        elif _slice.start is None and isinstance(_slice.stop, Integral):
            _repr.append(f":{_slice.stop}")
        elif isinstance(_slice.start, Integral) and _slice.stop is None:
            _repr.append(f"{_slice.start}:")
        elif isinstance(_slice.stop, Integral) and isinstance(_slice.stop, Integral):
            if _slice.stop == _slice.start + 1:
                _repr.append(f"{_slice.start}")
            else:
                _repr.append(f"{_slice.start}:{_slice.stop}")
    return "[" + ", ".join(_repr) + "]"


class Hdf5Io(IoBase):
    """IoBase implementation for Hdf5 files."""

    extensions_export = HDF5_EXTENSIONS
    extensions_import = HDF5_EXTENSIONS
    format_name = "Hdf5"
    dimensions = [1, 2, 3, 4, 5, 6, 7, 8]

    @classmethod
    def import_from_file(cls, filename: Union[Path, str], **kwargs: dict) -> Dataset:
        """
        Read data from a Hdf5 file.

        A subset of a Hdf5 dataset can be imported with giving sli

        Parameters
        ----------
        filename : Union[pathlib.Path, str]
            The filename of the file with the data to be imported.
        **kwargs : dict
            The following kwargs are supported:

            dataset : str, optional
                The full path to the hdf dataset within the file. The default is
                "entry/data/data".
            indices : tuple, optional
                Ranges for each axis. Can be given as a single data point, a tuple
                of (min, max) or None to use the full range for each axis. The
                default is an empty tuple ().
            roi : Union[tuple, None], optional
                A region of interest for cropping. Acceptable are both 4-tuples
                of integers in the format (y_low, y_high, x_low, x_high) or
                2-tuples of integers or slice objects. If None, the full image
                will be returned. The default is None.
            returnType : Union[datatype, 'auto'], optional
                If 'auto', the image will be returned in its native data type.
                If a specific datatype has been selected, the image is converted
                to this type. The default is 'auto'.
            binning : int, optional
                The re-binning factor to be applied to the image. The default
                is 1.
            auto_squeeze : bool, optional
                Flag to automatically squeeze data dimensions before returning
                the data. The default is True.
            import_pydidas_metadata : bool, optional
                Flag to get the Dataset metadata from the hdf5 file, if supplied.
                The default is True.

        Returns
        -------
        data : pydidas.core.Dataset
            The data in form of a pydidas Dataset (with embedded metadata)
        """
        _input_indices = kwargs.get("indices", slice(None))
        _indices = (
            (slice(None),)
            if _input_indices in [None, slice(None)]
            else (
                (_input_indices,)
                if isinstance(_input_indices, Integral)
                else tuple(_create_slice_object(_item) for _item in _input_indices)
            )
        )

        dataset = kwargs.get("dataset", "entry/data/data")
        auto_squeeze = kwargs.get("auto_squeeze", True)

        with (
            CatchFileErrors(filename),
            h5py.File(filename, "r") as _h5file,
        ):
            _raw_data = _h5file[dataset][_indices]
            _human_readable_indices = _get_slice_repr(_indices)
            if 0 in _raw_data.shape:
                _full_shape = _h5file[dataset].shape
                raise UserConfigError(
                    f"The selected indices {_human_readable_indices} resulted in a "
                    "dataset with at least one empty axis. Please check the selected "
                    f"slices. The hdf5 dataset has a shape of {_full_shape}."
                )
            _data = Dataset(
                _raw_data,
                metadata={"indices": _human_readable_indices, "dataset": dataset},
            )
            if kwargs.get("import_pydidas_metadata", True):
                cls._update_dataset_metadata(_data, _h5file, dataset, _indices)
            if auto_squeeze:
                _data = squeeze(_data)
            cls._data = _data
        return cls.return_data(**kwargs)

    @staticmethod
    def _update_dataset_metadata(
        data: Dataset, h5file: h5py.File, dataset: str, slicing_indices: tuple[slice]
    ):
        """
        Check the hdf5 file for Dataset metadata and update the data's properties.

        Parameters
        ----------
        data : pydidas.core.Dataset
            The Dataset with the raw data.
        h5file : h5py.File
            The open h5py file object.
        dataset : str
            The dataset location. This is required to find the metadata.
        slicing_indices : tuple[slice]
            The slicing indices used on the loaded data.
        """
        _data_group_name = os.path.dirname(dataset)
        _root = os.path.dirname(_data_group_name)
        _slicers = {index: _slice for index, _slice in enumerate(slicing_indices)}
        if _root == "":
            return
        _items = {_key: _item for _key, _item in h5file[_data_group_name].items()}
        for _ax in range(data.ndim):
            _curr_ax = f"axis_{_ax}"
            if _curr_ax not in _items:
                continue
            _ax_items = {
                _key: _item
                for _key, _item in h5file[f"{_data_group_name}/{_curr_ax}"].items()
            }
            for _key in ["label", "unit", "range"]:
                if _key not in _ax_items:
                    continue
                _val = (
                    _ax_items[_key][_slicers.get(_ax, slice(None))]
                    if _key == "range"
                    else _ax_items[_key][()].decode()
                )
                _meth = getattr(data, f"update_axis_{_key}")
                _meth(_ax, _val if _val is not None else "None")
        for _key in ["data_label", "data_unit"]:
            if _key in h5file[_root]:
                setattr(data, _key, h5file[_root][_key][()].decode())

    @classmethod
    def export_to_file(cls, filename: Union[Path, str], data: ndarray, **kwargs: dict):
        """
        Export data to a Hdf5 file.

        Parameters
        ----------
        filename : Union[pathlib.Path, str]
            The filename
        data : np.ndarray
            The data to be written to file.
        **kwargs : dict
            Additional keyword arguments. Supported keyword arguments are:

            dataset : str, optional
                The full path to the hdf dataset within the file. The default is
                "entry/data/data".
            overwrite : bool, optional
                Flag to allow overwriting of existing files. The default is False.
        """
        cls.check_for_existing_file(filename, **kwargs)
        _dataset = kwargs.get("dataset", "entry/data/data")
        _data_group_name, _dset_name = os.path.split(_dataset)
        _root_group_name = os.path.dirname(_data_group_name)
        if _root_group_name == "":
            raise UserConfigError(
                "The hdf5 dataset path is too shallow to allow writing all metadata. "
                "Please specify a dataset path with at least two groups levels, e.g. "
                "`entry/data/data`."
            )
        if not isinstance(data, Dataset):
            data = Dataset(data)
        with h5py.File(filename, "w") as _file:
            _data_group = create_nxdata_entry(_file, _dataset, data)
            _root_group = _file[_root_group_name]
            _root_group.create_dataset("data_label", data=data.data_label)
            _root_group.create_dataset("data_unit", data=data.data_unit)

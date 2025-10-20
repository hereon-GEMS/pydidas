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
import warnings
from pathlib import Path
from typing import Any, Iterable

import h5py
from numpy import ndarray, squeeze

from pydidas.core import Dataset, FileReadError, UserConfigError
from pydidas.core.constants import HDF5_EXTENSIONS
from pydidas.core.utils import CatchFileErrors, str_repr_of_slice
from pydidas.core.utils.converters import convert_to_slice
from pydidas.core.utils.hdf5_dataset_utils import (
    create_nxdata_entry,
)
from pydidas.data_io.implementations.io_base import IoBase


class Hdf5Io(IoBase):
    """IoBase implementation for Hdf5 files."""

    extensions_import = extensions_export = HDF5_EXTENSIONS
    format_name = "Hdf5"
    dimensions = [1, 2, 3, 4, 5, 6, 7, 8]

    @classmethod
    def import_from_file(cls, filename: Path | str, **kwargs: Any) -> Dataset:
        """
        Read data from an Hdf5 file.

        A subset of an Hdf5 dataset can be imported with giving sli

        Parameters
        ----------
        filename : Path | str
            The filename of the file with the data to be imported.
        **kwargs : Any
            The following kwargs are supported:

            dataset : str, optional
                The full path to the hdf dataset within the file. The default is
                "entry/data/data".
            indices : tuple, optional
                Ranges for each axis. Can be given as a single data point, a tuple
                of (min, max) or None to use the full range for each axis. The
                default is an empty tuple ().
            roi : tuple | None, optional
                A region of interest for cropping. Acceptable are both 4-tuples
                of integers in the format (y_low, y_high, x_low, x_high) or
                2-tuples of integers or slice objects. If None, the full image
                will be returned. The default is None.
            returnType : type | 'auto', optional
                If 'auto', the image will be returned in its native data type.
                If a specific datatype has been selected, the image is converted
                to this type. The default is 'auto'.
            binning : int, optional
                The re-binning factor to be applied to the image. The default
                is 1.
            auto_squeeze : bool, optional
                Flag to automatically squeeze data dimensions before returning
                the data. The default is True.
            import_metadata : bool, optional
                Flag to get the nexus metadata from the hdf5 file, if supplied.
                The default is True.

        Returns
        -------
        data : pydidas.core.Dataset
            The data in the form of a pydidas Dataset (with embedded metadata)
        """
        _input_indices = kwargs.get("indices", slice(None))
        if not isinstance(_input_indices, Iterable):
            _input_indices = (_input_indices,)
        _indices = tuple(convert_to_slice(_item) for _item in _input_indices)
        if "dset" in kwargs and "dataset" not in kwargs:
            warnings.warn("dset keyword is deprecated. Please use dataset instead.")
            kwargs["dataset"] = kwargs.pop("dset")
        dataset = kwargs.get("dataset", "entry/data/data")
        auto_squeeze = kwargs.get("auto_squeeze", True)
        with (
            CatchFileErrors(filename),
            h5py.File(filename, "r") as _h5file,
        ):
            _raw_data = _h5file[dataset][_indices]
            _human_readable_indices = (
                "[" + ", ".join(str_repr_of_slice(_item) for _item in _indices) + "]"
            )
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
            if kwargs.get("import_metadata", True):
                cls._update_dataset_metadata(_data, _h5file, dataset, _indices)
                # TODO [future]: deprecate the axes group reading from legacy results
                cls.__read_legacy_metadata(_data, _h5file, dataset, _indices)
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

        This method reads NeXus-compliant metadata from the hdf5 file and updates
        the Dataset's axis labels, units, and ranges accordingly.

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
        if dataset.count("/") < 2:
            # this means the dataset is not a valid NXdata structure
            return
        _data_group_name, _dset_name = dataset.rsplit("/", 1)
        _slicers = {index: _slice for index, _slice in enumerate(slicing_indices)}
        _data_group = h5file[_data_group_name]
        if not _data_group.attrs.get("NX_class", "") == "NXdata":
            return
        try:
            data.data_unit = h5file[dataset].attrs.get("units", "")
            _signal_name = _data_group.attrs.get("signal", "data")
            if _dset_name != _signal_name:
                data.data_label = h5file[dataset].attrs.get("long_name", "")
                data.metadata = data.metadata | {"valid_metadata": [0]}
                return
            _valid_metadata_axes = []
            for _item_idx, _name in enumerate(_data_group.attrs.get("axes", [])):
                _name = _name if isinstance(_name, str) else _name.decode()
                _idx = _data_group.attrs.get(f"{_name}_indices", [_item_idx])[0]
                _axis_ds = _data_group[_name]
                if isinstance(_axis_ds, h5py.Dataset):
                    _range = _axis_ds[_slicers.get(_idx, slice(None))]
                    data.update_axis_range(_idx, _range)
                    _unit = _axis_ds.attrs.get("units", "")
                    _label = _axis_ds.attrs.get("long_name", _name)
                    # TODO [future]: deprecate check for legacy file information
                    if _unit and _unit in _label:
                        _label = _label.replace(f" / {_unit}", "")
                    data.update_axis_label(_idx, _label)
                    data.update_axis_unit(_idx, _axis_ds.attrs.get("units", ""))
                    _valid_metadata_axes.append(_idx)
            data.data_label = _data_group.attrs.get("title", _signal_name)
            data.metadata = {**data.metadata, "valid_metadata": _valid_metadata_axes}
        except (ValueError, KeyError):
            raise FileReadError(
                "The HDF5 file is not NeXus compliant and the metadata is incomplete. "
                "Please load the data without metadata import and/or check the file."
            )

    @staticmethod
    def __read_legacy_metadata(
        data: Dataset, h5file: h5py.File, dataset: str, slicing_indices: tuple[slice]
    ):
        """
        Read legacy metadata from hdf5 files.

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
        if dataset.count("/") < 2:
            # this means the dataset is not a valid NXentry / NXdata structure
            return
        _data_group_name, _dset_name = dataset.rsplit("/", 1)
        if _dset_name.startswith("axis_"):
            return
        _root = os.path.dirname(_data_group_name)
        _slicers = {index: _slice for index, _slice in enumerate(slicing_indices)}
        _metadata = data.metadata
        _valid_metadata = _metadata.pop("valid_metadata", [])
        data.metadata = _metadata
        _group = h5file[_data_group_name]
        _group_items = [_k for _k, _v in _group.items() if isinstance(_v, h5py.Group)]
        _axes_to_check = {
            _i: f"axis_{_i}"
            for _i in range(data.ndim)
            if (_i not in _valid_metadata and f"axis_{_i}" in _group_items)
        }
        for _idx, _curr_ax in _axes_to_check.items():
            _ax_items = {
                _key: _item
                for _key, _item in h5file[f"{_data_group_name}/{_curr_ax}"].items()
            }
            for _key in ["label", "unit", "range"]:
                if _key not in _ax_items:
                    continue
                _val = (
                    _ax_items[_key][_slicers.get(_idx, slice(None))]
                    if _key == "range"
                    else _ax_items[_key][()].decode()
                )
                _meth = getattr(data, f"update_axis_{_key}")
                _meth(_idx, _val if _val is not None else "None")
        for _key in ["data_label", "data_unit"]:
            if _key in h5file[_root] and getattr(data, _key) == "":
                setattr(data, _key, h5file[_root][_key][()].decode())

    @classmethod
    def export_to_file(cls, filename: Path | str, data: ndarray, **kwargs: Any):
        """
        Export data to an Hdf5 file.

        Parameters
        ----------
        filename : Path | str
            The filename
        data : np.ndarray
            The data to be written to file.
        **kwargs : Any
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

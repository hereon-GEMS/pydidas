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
Module with the Scan class which is used to manage global information about the scan.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["Scan"]


import warnings
from pathlib import Path
from typing import Any, Literal, Union

import numpy as np

from pydidas.core import (
    ObjectWithParameterCollection,
    UserConfigError,
    get_generic_param_collection,
)


SCAN_DEFAULT_PARAMS = get_generic_param_collection(
    "scan_dim",
    "scan_title",
    "scan_base_directory",
    "scan_name_pattern",
    "file_number_offset",
    "file_number_delta",
    "frame_indices_per_scan_point",
    "scan_frames_per_scan_point",
    "scan_multi_frame_handling",
    "scan_dim0_label",
    "scan_dim1_label",
    "scan_dim2_label",
    "scan_dim3_label",
    "scan_dim0_n_points",
    "scan_dim1_n_points",
    "scan_dim2_n_points",
    "scan_dim3_n_points",
    "scan_dim0_delta",
    "scan_dim1_delta",
    "scan_dim2_delta",
    "scan_dim3_delta",
    "scan_dim0_unit",
    "scan_dim1_unit",
    "scan_dim2_unit",
    "scan_dim3_unit",
    "scan_dim0_offset",
    "scan_dim1_offset",
    "scan_dim2_offset",
    "scan_dim3_offset",
)
SCAN_LEGACY_PARAMS = {
    "scan_start_index": "file_number_offset",
    "scan_index_stepping": "frame_indices_per_scan_point",
    "scan_multiplicity": "scan_frames_per_scan_point",
    "scan_multi_image_handling": "scan_multi_frame_handling",
}


class Scan(ObjectWithParameterCollection):
    """
    Class which holds the settings for a scan.

    Only use this class if you are in need to a local Scan instance. Generally,
    the global ScanContext instance is used throughout pydidas to ensure a
    consistent state for all usages of the Scan.
    """

    default_params = SCAN_DEFAULT_PARAMS

    def __init__(self):
        super().__init__()
        self.set_default_params()
        self._scan_io = None

    def get_indices_from_ordinal(self, ordinal: int) -> tuple[int, ...]:
        """
        Get the scan coordinates of the given input index.

        Parameters
        ----------
        ordinal : int
            The ordinal index of the scan point (i.e. the position in the 'timeline')

        Returns
        -------
        tuple[int, ...]
            The indices for indexing the scan point in the grid of all scan points.
            The length of indices is equal to the number of scan dimensions.
        """
        if not 0 <= ordinal < self.n_points:
            raise UserConfigError(
                f"The demanded frame number {ordinal} is out of the scope of the Scan "
                f"indices (0, {self.n_points})."
            )
        _ndim: int = self.get_param_value("scan_dim")  # noqa
        _N = self.shape + (1,)
        _indices = [0] * _ndim
        for _dim in range(_ndim):
            _indices[_dim] = ordinal // int(np.prod(_N[_dim + 1 :]))
            ordinal -= _indices[_dim] * int(np.prod(_N[_dim + 1 :]))
        return tuple(_indices)

    def get_ordinal_from_indices(
        self, indices: tuple[int] | list[int] | np.ndarray
    ) -> int:
        """
        Get the ordinal index based on the scan indices.

        Note: For multiple frames per scan point, this frame number corresponds to
        the first frame at this scan position.

        Parameters
        ----------
        indices : tuple[int] | list[int] | np.ndarray
            The iterable with the scan position indices.

        Returns
        -------
        int
            The frame index in the scan.
        """
        if not isinstance(indices, np.ndarray):
            indices = np.asarray(indices)
        _shapes = np.asarray(self.shape + (1,))
        _indices_okay = [
            0 <= _index <= _shapes[_dim]  # noqa
            for _dim, _index in enumerate(indices)
        ]
        if False in _indices_okay:
            raise UserConfigError(
                f"The given indices {tuple(indices)} are out of the scope "
                f"of the scan range {self.shape}"
            )
        _factors = np.asarray([np.prod(_shapes[_i + 1 :]) for _i in range(self.ndim)])
        _index = np.sum(_factors * indices)
        return _index

    def get_metadata_for_dim(
        self, index: Literal[0, 1, 2, 3]
    ) -> tuple[str, str, np.ndarray]:
        """
        Get the label, unit and range of the specified scan dimension.

        Note: The scan dimensions are 0 ... 3 and follow the python convention of
        starting with zero.

        Parameters
        ----------
        index : Literal[0, 1, 2, 3]
            The index of the scan dimension.

        Returns
        -------
        label : str
            The label / motor name for this scan dimension.
        unit : str
            The unit for the range.
        range : np.ndarray
            The numerical positions of the scan.
        """
        if index not in [0, 1, 2, 3]:
            raise UserConfigError("Only the scan dimensions 0, 1, 2, 3 are supported.")
        _label = self.get_param_value(f"scan_dim{index}_label")
        _unit = self.get_param_value(f"scan_dim{index}_unit")
        _range = self.get_range_for_dim(index)
        return _label, _unit, _range

    def get_range_for_dim(self, index: int) -> np.ndarray:
        """
        Get the Scan range for the specified dimension.

        Note: The scan dimensions are 0 ... 3 and follow the python convention of
        starting with zero.

        Parameters
        ----------
        index : Union[0, 1, 2, 3]
            The scan dimension

        Returns
        -------
        np.ndarray
            The scan range as numpy array.
        """
        if index not in [0, 1, 2, 3]:
            raise UserConfigError("Only the scan dimensions 0, 1, 2, 3 are supported.")
        _f0 = self.get_param_value(f"scan_dim{index}_offset")
        _df = self.get_param_value(f"scan_dim{index}_delta")
        _n = self.get_param_value(f"scan_dim{index}_n_points")
        return np.linspace(_f0, _f0 + _df * _n, _n, endpoint=False)  # noqa

    def update_from_scan(self, scan: "Scan"):
        """
        Update this Scan object's Parameters from another Scan.

        The purpose of this method is to "copy" the other Scan's Parameter values while
        keeping the reference to this object.

        Parameters
        ----------
        scan : Scan
            The other Scan from which the Parameters should be taken.
        """
        for _key, _val in scan.get_param_values_as_dict().items():
            self.set_param_value(_key, _val)

    def update_from_dictionary(self, scan_dict: dict):
        """
        Update the Scan from an imported dictionary.

        Parameters
        ----------
        scan_dict : dict
            The dictionary with the data to import.
        """
        if scan_dict == {}:
            return
        for _pname in [
            "scan_dim",
            "scan_title",
            "scan_base_directory",
            "scan_name_pattern",
            "file_number_offset",
            "frame_indices_per_scan_point",
            "scan_frames_per_scan_point",
            "scan_multi_frame_handling",
        ]:
            self.set_param_value(_pname, scan_dict[_pname])
        for _dim in range(self.get_param_value("scan_dim")):
            _curr_dim_info = scan_dict[_dim]
            for _entry in ["label", "unit", "offset", "delta", "n_points"]:
                self.set_param_value(f"scan_dim{_dim}_{_entry}", _curr_dim_info[_entry])

    @property
    def shape(self) -> tuple[int, ...]:
        """
        Get the shape of the Scan.

        Returns
        -------
        tuple[int]
            The tuple with an entry of the length for each dimension.
        """
        return tuple(
            self.get_param_value(f"scan_dim{_i}_n_points")
            for _i in range(self.ndim)  # noqa
        )

    @property
    def n_points(self) -> int:
        """
        Get the total number of points in the Scan.

        Returns
        -------
        int
            The total number of images.
        """
        return int(np.prod(self.shape))

    @property
    def ndim(self) -> int:
        """
        Get the number of dimensions in the ScanContext.

        This method is a simplified wrapper for the ParameterValue "scan_dim".

        Returns
        -------
        int
            The number of dimensions.
        """
        return self.get_param_value("scan_dim")

    @property
    def axis_labels(self) -> list[str]:
        """
        Get the axis labels of the scan.

        Returns
        -------
        list[str]
            The axis labels.
        """
        return [self.get_param_value(f"scan_dim{_i}_label") for _i in range(self.ndim)]

    @property
    def axis_units(self) -> list[str]:
        """
        Get the axis units of the scan.

        Returns
        -------
        list[str]
            The axis units.
        """
        return [self.get_param_value(f"scan_dim{_i}_unit") for _i in range(self.ndim)]

    @property
    def axis_ranges(self) -> list[np.ndarray]:
        """
        Get the axis ranges of the scan.

        Returns
        -------
        list[np.ndarray]
            The axis ranges.
        """
        return [self.get_range_for_dim(_i) for _i in range(self.ndim)]

    def import_from_file(self, filename: Union[str, Path]):
        """
        Import ScanContext from a file.

        Parameters
        ----------
        filename : Union[str, pathlib.Path]
            The full filename.
        """
        if self._scan_io is None:
            from pydidas.contexts.scan.scan_io import ScanIo

            self._scan_io = ScanIo
        self._scan_io.import_from_file(filename, scan=self)

    def export_to_file(self, filename: Union[str, Path], overwrite: bool = False):
        """
        Export ScanContext to a file.

        Parameters
        ----------
        filename : Union[str, pathlib.Path]
            The full filename.
        overwrite : bool
            Keyword to allow overwriting of existing files. The default is
            False.
        """
        if self._scan_io is None:
            from pydidas.contexts.scan.scan_io import ScanIo

            self._scan_io = ScanIo
        self._scan_io.export_to_file(filename, scan=self, overwrite=overwrite)

    def set_param_value(self, param_key: str, value: Any):
        """
        Set the value of a parameter.

        Parameters
        ----------
        param_key : str
            The key of the parameter to set.
        value : Any
            The value to set for the parameter.
        """
        if param_key in SCAN_LEGACY_PARAMS:
            warnings.warn(
                (
                    f"The parameter `{param_key}` is deprecated and has be replaced by "
                    f"`{SCAN_LEGACY_PARAMS[param_key]}`. Please use the new parameter "
                    "key."
                ),
                DeprecationWarning,
            )
            param_key = SCAN_LEGACY_PARAMS[param_key]
        super().set_param_value(param_key, value)

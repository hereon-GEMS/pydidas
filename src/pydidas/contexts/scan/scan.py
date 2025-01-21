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


from pathlib import Path
from typing import Self, Tuple, Union

import numpy as np

from pydidas.contexts.scan.scan_io import ScanIo
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
    "scan_start_index",
    "scan_index_stepping",
    "scan_multiplicity",
    "scan_multi_image_handling",
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


class Scan(ObjectWithParameterCollection):
    """
    Class which holds the settings for the scan.

    This class should only be instanciated through its factory, therefore guaranteeing
    that only a single instance exists. Please instanciate Scan only directly if you
    explicitly need to.
    """

    default_params = SCAN_DEFAULT_PARAMS.copy()

    def __init__(self):
        super().__init__()
        self.set_default_params()

    def get_index_position_in_scan(self, index: int) -> tuple:
        """
        Get the scan coordinates of the given input index.

        Parameters
        ----------
        index : int
            The index of the scan point (i.e. the position in the 'timeline')

        Returns
        -------
        tuple
            The indices for indexing the position of the frame in the scan.
            The length of indices is equal to the number of scan dimensions.
        """
        return self.__get_scan_indices(index, 1)

    def get_frame_position_in_scan(self, frame_index: int):
        """
        Get the position of a frame number on scan coordinates.

        Parameters
        ----------
        frame : int
            The frame number.

        Returns
        -------
        indices : tuple
            The indices for indexing the position of the frame in the scan.
            The length of indices is equal to the number of scan dimensions.
        """
        return self.__get_scan_indices(
            frame_index, self.get_param_value("scan_multiplicity")
        )

    def __get_scan_indices(self, index: int, multiplicity: int) -> tuple:
        """
        Get the scan indices for the given index and multiplicity.

        Parameters
        ----------
        index : int
            The input index.
        multiplicity : int
            The image multiplicity.

        Returns
        -------
        tuple
            The scan indices.
        """
        _n_frames = self.n_points * multiplicity
        if not 0 <= index < _n_frames:
            raise UserConfigError(
                f"The demanded frame number {index} is out of the scope of the Scan "
                f"indices (0, {_n_frames})."
            )
        _ndim = self.get_param_value("scan_dim")
        _N = [self.get_param_value(f"scan_dim{_n}_n_points") for _n in range(_ndim)] + [
            multiplicity
        ]
        _indices = [0] * _ndim
        for _dim in range(_ndim):
            _indices[_dim] = index // np.prod(_N[_dim + 1 :])
            index -= _indices[_dim] * np.prod(_N[_dim + 1 :])
        return tuple(_indices)

    def get_frame_from_indices(self, indices: tuple) -> int:
        """
        Get the frame number based on the scan indices.

        Note: For an image multiplicity > 1, this frame number corresponds to the first
        frame at this scan position.

        Parameters
        ----------
        indices : Union[tuple, list, np.ndarray]
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
            0 <= _index <= _shapes[_dim] for _dim, _index in enumerate(indices)
        ]
        if False in _indices_okay:
            raise UserConfigError(
                f"The given indices {tuple(indices)} are out of the scope "
                f"of the scan range {self.shape}"
            )
        _factors = np.asarray([np.prod(_shapes[_i + 1 :]) for _i in range(self.ndim)])
        _index = np.sum(_factors * indices) * self.get_param_value("scan_multiplicity")
        return _index

    def get_index_of_frame(self, frame_index: int) -> int:
        """
        Get the scan point index of the given frame.

        Parameters
        ----------
        frame_index : int
            The frame index.

        Returns
        -------
        int
            The scan point index.
        """
        return frame_index // self.get_param_value("scan_multiplicity")

    def get_metadata_for_dim(self, index: int) -> Tuple[str, str, np.ndarray]:
        """
        Get the label, unit and range of the specified scan dimension.

        Note: The scan dimensions are 0 .. 3 and follow the python convention of
        starting with zero.

        Parameters
        ----------
        index : Union[0, 1, 2, 3]
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
        _label = self.get_param_value(f"scan_dim{index}_label")
        _unit = self.get_param_value(f"scan_dim{index}_unit")
        _range = self.get_range_for_dim(index)
        return _label, _unit, _range

    def get_range_for_dim(self, index: int) -> np.ndarray:
        """
        Get the Scan range for the specified dimension.

        Note: The scan dimensions are 0 .. 3 and follow the python convention of
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
        return np.linspace(_f0, _f0 + _df * _n, _n, endpoint=False)

    def update_from_scan(self, scan: Self):
        """
        Update this Scan onject's Parameters from another Scan.

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
            "scan_start_index",
            "scan_index_stepping",
            "scan_multiplicity",
            "scan_multi_image_handling",
        ]:
            self.set_param_value(_pname, scan_dict[_pname])
        for _dim in range(self.get_param_value("scan_dim")):
            _curr_dim_info = scan_dict[_dim]
            for _entry in ["label", "unit", "offset", "delta", "n_points"]:
                self.set_param_value(f"scan_dim{_dim}_{_entry}", _curr_dim_info[_entry])

    @property
    def shape(self) -> tuple:
        """
        Get the shape of the Scan.

        Returns
        -------
        tuple
            The tuple with an entry of the length for each dimension.
        """
        return tuple(
            self.get_param_value(f"scan_dim{_i}_n_points")
            for _i in range(self.get_param_value("scan_dim"))
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
        _n = np.prod(
            [self.get_param_value(f"scan_dim{_i}_n_points") for _i in range(self.ndim)]
        )
        return int(_n)

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

    def import_from_file(self, filename: Union[str, Path]):
        """
        Import ScanContext from a file.

        Parameters
        ----------
        filename : Union[str, pathlib.Path]
            The full filename.
        """
        ScanIo.import_from_file(filename, scan=self)

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
        ScanIo.export_to_file(filename, scan=self, overwrite=overwrite)

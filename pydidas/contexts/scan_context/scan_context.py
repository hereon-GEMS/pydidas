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
Module with the ScanContext class which is used to manage global
information about the scan.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["ScanContext", "Scan"]

import numpy as np

from ...core import (
    SingletonFactory,
    get_generic_param_collection,
    ObjectWithParameterCollection,
    UserConfigError,
)
from .scan_context_io_meta import ScanContextIoMeta


SCAN_CONTEXT_DEFAULT_PARAMS = get_generic_param_collection(
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
    Class which holds the settings for the scan. This class must only be
    instanciated through its factory, therefore guaranteeing that only a
    single instance exists.
    """

    default_params = SCAN_CONTEXT_DEFAULT_PARAMS.copy()

    def __init__(self):
        super().__init__()
        self.set_default_params()

    def get_frame_position_in_scan(self, frame):
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
        _n_frames = self.n_points * self.get_param_value("scan_multiplicity")
        if not 0 <= frame < _n_frames:
            raise UserConfigError(
                f"The demanded frame number '{frame}' is out of the scope of the Scan "
                f"indices (0, {_n_frames})."
            )
        _ndim = self.get_param_value("scan_dim")
        _N = [self.get_param_value(f"scan_dim{_n}_n_points") for _n in range(_ndim)] + [
            self.get_param_value("scan_multiplicity")
        ]
        _indices = [0] * _ndim
        for _dim in range(_ndim):
            _indices[_dim] = frame // np.prod(_N[_dim + 1 :])
            frame -= _indices[_dim] * np.prod(_N[_dim + 1 :])
        return tuple(_indices)

    def get_frame_number_from_scan_indices(self, indices):
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
                f'The given indices "{tuple(indices)}" are out of the scope '
                f"of the scan range {self.shape}"
            )
        _factors = np.asarray([np.prod(_shapes[_i + 1 :]) for _i in range(self.ndim)])
        _index = np.sum(_factors * indices) * self.get_param_value("scan_multiplicity")
        return _index

    def get_metadata_for_dim(self, index):
        """
        Get the label, unit and range of the specified scan dimension.

        Note
        ----
        The scan dimensions are 1 .. 4 and do not start with 0.

        Parameters
        ----------
        index : Union[1, 2, 3, 4]
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

    def get_range_for_dim(self, index):
        """
        Get the Scan range for the specified dimension.

        Note
        ----
        The scan dimensions are 0 .. 3 and follow the python convention of starting with
        zero.

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

    def update_from_dictionary(self, scan_dict):
        """
        Update scen ScanContext from an imported dictionary.

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
    def shape(self):
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
    def n_points(self):
        """
        Get the total number of points in the Scan.

        Returns
        -------
        int
            The total number of images.
        """
        return np.prod(
            [
                self.get_param_value(f"scan_dim{_i}_n_points")
                for _i in range(self.get_param_value("scan_dim"))
            ]
        )

    @property
    def ndim(self):
        """
        Get the number of dimensions in the ScanContext.

        This method is a simplified wrapper for the ParameterValue "scan_dim".

        Returns
        -------
        int
            The number of dimensions.
        """
        return self.get_param_value("scan_dim")

    @staticmethod
    def import_from_file(filename):
        """
        Import ScanContext from a file.

        Parameters
        ----------
        filename : Union[str, pathlib.Path]
            The full filename.
        """
        ScanContextIoMeta.import_from_file(filename)

    @staticmethod
    def export_to_file(filename, overwrite=False):
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
        ScanContextIoMeta.export_to_file(filename, overwrite=overwrite)


ScanContext = SingletonFactory(Scan)

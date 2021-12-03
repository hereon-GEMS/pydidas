# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Module with the GlobalSettings class which is used to manage global
information independant from the individual frames."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ScanSettings']

import numpy as np

from .scan_settings_io_meta import ScanSettingsIoMeta
from ...core import (SingletonFactory, ParameterCollection,
                    get_generic_parameter, ObjectWithParameterCollection)


DEFAULT_PARAMS = ParameterCollection(
    get_generic_parameter('scan_dim'),
    get_generic_parameter('scan_name'),
    get_generic_parameter('scan_dir_1'),
    get_generic_parameter('scan_dir_2'),
    get_generic_parameter('scan_dir_3'),
    get_generic_parameter('scan_dir_4'),
    get_generic_parameter('n_points_1'),
    get_generic_parameter('n_points_2'),
    get_generic_parameter('n_points_3'),
    get_generic_parameter('n_points_4'),
    get_generic_parameter('delta_1'),
    get_generic_parameter('delta_2'),
    get_generic_parameter('delta_3'),
    get_generic_parameter('delta_4'),
    get_generic_parameter('unit_1'),
    get_generic_parameter('unit_2'),
    get_generic_parameter('unit_3'),
    get_generic_parameter('unit_4'),
    get_generic_parameter('offset_1'),
    get_generic_parameter('offset_2'),
    get_generic_parameter('offset_3'),
    get_generic_parameter('offset_4'),
    )


class _ScanSettings(ObjectWithParameterCollection):
    """
    Class which holds experimental settings. This class must only be
    instanciated through its factory, therefore guaranteeing that only a
    single instance exists.
    """
    default_params = DEFAULT_PARAMS

    def __init__(self):
        """Setup method"""
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
        if frame < 0 or frame >= self.n_total:
            raise ValueError(f'The demanded frame number "{frame}" is out of '
                             f'the scope of the Scan (0, {self.n_total}).')
        _ndim = self.get_param_value('scan_dim')
        _N = [self.get_param_value(f'n_points_{_n}')
              for _n in range(1, _ndim + 1)] + [1]
        _indices = [0] * _ndim
        for _dim in range(_ndim):
            _indices[_dim] = frame // np.prod(_N[_dim + 1:])
            frame -= _indices[_dim] * np.prod(_N[_dim + 1:])
        return tuple(_indices)

    def get_metadata_for_dim(self, index):
        """
        Get the label, unit and range of the specified scan dimension.

        Note: The scan dimensions are 1 .. 4 and do not start with 0.

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
        _label = self.get_param_value(f'scan_dir_{index}')
        _unit = self.get_param_value(f'unit_{index}')
        _range = self.get_range_for_dim(index)
        return _label, _unit, _range

    def get_range_for_dim(self, index):
        """
        Get the Scan range for the specified dimension.

        Note: The scan dimensions are 1 .. 4 and do not start with 0.

        Parameters
        ----------
        index : Union[1, 2, 3, 4]
            The scan dimension

        Returns
        -------
        np.ndarray
            The scan range as numpy array.
        """
        if index not in [1, 2, 3, 4]:
            raise ValueError('Only the scan dimensions [1, 2, 3, 4] are '
                             'supported.')
        _f0 = self.get_param_value(f'offset_{index}')
        _df = self.get_param_value(f'delta_{index}')
        _n = self.get_param_value(f'n_points_{index}')
        return np.linspace(_f0, _f0 + _df * _n, _n, endpoint=False)

    @property
    def shape(self):
        """
        Get the shape of the Scan.

        Returns
        -------
        tuple
            The tuple with an entry of the length for each dimension.
        """
        return tuple(self.get_param_value(f'n_points_{_i}')
                     for _i in range(1, self.get_param_value('scan_dim') + 1))

    @property
    def n_total(self):
        """
        Get the total number of points in the Scan.

        Returns
        -------
        int
            The total number of images.
        """
        return np.prod([self.get_param_value(f'n_points_{_i}') for _i
                        in range(1, self.get_param_value('scan_dim') + 1)])

    @property
    def ndim(self):
        """
        Get the number of dimensions in the ScanSettings.

        This method is a simplified wrapper for the ParameterValue "scan_dim".

        Returns
        -------
        int
            The number of dimensions.
        """
        return self.get_param_value('scan_dim')

    @staticmethod
    def import_from_file(filename):
        """
        Import ScanSettings from a file.

        Parameters
        ----------
        filename : Union[str, pathlib.Path]
            The full filename.
        """
        ScanSettingsIoMeta.import_from_file(filename)

    @staticmethod
    def export_to_file(filename):
        """
        Import ScanSettings from a file.

        Parameters
        ----------
        filename : Union[str, pathlib.Path]
            The full filename.
        """
        ScanSettingsIoMeta.export_to_file(filename)


ScanSettings = SingletonFactory(_ScanSettings)

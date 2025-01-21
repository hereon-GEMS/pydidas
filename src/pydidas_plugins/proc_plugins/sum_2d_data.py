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
Module with the Sum2dData Plugin which can be used to sum over 2D data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["Sum2dData"]


import numpy as np

from pydidas.core import Dataset, UserConfigError, get_generic_param_collection
from pydidas.plugins import ProcPlugin


class Sum2dData(ProcPlugin):
    """
    Sum up datapoints in a 2D dataset.

    This plugin creates a single datapoint from the 2D input data. Limits
    can be given with the lower and upper limit parameters. The data can
    be selected either by indices or by the data range. The type of selection
    is determined by the `type_selection` parameter. `None` values in the
    lower and upper limit parameters are used to ignore the limit. The upper
    limit is included in the summation.

    The plugin can handle higher-dimensional input data and will keep the
    dimensions not processed by the plugin. For example, in a 3D dataset,
    summing over axes 0 and 1 would yield a 1D dataset with the original
    dimension 2 kept in place.

    Note that the plugin sorts the dimensions to process. For example, if
    the dimensions to process are given as `(2, 0)`, the plugin will process
    the dimensions in the order `(0, 2)` and therefore the limit for
    `axis 0` will be applied to dimension 0 and the limit for `axis 1`
    will be applied to dimension 2 of the input dataset.
    """

    plugin_name = "Sum 2D data"

    default_params = get_generic_param_collection(
        "process_data_dims",
        "_process_data_dims",
        "type_selection",
        "lower_limit_ax0",
        "upper_limit_ax0",
        "lower_limit_ax1",
        "upper_limit_ax1",
    )

    output_data_label = "data sum (2d)"
    output_data_unit = "a.u."
    new_dataset = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pre_execute()

    def pre_execute(self):
        """
        Reset the index range slices before starting a new processing run.
        """
        self._config["slices"] = None
        self._config["first_execute_configured"] = False
        self._metadata = {}

    def execute(self, data: Dataset, **kwargs: dict) -> tuple[Dataset, dict]:
        """
        Sum the input data over the given ranges.

        Parameters
        ----------
        data : pydidas.core.Dataset
            The input Dataset
        **kwargs : dict
            Any calling keyword arguments.

        Returns
        -------
        pydidas.core.Dataset
            The data sum in form of an array of shape (1,).
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        self._data = data
        if not self._config["first_execute_configured"]:
            self._first_execution()
        _new_data = np.atleast_1d(
            np.sum(
                data, axis=self.get_param_value("_process_data_dims"), where=self._mask
            )
        )
        return (
            Dataset(
                _new_data,
                metadata=data.metadata,
                data_label=self.output_data_label,
                data_unit=self.output_data_unit,
                **self._metadata,
            ),
            kwargs,
        )

    def _first_execution(self):
        """
        Compute steps which are required only once for the execution of the plugin.
        """
        self._create_sum_mask()
        self.output_data_unit = self._data.data_unit
        self.output_data_label = f"2d sum of {self._data.data_label}"
        if self._data.ndim > 2:
            self._metadata = {
                "axis_labels": [
                    _label
                    for _dim, _label in self._data.axis_labels.items()
                    if _dim not in self.get_param_value("_process_data_dims")
                ],
                "axis_units": [
                    _unit
                    for _dim, _unit in self._data.axis_units.items()
                    if _dim not in self.get_param_value("_process_data_dims")
                ],
                "axis_ranges": [
                    _range
                    for _dim, _range in self._data.axis_ranges.items()
                    if _dim not in self.get_param_value("_process_data_dims")
                ],
            }
        else:
            self._metadata = {
                "axis_labels": ["Data sum"],
            }
        self._config["first_execute_configured"] = True

    def _create_sum_mask(self):
        """
        Calculate the ranges for the selected data sum.
        """
        _proc_dims = self._get_proc_dims()
        _valid_ranges = {
            _dim: self._get_valid_indices(_ax, _dim)
            for _ax, _dim in enumerate(_proc_dims)
        }
        _mask = np.ones(self._data.shape, dtype=bool)
        for _dim, _to_sum in _valid_ranges.items():
            _slicer = (
                [None] * _dim + [slice(None)] + [None] * (self._data.ndim - _dim - 1)
            )
            _mask *= _to_sum[*_slicer]
        self._mask = _mask

    def _get_proc_dims(self, input_ndim=None) -> tuple[int]:
        """
        Get the dimensions to process.

        Parameters
        ----------
        input_ndim : tuple[int], optional
            The number of dimensions of the input data. If None, the dimensionality
            of the input data is taken. The default is None.

        Returns
        -------
        tuple[int]
            The dimensions to process.
        """
        if input_ndim is None:
            input_ndim = self._data.ndim
        _proc_dims = self.get_param_value("process_data_dims")
        if _proc_dims is None:
            if input_ndim != 2:
                raise UserConfigError(
                    "The input data in `Sum2D`is not 2D and the plugin is not "
                    "configured to handle more dimensions. Please set the "
                    "`process_data_dims` parameter to a tuple with the two dimensions "
                    "to process (e.g. `(0, 1)`)."
                )
            _proc_dims = (0, 1)
        if len(_proc_dims) != 2:
            raise UserConfigError(
                "The `process_data_dims` Parameter in the `Sum2D` plugin is not "
                "correctly configured. Please provide a tuple with only two "
                "dimensions to process (e.g. `(0, 1)`)."
            )
        _proc_dims = tuple(sorted([_d % input_ndim for _d in _proc_dims]))
        self.set_param_value("_process_data_dims", _proc_dims)
        return self.get_param_value("_process_data_dims")

    def _get_valid_indices(self, axis: int, dim: int) -> np.ndarray[bool]:
        """
        Get the indices for the selected data range.

        Parameters
        ----------
        axis : int
            The axis number in the Parameters.
        dim : int
            The dimension to process.

        Returns
        -------
        np.ndarray[bool]
            The mask for the selected range.
        """
        _data_dim_size = self._data.shape[dim]
        if self.get_param_value("type_selection") == "Indices":
            _ax_range = np.arange(_data_dim_size)
            _low, _high = self._get_axis_range(dim, 0, _data_dim_size)
        else:
            _ax_range = self._data.axis_ranges[dim]
            assert isinstance(_ax_range, np.ndarray), (
                "The data does not have a correct range and using the data range "
                "for selection is only available using the indices."
            )
            _low, _high = self._get_axis_range(axis, _ax_range[0], _ax_range[-1])
        return np.where((_low <= _ax_range) & (_ax_range <= _high), 1, 0).astype(bool)

    def _get_axis_range(
        self, axis: int, default_low: float, default_high: float
    ) -> tuple[float, float]:
        """
        Get the range for the selected axis.

        Parameters
        ----------
        axis : int
            The axis number.
        default_low : float
            The default value in case the lower limit is None.
        default_high : float
            The default value in case the lower limit is None.

        Returns
        -------
        tuple[float, float]
            The axis bounds
        """
        _low_lim = self.get_param_value(f"lower_limit_ax{axis}")
        _low = _low_lim if _low_lim is not None else default_low
        _high_lim = self.get_param_value(f"upper_limit_ax{axis}")
        _high = _high_lim if _high_lim is not None else default_high
        return (_low, _high)

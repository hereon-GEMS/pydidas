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
The PluginResultInfo is a class for storing and accessing information
about plugin results.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PluginResultInfo"]

from dataclasses import dataclass, field, replace
from typing import Any

import numpy as np
from numpy import ndarray


@dataclass
class PluginResultInfo:
    """
    A class for handling information of node results.

    In addition to the usual dataclass attributes, derived attributes
    for the squeezed result shape are implemented.
    """

    label: str = ""
    node_id: int | None = None
    plugin_name: str = ""
    result_title: str = ""
    scan_ndim: int = 0
    squeeze: bool = False
    data_label: str = ""
    data_unit: str = ""
    axis_labels: dict[int, str] = field(default_factory=dict)
    axis_units: dict[int, str] = field(default_factory=dict)
    axis_ranges: dict[int, ndarray] = field(default_factory=dict)

    @property
    def export_shape(self) -> tuple[int, ...]:
        """
        Get the shape of the result export.

        Depending on the squeeze flag, the shape may be reduced by
        removing dimensions of length 1.

        Returns
        -------
        tuple[int, ...]
            The shape of the result export, potentially squeezed.
        """
        if self.squeeze:
            return tuple(_n for _n in self.shape if _n > 1)
        return self.shape

    @property
    def dataset_metadata(self) -> dict[str, Any]:
        """
        Get the metadata required to create a Dataset object from the result.

        Returns
        -------
        dict[str, Any]
            The metadata required to create a Dataset object from the result.
        """
        return {
            "data_label": self.data_label,
            "data_unit": self.data_unit,
            "axis_labels": self.axis_labels,
            "axis_units": self.axis_units,
            "axis_ranges": self.axis_ranges,
        }

    @dataset_metadata.setter
    def dataset_metadata(self, metadata_dict: dict[str, Any]) -> None:
        """
        Set the metadata required to create a Dataset object from the result.

        Parameters
        ----------
        metadata_dict : dict[str, Any]
            The metadata dictionary to set.
        """
        self.data_label = metadata_dict.get("data_label", "")
        self.data_unit = metadata_dict.get("data_unit", "")
        self.axis_labels = metadata_dict.get("axis_labels", {})
        self.axis_units = metadata_dict.get("axis_units", {})
        self.axis_ranges = metadata_dict.get("axis_ranges", {})

    @property
    def shape(self) -> tuple[int, ...]:
        """
        Get the shape of the result.

        Returns
        -------
        tuple[int, ...]
            The shape of the result.
        """
        return tuple(_range.size for _range in self.axis_ranges.values())

    @property
    def ndim(self) -> int:
        """
        Get the number of dimensions of the result.

        Returns
        -------
        int
            The number of dimensions of the result.
        """
        return len(self.shape)

    @property
    def result_ndim(self) -> int:
        """
        Get the number of dimensions of the result excluding scan dimensions.

        Returns
        -------
        int
            The number of dimensions of the result excluding scan dimensions.
        """
        return self.ndim - self.scan_ndim

    @property
    def result_shape(self) -> tuple[int, ...]:
        """
        Get the shape of the result excluding scan dimensions.

        Returns
        -------
        tuple[int, ...]
            The shape of the result excluding scan dimensions.
        """
        return self.shape[self.scan_ndim :]

    def get_metadata(
        self, use_scan_timeline: bool = False, squeeze: bool = False
    ) -> dict[str, Any]:
        """
        Get the metadata required to describe the results.

        Parameters
        ----------
        use_scan_timeline : bool, optional
            Whether to flatten the scan to a single timeline, by default False
        squeeze : bool, optional
            Whether to squeeze the results (i.e. remove all dimensions of length 1)
            from the data. The default is False.

        Returns
        -------
        dict[str, Any]
            The metadata required to describe the results.
        """
        _data_ndim = self.ndim - self.scan_ndim
        if not use_scan_timeline:
            _metadata = self.dataset_metadata
            for _key in ["axis_ranges", "axis_labels", "axis_units"]:
                _metadata[_key] = list(_metadata[_key].values())
            _metadata["shape"] = self.shape
            _metadata["axis_types"] = ["(scan)"] * self.scan_ndim + [
                "(data)"
            ] * _data_ndim
            _metadata["ndim_scan"] = self.scan_ndim
        else:
            _metadata: dict[str, Any] = {
                "data_label": self.data_label,
                "data_unit": self.data_unit,
                "ndim_scan": 1,
                "axis_labels": ["Chronological scan points"],
                "axis_units": [""],
                "axis_ranges": [np.arange(np.prod(self.shape[: self.scan_ndim]))],
                "axis_types": ["(scan)"] + ["(data)"] * _data_ndim,
            }
            for _dim in range(self.scan_ndim, self.ndim):
                _metadata["axis_ranges"].append(self.axis_ranges[_dim])
                _metadata["axis_labels"].append(self.axis_labels.get(_dim, ""))
                _metadata["axis_units"].append(self.axis_units.get(_dim, ""))
            _metadata["shape"] = tuple(_ax.size for _ax in _metadata["axis_ranges"])
        if squeeze:
            _dims_to_squeeze = [
                _i for _i, _arr in enumerate(_metadata["axis_ranges"]) if _arr.size == 1
            ]
            for _dim in [0] if use_scan_timeline else range(self.scan_ndim):
                if _dim in _dims_to_squeeze:
                    _metadata["ndim_scan"] -= 1
            for _key in [
                "axis_labels",
                "axis_units",
                "axis_ranges",
                "shape",
                "axis_types",
            ]:
                _metadata[_key] = [
                    _v
                    for _i, _v in enumerate(_metadata[_key])
                    if _i not in _dims_to_squeeze
                ]
        return _metadata

    def copy(self) -> "PluginResultInfo":
        """An alias for the __copy__ method."""
        return self.__copy__()

    def __copy__(self) -> "PluginResultInfo":
        """A copy implementation to be used by the copy module."""
        _copy = replace(self)
        return _copy

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
Module with the NXdataResultLoader plugin for re-ingesting pydidas result
files into a new workflow as input data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["NXdataResultLoader"]

from pathlib import Path
from typing import Any, NoReturn

from pydidas.core import (
    Dataset,
    FileReadError,
    Parameter,
    ParameterCollection,
    UserConfigError,
    get_generic_parameter,
)
from pydidas.core.utils.hdf5 import get_hdf5_metadata
from pydidas.core.utils.hdf5.nxs_dataset_utils import check_nxdata_adherence
from pydidas.data_io import import_data
from pydidas.plugins import BasePlugin, InputPlugin


class NXdataResultLoader(InputPlugin):
    """
    Load results from a single HDF5 file with a NXdata entry.

    All intermediate pydidas results are stored with the NXdata convention
    and can be imported, as well as all other data which adhere to the
    NXdata convention.

    Note that the data must have a shape of (scan_shape, data_dim0, data_dim1,
    ...) and the number of expected data dimensions must be given in the
    respective Parameter to verify the data consistency.

    Parameters
    ----------
    nxdata_key : str, optional
        Path to the dataset inside the HDF5 file.
        The default is ``entry/data/data``.
    expected_data_dim : int, optional
        Number of dimensions per individual data point (trailing, non-scan
        dimensions). The default is 2.
    """

    plugin_name = "NXdata result loader"
    base_output_data_dim = None
    generic_params = BasePlugin.generic_params.copy()
    advanced_parameters = []

    default_params = ParameterCollection(
        get_generic_parameter("nxdata_key"),
        Parameter(
            "expected_data_dim",
            int,
            2,
            name="Data point dimensionality",
            tooltip=(
                "The expected number of dimensions per data point (i.e. the "
                "number of non-scan axes in the result file). Required to "
                "correctly index into the stored dataset."
            ),
        ),
        get_generic_parameter("_counted_images_per_file"),
    )

    @property
    def output_data_dim(self) -> int:
        """
        The output dimensionality of a single execution call.

        Returns
        -------
        int
            ``expected_data_dim`` plus one when ``scan_frames_per_point > 1``
            and ``scan_multi_frame_handling`` is ``"Stack"``.
        """
        _data_dim = self.get_param_value("expected_data_dim")
        return _data_dim + (
            1
            if self._SCAN.get_param_value("scan_frames_per_point") > 1
            and self._SCAN.get_param_value("scan_multi_frame_handling") == "Stack"
            else 0
        )

    # ------------------------------------
    # Re-implemented InputPlugin methods:
    # ------------------------------------

    def input_available(self, ordinal: int) -> bool:
        """
        Check whether input is available.

        For importing results, this method always returns True.

        Parameters
        ----------
        ordinal : int
            The frame index. This is ignored for this plugin as the same file
            is used for all frames.

        Returns
        -------
        bool
            Always True.
        """
        return True

    def update_filepath(self):
        """Update the stored filepath."""
        InputPlugin.update_filepath(self)
        self._config["filename"] = self._base_dir / self._filename

    def pre_execute(self) -> None:
        """Prepare the loader and read required metadata once."""
        InputPlugin.pre_execute(self)
        check_nxdata_adherence(
            self._config["filename"], self.get_param_value("nxdata_key")
        )
        self.set_param_value("_counted_images_per_file", self._SCAN.n_points)
        self._verify_data_shape_valid()
        self._standard_kwargs = {
            "dataset": self.get_param_value("nxdata_key"),
            # Suppress automatic metadata and import metadata once to prevent
            # parsing it for every scan point
            "import_metadata": False,
        }
        self._store_result_metadata()

    def get_filename(self, frame_index: int) -> Path:
        """
        Return the single result file regardless of the frame index.

        Parameters
        ----------
        frame_index : int
            Ignored; present only for interface compatibility.

        Returns
        -------
        Path
            The path to the pydidas result file.
        """
        return self._config["filename"]

    def get_frame(self, frame_index: int, **kwargs: Any) -> tuple[Dataset, dict]:
        """
        Load the data point for the given scan ordinal.

        Parameters
        ----------
        frame_index : int
            The scan ordinal (position in 'timeline') of the requested point.
        **kwargs : Any
            Additional keyword arguments forwarded to ``import_data``.

        Returns
        -------
        Dataset
            The data for this scan point with data-dimension axes attached.
        kwargs : dict
            The updated keyword arguments.
        """
        kwargs = kwargs | self._standard_kwargs
        kwargs["indices"] = self._SCAN.get_indices_from_ordinal(frame_index)
        _data = import_data(self._config["filename"], **kwargs)
        for _key, _val in self._config["frame_metadata"].items():
            setattr(_data, _key, _val)
        return _data, kwargs

    # ------------------------------------
    # private helper methods:
    # ------------------------------------

    def _verify_data_shape_valid(self) -> None | NoReturn:
        """Verify that the shape of the data in the file matches the scan shape."""
        _scan_ndim = self._SCAN.ndim
        _scan_shape = self._SCAN.shape
        _data_shape = get_hdf5_metadata(
            self._config["filename"], "shape", dset=self.get_param_value("nxdata_key")
        )
        _data_ndim = len(_data_shape)
        _expected_ndim = self.get_param_value("expected_data_dim")
        if not _data_shape[:_scan_ndim] == _scan_shape:
            raise UserConfigError(
                f"The imported data `{self._config['filename']}::"
                f"{self.get_param_value('nxdata_key')}` with the shape "
                f"{_data_shape} does not match the defined shape of the Scan "
                f"{_scan_shape}. Please check the input file or the Scan "
                "definition. Data import did not succeed."
            )
        if not _data_ndim - _scan_ndim == _expected_ndim:
            raise UserConfigError(
                f"The imported data `{self._config['filename']}::"
                f"{self.get_param_value('nxdata_key')}` does not match the "
                "defined number of dimensions of the results.\n\n"
                f"Expected number of dimensions: {_scan_ndim + _expected_ndim} "
                f"({_scan_ndim} scan dimensions + {_expected_ndim} data dimensions) "
                f"but received data with {_data_ndim} dimensions.\n\n"
                "Please verify the data and adjust the Parameter for the expected "
                "data dimensionality."
            )

    def _store_result_metadata(self) -> dict[str, Any]:
        """
        Read the required result metadata and store it in a dictionary.

        This method reads the metadata from the file defined in the Scan
        and stores it locally.

        Returns
        -------
        dict[str, Any]
            The metadata from the dataset to import.
        """
        try:
            _data = import_data(
                self._config["filename"],
                indices=(0,) * self._SCAN.ndim,
                dataset=self.get_param_value("nxdata_key"),
            )
        except (KeyError, FileNotFoundError, FileReadError):
            raise UserConfigError(
                f"The dataset `{self._config['filename']}::"
                f"{self.get_param_value('nxdata_key')}` could not be read as "
                "NXdata dataset. Please check the file and dataset key. "
                "\n\nThe NXdataResultLoader plugin relies on the correct metadata "
                "and will not accept non-NeXus-compliant files. "
                "If you need to import HDF5 data without metadata, please use the "
                "`Hdf5fileSeriesLoader` plugin instead."
            )
        self._config["frame_metadata"] = _data.property_dict
        self._config["frame_metadata"]["metadata"].pop("indices")
        self.output_data_label = _data.data_label
        self.output_data_unit = _data.data_unit

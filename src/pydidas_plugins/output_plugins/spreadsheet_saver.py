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
Module with the SpreadsheetSaver Plugin which can be used to save 2d data in ASCII
format with different metadata headers.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["SpreadsheetSaver"]


import numpy as np

from pydidas.core import Dataset, Parameter, UserConfigError
from pydidas.plugins import OutputPlugin


class SpreadsheetSaver(OutputPlugin):
    """
    A saver to export two-dimensional data to ASCII format.

    This class is designed to store data passed down from other processing
    plugins into Ascii files with different headers.

    Warning: This plugin will create one file for each input image and is not
    recommended at all unless other processing tools specifically require
    these individual files.

    Parameters
    ----------
    label : str
        The prefix for saving the data.
    directory_path : Path | str
        The output directory.
    """

    plugin_name = "Spreadsheet Saver"
    input_data_dim = 2
    generic_params = OutputPlugin.generic_params.copy()
    generic_params.add_param(
        Parameter(
            "header",
            str,
            "Spreadsheet (.spr)",
            choices=[
                "Spreadsheet (.spr)",
            ],
            name="Output header",
            tooltip=(
                "The output file format and header. A generic header is created "
                "based on the file type selection."
            ),
        )
    )

    def execute(self, data: Dataset | np.ndarray, **kwargs: dict):
        """
        Save data to file in raw ascii text format.

        Parameters
        ----------
        data : Dataset | np.ndarray
            The data to be stored.
        **kwargs : dict
            Any calling keyword arguments. Can be used to apply a ROI or
            binning to the raw image.

        Returns
        -------
        data : Dataset
            The input data.
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        if data.ndim != 2:
            raise UserConfigError("Only 2-d data can be saved as a spreadsheet")
        if kwargs.get("test", False):
            return data, kwargs
        self._config["global_index"] = kwargs.get("global_index", None)
        if not isinstance(data, Dataset):
            data = Dataset(data)
        if data.axis_ranges[0] is None:
            data.update_axis_range(0, np.arange(data.size))
            data.update_axis_label(0, "index")
        self._data = data
        _ext, _header = self._get_ext_and_header()
        np.savetxt(
            self.get_output_filename(_ext),
            data.array,
            header=_header,
            comments="",
        )
        return data, kwargs

    def _get_ext_and_header(self) -> tuple[str, str]:
        """
        Get the file extension and header, based on the "header" Parameter.

        Returns
        -------
        tuple[str, str]
            The file extension and the header string.
        """
        _header_type = self.get_param_value("header")
        if _header_type == "Spreadsheet (.spr)":
            return "spr", self._get_spr_header()
        raise ValueError("The header type is not supported.")

    def _get_spr_header(self) -> str:
        """
        Get the header for a textfile with metadata header.

        Returns
        -------
        _header : str
            The header string.
        """
        _header = (
            " "
            + f"{self._data.shape[1]:7d}"
            + " "
            + f"{self._data.shape[0]:7d}"
            + " Start pixel = (       1       1)"
        )
        return _header

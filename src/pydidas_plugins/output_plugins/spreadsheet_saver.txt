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

from typing import Any

import numpy as np

from pydidas.core import Dataset, Parameter, UserConfigError
from pydidas.plugins import OutputPlugin


HEADER_PARAM = Parameter(
    "header",
    str,
    "Spreadsheet (.spr)",
    choices=["Spreadsheet (.spr)", "CSV (.csv)"],
    name="Output header",
    tooltip=(
        "The output file format and header. A generic header is created "
        "based on the file type selection."
    ),
)
SIG_DIGIT_PARAM = Parameter(
    "significant_digits",
    int,
    5,
    choices=None,
    name="Significant digits",
    tooltip="The number of significant digits to be used in the output file.",
)
CAPITAL_E_NOTATION_PARAM = Parameter(
    "notation_capital_e",
    bool,
    True,
    choices=[True, False],
    name="Use capital `E` in scientific notation",
    tooltip=(
        "Use a capital E in the scientific notation (e.g. 2.422E+4). If unchecked, a "
        "lowercase `e` is used (e.g. 2.422e+4)."
    ),
)
DELIMITER_PARAM = Parameter(
    "delimiter",
    str,
    "Double space",
    choices=[
        "Single space",
        "Double space",
        "Tabulator",
        "Comma",
        "Comma and space",
        "Semicolon",
        "Semicolon and space",
    ],
    name="Delimiter",
    tooltip=(
        "The delimiter to be used in the output file to separate entries. Note that "
        "the delimiter is not used in the header."
    ),
)
FILTER_NEGATIVE_PARAM = Parameter(
    "filter_negative_values",
    bool,
    False,
    choices=[True, False],
    name="Replace negative values with zero",
    tooltip=("If checked, all negative values in the data will be replaced by zeros. "),
)


class SpreadsheetSaver(OutputPlugin):
    """
    A saver to export two-dimensional data to ASCII format.

    This class is designed to store data passed down from other processing
    plugins into ASCII files with different headers.

    Warning: This plugin will create one file for each input image and is not
    recommended at all unless other processing tools specifically require
    these individual files.
    """

    plugin_name = "Spreadsheet Saver"
    input_data_dim = 2
    generic_params = OutputPlugin.generic_params.copy()
    generic_params.add_params(
        HEADER_PARAM,
        SIG_DIGIT_PARAM,
        CAPITAL_E_NOTATION_PARAM,
        DELIMITER_PARAM,
        FILTER_NEGATIVE_PARAM,
    )
    advanced_parameters = OutputPlugin.advanced_parameters + [
        CAPITAL_E_NOTATION_PARAM.refkey,
        SIG_DIGIT_PARAM.refkey,
        DELIMITER_PARAM.refkey,
        FILTER_NEGATIVE_PARAM.refkey,
    ]

    def pre_execute(self):
        """Prepare the execution"""
        OutputPlugin.pre_execute(self)
        _sig_digits = self.get_param_value("significant_digits")
        if _sig_digits < 1:
            raise UserConfigError(
                "The number of significant digits must be at least 1."
            )
        _e_format = "E" if self.get_param_value("notation_capital_e") else "e"
        self._format = f"%.{self.get_param_value('significant_digits')}{_e_format}"
        _delimiter = self.get_param_value("delimiter")
        match _delimiter:
            case "Single space":
                self._delimiter = " "
            case "Double space":
                self._delimiter = "  "
            case "Tabulator":
                self._delimiter = "\t"
            case "Comma":
                self._delimiter = ","
            case "Comma and space":
                self._delimiter = ", "
            case "Semicolon":
                self._delimiter = ";"
            case "Semicolon and space":
                self._delimiter = "; "

    def execute(self, data: Dataset | np.ndarray, **kwargs: Any):
        """
        Save 2d data to file in raw ASCII text format.

        Parameters
        ----------
        data : Dataset | np.ndarray
            The data to be stored.
        **kwargs : Any
            Calling keyword arguments. These can be used and / or modified
            and will be passed to the next plugin in the chain.

        Returns
        -------
        data : Dataset
            The input data.
        kwargs : Any
            Calling kwargs, appended by any changes in the function.
        """
        if data.ndim != 2:
            raise UserConfigError("Only 2-d data can be saved as a spreadsheet")
        if kwargs.get("test", False):
            return data, kwargs
        if not isinstance(data, Dataset):
            data = Dataset(data)
        self._config["global_index"] = kwargs.get("global_index", None)
        if data.axis_ranges[0] is None:
            data.update_axis_range(0, np.arange(data.size))
            data.update_axis_label(0, "index")
        if self.get_param_value("filter_negative_values"):
            data[data.array < 0] = 0
        self._data = data
        _ext, _header = self._get_ext_and_header()
        np.savetxt(
            self.get_output_filename(_ext),
            data.array,
            header=_header,
            delimiter=self._delimiter,
            fmt=self._format,
            comments="",
            newline="\n ",
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
        if _header_type == "CSV (.csv)":
            return "csv", "#"
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

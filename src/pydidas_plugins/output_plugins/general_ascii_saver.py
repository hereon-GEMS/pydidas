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
Module with the GeneralAsciiSaver Plugin which can be used to save 1d data in ASCII
format with different metadata headers.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["GeneralAsciiSaver"]


import datetime
import time
from pathlib import Path
from typing import Union

import numpy as np

from pydidas.core import Dataset, Parameter, UserConfigError
from pydidas.plugins import OutputPlugin


class GeneralAsciiSaver(OutputPlugin):
    """
    An Ascii saver to export one-dimensional data.

    This class is designed to store data passed down from other processing
    plugins into Ascii files with different headers.

    Warning: This plugin will create one file for each input image and is not
    recommended at all unless other processing tools specifically require
    these individual files.

    Parameters
    ----------
    label : str
        The prefix for saving the data.
    directory_path : Union[pathlib.Path, str]
        The output directory.
    """

    plugin_name = "ASCII Saver with header"
    input_data_dim = 1
    generic_params = OutputPlugin.generic_params.copy()
    generic_params.add_param(
        Parameter(
            "header",
            str,
            "metadata header (.txt)",
            choices=[
                "metadata header (.txt)",
                "CHI header (.chi)",
                "SpecFile (.dat)",
                "no header (.txt)",
            ],
            name="Output header",
            tooltip=(
                "The output file format and header. A generic header is created "
                "based on the file type selection."
            ),
        )
    )

    def execute(self, data: Union[np.ndarray, Dataset], **kwargs: dict):
        """
        Save data to file in raw ascii text format.

        Parameters
        ----------
        data : Union[np.ndarray, pydidas.core.Dataset]
            The data to be stored.
        **kwargs : dict
            Any calling keyword arguments. Can be used to apply a ROI or
            binning to the raw image.

        Returns
        -------
        data : pydidas.core.Dataset
            The input data.
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        if data.ndim > 1:
            raise UserConfigError("Only 1-d data can be saved as ASCII")
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
        with open(self.get_output_filename(_ext), "w") as _file:
            _file.write(_header)
            for _x, _y in zip(data.axis_ranges[0], data.array):
                _file.write(f"{_x}\t{_y}\n")
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
        if _header_type == "no header (.txt)":
            return "txt", ""
        if _header_type == "metadata header (.txt)":
            return "txt", self._get_txt_header()
        if _header_type == "CHI header (.chi)":
            return "chi", self._get_chi_header()
        if _header_type == "SpecFile (.dat)":
            return "dat", self._get_specfile_header()
        raise ValueError("The header type is not supported.")

    def _get_txt_header(self) -> str:
        """
        Get the header for a textfile with metadata header.

        Returns
        -------
        _header : str
            The header string.
        """
        _header = "# Metadata:\n"
        for _key, _val in self._data.metadata:
            _header += f"# {_key}: {_val}\n"
        _header += "#\n"
        _header += f"# Axis label: {self._data.axis_labels[0]}\n"
        _header += f"# Axis unit: {self._data.axis_units[0]}\n"
        _header += "# --- end of metadata ---\n"
        _header += "# axis\tvalue\n"
        return _header

    def _get_chi_header(self) -> str:
        """
        Get the header for a .chi file.

        Returns
        -------
        str
            The header string.
        """
        return (
            Path(self.get_output_filename("dat")).name
            + "\n"
            + f"{self.data_x_label}\n"
            + f"{self.data_y_label}\n"
            + f"\t{self._data.size}\n"
        )

    def _get_specfile_header(self) -> str:
        """
        Get the header for a SpecFile .dat file.

        Returns
        -------
        str
            The header string.
        """
        _time = datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y")
        return (
            f"#F {Path(self.get_output_filename('dat')).name}\n"
            + f"#E {time.time()}\n"
            + f"#D {_time}\n\n"
            + "#S 1 pydidas results\n"
            + f"#D {_time}\n"
            + "#N 2\n"
            + f"#L {self.data_x_label} {self.data_y_label}\n"
        )

    @property
    def data_x_label(self) -> str:
        """The label for the x-axis of the data."""
        _unit = self._data.axis_units[0]
        return self._data.axis_labels[0] + (f" ({_unit})" if len(_unit) > 0 else "")

    @property
    def data_y_label(self) -> str:
        """The label for the x-axis of the data."""
        return self._data.data_label + (
            f" ({self._data.data_unit})" if len(self._data.data_unit) > 0 else ""
        )

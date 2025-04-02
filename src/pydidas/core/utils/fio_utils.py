# This file is part of pydidas.
#
# Copyright 2025, Helmholtz-Zentrum Hereon
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
Module with utilites for reading and analyzing fio files.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "update_config_from_fio_file",
    "determine_header_and_data_lines",
    "create_x_scale",
    "load_fio_spectrum",
]


from pathlib import Path

import numpy as np

from pydidas.core import Dataset, ParameterCollection
from pydidas.core.utils import CatchFileErrors


def update_config_from_fio_file(
    filename: Path | str, config: dict, params: ParameterCollection
):
    """
    Update the configuration dictionary in place with information from a fio file.

    This function will add/replace the following keys to the dictionary:

    - header_rows
    - x_unit
    - x_scale

    Parameters
    ----------
    filename : Path | str
        The filename of the file to be read.
    config : dict
        The dictionary with the configuration parameters.
    params : ParameterCollection
        The ParameterCollection with the relevant parameters to be used.
        It must include the following keys:
        - use_custom_xscale
        - x_delta
        - x_unit
        - x0_offset
    """
    _n_header, _n_data = determine_header_and_data_lines(filename)
    _unit, _scale = create_x_scale(_n_data, params)
    config["header_lines"] = _n_header
    config["data_lines"] = _n_data
    config["x_unit"] = _unit
    config["x_label"] = params.get_value("x_label")
    config["x_scale"] = _scale


def determine_header_and_data_lines(filename: Path | str) -> tuple[int, int]:
    """
    Determine the number of header and data lines in a fio file.

    Parameters
    ----------
    filename : Path | str
        The filename of the file to be read.

    Returns
    -------
    header_lines : int
        The number of header lines.
    data_lines : int
        The number of data lines.
    """
    with CatchFileErrors(filename):
        with open(filename, "r") as _f:
            _lines = _f.readlines()
    _lines_total = len(_lines)
    _n_header = _lines.index("! Data \n") + 2
    _lines = _lines[_n_header:]
    while _lines[0].strip().startswith("Col"):
        _lines.pop(0)
        _n_header += 1
    return _n_header, _lines_total - _n_header


def create_x_scale(
    n_points: int, params: ParameterCollection
) -> tuple[str, np.ndarray]:
    """
    Create an energy scale for a fio file based on the energy parameters.

    Parameters
    ----------
    n_points : int
        The number of points in the energy scale.
    params : ParameterCollection
       The ParameterCollection with the relevant parameters. It must include the
       following keys:
       - use_custom_xscale
       - x_delta
       - x_unit
       - x0_offset

    Returns
    -------
    x_unit : str
        The unit of the x-scale.
    x_scale : np.ndarray
        The x-scale.
    """
    if params.get_value("use_custom_xscale"):
        _unit = params.get_value("x_unit")
        _scale = np.arange(n_points) * params.get_value("x_delta") + params.get_value(
            "x0_offset"
        )
        return _unit, _scale
    return "channel", np.arange(n_points)


def load_fio_spectrum(filename: Path | str, config: dict) -> Dataset:
    """
    Load a spectrum from a fio file.

    Parameters
    ----------
    filename : Path | str
        The filename of the file to be read.
    config : dict
        The dictionary with the configuration parameters. It must include the
        following keys:

            header_rows : int
                The number of header rows in the file.
            x_unit : str
                The unit of the x-scale.
            x_scale : np.ndarray
                The x-scale.
            roi : slice | None
                The region of interest to be used. If None, the whole dataset is
                returned.

    Returns
    -------
    Dataset
        The imported dataset.
    """
    with CatchFileErrors(filename):
        _data = np.loadtxt(filename, skiprows=config["header_lines"])
    _dataset = Dataset(
        _data,
        axis_labels=[config["x_label"]],
        axis_units=[config["x_unit"]],
        axis_ranges=[config["x_scale"]],
    )
    if config["roi"] is not None:
        _dataset = _dataset[config["roi"]]
    return _dataset

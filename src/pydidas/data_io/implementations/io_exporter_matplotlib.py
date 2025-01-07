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
Module with the IoExporterMatplotlib class for exporting data in form of matplotlib
images.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []


from pathlib import Path
from typing import Union

import matplotlib.pyplot as plt
import numpy as np

from pydidas.core import Dataset
from pydidas.data_io.implementations.io_base import IoBase
from pydidas.data_io.utils import calculate_fig_size_arguments


class IoExporterMatplotlib(IoBase):
    """IObase implementation for matplotlib based exporters."""

    extensions_export = []
    extensions_import = []
    format_name = ""
    dimensions = [1, 2]

    @classmethod
    def export_to_file(
        cls, filename: Union[Path, str], data: np.ndarray, **kwargs: dict
    ):
        """
        Export data as a matplotlib plot.

        Parameters
        ----------
        filename : Union[pathlib.Path, str]
            The filename
        data : np.ndarray
            The data to be written to file.
        """
        if data.ndim == 1:
            cls.export_matplotlib_plot(filename, data, **kwargs)
        else:
            cls.export_matplotlib_figure(filename, data, **kwargs)

    @classmethod
    def export_matplotlib_figure(
        cls, filename: Union[Path, str], data: np.ndarray, **kwargs: dict
    ):
        """
        Export data to a matplotlib file.

        Parameters
        ----------
        filename : Union[pathlib.Path, str]
            The filename
        data : np.ndarray
            The data to be written to file.
        overwrite : bool, optional
            Flag to allow overwriting of existing files. The default is False.
        colormap : str, optional
            The colormap to be used. Must be a colormap name supported by
            matplotlib. The default is "gray"
        data_range : list, optional
            The range with lower and upper bounds for the data export.
        """
        cls.check_for_existing_file(filename, **kwargs)
        _range = cls.get_data_range(data, **kwargs)
        _cmap = kwargs.get("colormap", "gray")
        _backend = plt.get_backend()
        try:
            plt.rcParams["backend"] = "Agg"
            _figshape, _dpi = calculate_fig_size_arguments(data.shape)
            fig1 = plt.figure(figsize=_figshape, dpi=50)
            ax = fig1.add_axes([0, 0, 1, 1])
            ax.imshow(
                data, interpolation="none", vmin=_range[0], vmax=_range[1], cmap=_cmap
            )
            ax.set_xticks([])
            ax.set_yticks([])
            fig1.savefig(filename, dpi=_dpi)
            plt.close(fig1)
        finally:
            plt.rcParams["backend"] = _backend

    @classmethod
    def export_matplotlib_plot(
        cls, filename: Union[Path, str], data: np.ndarray, **kwargs: dict
    ):
        """
        Export data to a matplotlib file.

        Parameters
        ----------
        filename : Union[pathlib.Path, str]
            The filename
        data : np.ndarray
            The data to be written to file.
        overwrite : bool, optional
            Flag to allow overwriting of existing files. The default is False.
        """
        cls.check_for_existing_file(filename, **kwargs)
        _range = cls.get_data_range(data, **kwargs)
        _backend = plt.get_backend()
        try:
            plt.rcParams["backend"] = "Agg"
            _figshape, _dpi = calculate_fig_size_arguments(data.shape)
            fig1 = plt.figure(figsize=_figshape, dpi=50)
            ax = fig1.add_axes([0, 0, 1, 1])

            _x = (
                data.axis_ranges[0]
                if isinstance(data, Dataset)
                else np.arange(data.size)
            )

            ax.plot(_x, data, vmin=_range[0], vmax=_range[1])
            fig1.savefig(filename, dpi=_dpi)
            plt.close(fig1)
        finally:
            plt.rcParams["backend"] = _backend

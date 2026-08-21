# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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

"""Module with the IoExporterMatplotlib class for matplotlib-based exports."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []


from pathlib import Path
from typing import Any, ClassVar

import numpy as np

from pydidas.core import Dataset
from pydidas.core.utils import verify_is_new_file_or_replace_set
from pydidas.data_io.implementations.io_base import IoBase
from pydidas.data_io.utils import calculate_fig_size_arguments


class IoExporterMatplotlib(IoBase):
    """IObase implementation for matplotlib based exporters."""

    extensions_export: ClassVar[list[str]] = []
    extensions_import: ClassVar[list[str]] = []
    format_name: ClassVar[str] = ""
    dimensions: ClassVar[list[int]] = [1, 2]

    @staticmethod
    def export_to_file(filename: Path | str, data: np.ndarray, **kwargs: Any) -> None:
        """
        Export data as a matplotlib plot.

        Parameters
        ----------
        filename : Path or str
            The filename
        data : np.ndarray
            The data to be written to file.
        """
        if data.ndim == 1:
            IoExporterMatplotlib.export_matplotlib_plot(filename, data, **kwargs)
        else:
            IoExporterMatplotlib.export_matplotlib_figure(filename, data, **kwargs)

    @staticmethod
    def export_matplotlib_figure(
        filename: Path | str, data: np.ndarray, **kwargs: Any
    ) -> None:
        """
        Export data to a matplotlib file.

        Parameters
        ----------
        filename : Path or str
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
        verify_is_new_file_or_replace_set(filename, **kwargs)
        import matplotlib.pyplot as plt

        _data_range = IoExporterMatplotlib.get_data_range(data, **kwargs)
        _cmap = kwargs.get("colormap", "gray")
        _backend = plt.get_backend()
        try:
            plt.rcParams["backend"] = "Agg"
            _figshape, _dpi = calculate_fig_size_arguments(data.shape)
            fig1 = plt.figure(figsize=_figshape, dpi=50)
            ax = fig1.add_axes([0, 0, 1, 1])
            ax.imshow(
                data,
                interpolation="none",
                vmin=_data_range[0],
                vmax=_data_range[1],
                cmap=_cmap,
            )
            ax.set_xticks([])
            ax.set_yticks([])
            fig1.savefig(filename, dpi=_dpi)
            plt.close(fig1)
        finally:
            plt.rcParams["backend"] = _backend

    @staticmethod
    def export_matplotlib_plot(
        filename: Path | str, data: np.ndarray, **kwargs: Any
    ) -> None:
        """
        Export data to a matplotlib file.

        Parameters
        ----------
        filename : Path or str
            The filename
        data : np.ndarray
            The data to be written to file.
        overwrite : bool, optional
            Flag to allow overwriting of existing files. The default is False.
        """
        verify_is_new_file_or_replace_set(filename, **kwargs)
        import matplotlib.pyplot as plt

        _data_range = IoExporterMatplotlib.get_data_range(data, **kwargs)
        _backend = plt.get_backend()
        try:
            plt.rcParams["backend"] = "Agg"
            # artificially set the size to a 60:100 ratio for 1D plots
            _figshape, _dpi = calculate_fig_size_arguments((60, 100))
            fig1, ax = plt.subplots(figsize=_figshape, dpi=50)

            _x = (
                data.axis_ranges[0]
                if isinstance(data, Dataset)
                else np.arange(data.size)
            )

            ax.plot(_x, data)
            ax.set_ylim(*_data_range)
            fig1.savefig(filename, dpi=_dpi)
            plt.close(fig1)
        finally:
            plt.rcParams["backend"] = _backend

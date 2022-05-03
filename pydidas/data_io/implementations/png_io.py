# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the PngIo class for exporting png data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

import numpy as np
import matplotlib.pyplot as plt

from ..utils import calculate_fig_size_arguments
from .io_base import IoBase


class PngIo(IoBase):
    """IObase implementation for png files."""
    extensions_export = ['.png']
    extensions_import = []
    format_name = 'Png'
    dimensions = [2]

    @classmethod
    def export_to_file(cls, filename, data, **kwargs):
        """
        Export data to a png file.

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
        """
        cls.check_for_existing_file(filename, **kwargs)
        _cmap = kwargs.get('colormap', 'gray')
        _backend = plt.get_backend()
        try:
            plt.rcParams['backend'] = 'Agg'
            _figshape, _dpi = calculate_fig_size_arguments(data.shape)
            fig1 = plt.figure(figsize=_figshape, dpi=50)
            ax = fig1.add_axes([0, 0, 1, 1])
            ax.imshow(data, interpolation='none', vmin=np.amin(data),
                      vmax=np.amax(data), cmap=_cmap)
            ax.set_xticks([])
            ax.set_yticks([])
            fig1.savefig(filename, dpi=_dpi)
            plt.close(fig1)
        finally:
            plt.rcParams['backend'] = _backend

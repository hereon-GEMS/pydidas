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
Module with the JpegIo class for exporting data to JPEG files.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

from ...core.constants import JPG_EXTENSIONS
from .io_exporter_matplotlib import IoExporterMatplotlib


class JpegIo(IoExporterMatplotlib):
    """IObase implementation for jpeg files."""

    extensions_export = JPG_EXTENSIONS
    extensions_import = []
    format_name = "jpeg"
    dimensions = [2]

    @classmethod
    def export_to_file(cls, filename, data, **kwargs):
        """
        Export data to a jpeg file.

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
        cls.export_matplotlib_figure(filename, data, **kwargs)
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
Module with the FrameLoader Plugin which can be used to load files with
single images in each, e.g. tiff files or numpy files.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["FrameLoader"]


from pydidas.core import Dataset
from pydidas.data_io import import_data
from pydidas.plugins import InputPlugin


class FrameLoader(InputPlugin):
    """
    Load 2d data frames from files with a single image in each, for example tif files.

    This class is designed to load data from a series of files. The file
    series is defined through the first and last file and file stepping.
    Filesystem checks can be disabled using the live_processing keyword but
    are enabled by default.

    A region of interest and image binning can be supplied to apply directly
    to the raw image.
    """

    plugin_name = "Single frame loader"

    def get_frame(self, frame_index: int, **kwargs: dict) -> tuple[Dataset, dict]:
        """
        Load a frame and pass it on.

        Parameters
        ----------
        frame_index : int
            The frame index.
        **kwargs : dict
            Any calling keyword arguments. Can be used to apply a ROI or
            binning to the raw image.

        Returns
        -------
        _data : pydidas.core.Dataset
            The image data.
        kwargs : dict
            The updated calling keyword arguments.
        """
        _fname = self.get_filename(frame_index)
        kwargs["roi"] = self._get_own_roi()
        _data = import_data(_fname, **kwargs)
        _data.axis_units = ["pixel", "pixel"]
        _data.axis_labels = ["detector y", "detector x"]
        return _data, kwargs

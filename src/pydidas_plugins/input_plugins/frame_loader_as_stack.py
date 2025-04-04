# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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

__author__ = "Nonni Heere, Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["FrameLoaderAsStack"]


import numpy as np

from pydidas.core import (
    Dataset,
    FileReadError,
    UserConfigError,
    get_generic_param_collection,
)
from pydidas.data_io import import_data
from pydidas.plugins import InputPlugin


class FrameLoaderAsStack(InputPlugin):
    """
    Load a series of 2d data frames from files with a single image in each.

    This plugin can be used to apply a rolling average on input data.

    NOTE: The FrameStackLoader Plugin is used to load a series of data
    frames into a single 3D Dataset for further special analysis. Note
    that this plugin should only be used if the next processing step is
    to apply individual masks or to average / sum the frames.

    This class is designed to load data from a series of files. The file
    series is defined through the first and last file and file stepping.
    Filesystem checks can be disabled using the live_processing keyword
    but are enabled by default.

    A region of interest and image binning can be supplied to apply
    directly to the raw image.
    """

    plugin_name = "Single frame *stack* loader"
    default_params = get_generic_param_collection("num_frames_to_use")
    output_data_dim = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._roi_data_dim = 2

    def get_frame(self, frame_index: int, **kwargs: dict) -> tuple[Dataset, dict]:
        """
        Load a frame stack and pass it on.

        Parameters
        ----------
        frame_index : int
            The frame index.
        **kwargs : dict
            Any calling keyword arguments. Can be used to apply a ROI or
            binning to the raw image.

        Returns
        -------
        new_data : pydidas.core.Dataset
            The 3d image data.
        kwargs : dict
            The updated calling keyword arguments.
        """
        num_frames_to_use = self.get_param_value("num_frames_to_use")
        if num_frames_to_use < 1:
            raise UserConfigError("Frame count must be at least 1.")
        _stack = None
        kwargs["roi"] = self._get_own_roi()
        for i in range(num_frames_to_use):
            _fname = self.get_filename(frame_index + i)
            try:
                _fdata = import_data(_fname, **kwargs)
            except FileReadError:
                raise UserConfigError(
                    f"File {self.get_filename(frame_index + i)} not found. "
                    "\n\nTry setting number of scan points to "
                    f"{frame_index - num_frames_to_use + i} or lowering frame count "
                    f"to {num_frames_to_use - 1}"
                )
            _fdata.axis_units = ["pixel", "pixel"]
            _fdata.axis_labels = ["detector y", "detector x"]
            if _stack is None:
                _stack = np.zeros((num_frames_to_use, *_fdata.shape))
            _stack[i] = _fdata

        data_kwargs = {
            "axis_labels": ["image number"] + list(_fdata.axis_labels.values()),
            "axis_ranges": [None] + list(_fdata.axis_ranges.values()),
            "axis_units": [""] + list(_fdata.axis_units.values()),
            "data_label": _fdata.data_label,
            "data_unit": _fdata.data_unit,
        }
        new_data = Dataset(_stack, **data_kwargs)
        return new_data, kwargs

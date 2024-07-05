# This file is part of pydidas.
#
# Copyright 2024, Helmholtz-Zentrum Hereon
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

__author__ = "Nonni Heere"
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["FrameStackLoader"]


import numpy as np

from pydidas.core import (
    Dataset,
    FileReadError,
    Parameter,
    ParameterCollection,
    UserConfigError,
)
from pydidas.core.constants import INPUT_PLUGIN
from pydidas.data_io import import_data
from pydidas.plugins import InputPlugin


class FrameStackLoader(InputPlugin):
    """
    Load data frames from files with a single image in each, for example tif files.

    This class is designed to load data from a series of files. The file
    series is defined through the first and last file and file stepping.
    Filesystem checks can be disabled using the live_processing keyword but
    are enabled by default.

    A region of interest and image binning can be supplied to apply directly
    to the raw image.
    """

    plugin_name = "Frame stack loader"
    basic_plugin = False
    plugin_type = INPUT_PLUGIN
    default_params = ParameterCollection(
        Parameter(
            "frame_count",
            int,
            3,
            name="Frame count",
            tooltip="How many frames should be included in the stack.",
        )
    )
    input_data_dim = None
    output_data_dim = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._roi_data_dim = 2

    def calculate_result_shape(self):
        """
        Calculate the shape of the Plugin's results.
        """
        self.update_filename_string()
        self._image_metadata.update(filename=self.get_filename(0))
        self._config["result_shape"] = (
            self.get_param_value("frame_count"),
            *self._image_metadata.final_shape,
        )
        self._original_input_shape = (
            self._image_metadata.raw_size_y,
            self._image_metadata.raw_size_x,
        )

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
        frame_count = self.get_param_value("frame_count")
        if frame_count < 1:
            raise UserConfigError("Frame count must be at least 1.")
        _stack = None
        for i in range(frame_count):
            _fname = self.get_filename(frame_index + i)
            try:
                _fdata = import_data(_fname, **kwargs)
            except FileReadError:
                raise UserConfigError(
                    f"""File {self.get_filename(frame_index + i)} not found.
                    
                    Try setting number of scan points to {frame_index - frame_count + i}
                    or lowering frame count to {frame_count - 1}"""
                )
            _fdata.axis_units = ["pixel", "pixel"]
            _fdata.axis_labels = ["detector y", "detector x"]
            if _stack is None:
                _stack = Dataset(np.zeros((frame_count, *_fdata.shape)))
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

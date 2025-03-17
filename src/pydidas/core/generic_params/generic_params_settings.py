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
The generic_params_settings module holds all the required data to create generic
Parameters for the global pydidas settings
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["GENERIC_PARAMS_SETTINGS"]


GENERIC_PARAMS_SETTINGS = {
    "mp_n_workers": {
        "type": int,
        "default": 4,
        "name": "Number of MP workers",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The number of multiprocessing workers. Note that this number should "
            "not be set too high for two reasons:\n1. File reading processes "
            "interfere with each other if too many are active at once.\n2. pyFAI "
            "already inherently uses parallelization and you can only gain limited "
            "performance increases for multiple parallel processes."
        ),
    },
    "data_buffer_size": {
        "type": float,
        "default": 1500,
        "name": "Data buffer size",
        "choices": None,
        "unit": "MB",
        "allow_None": False,
        "tooltip": (
            "The maximum size of the data buffer (for each display widget). "
            "Any data which is smaller than the buffer size will be stored in "
            "memory. Larger data will be read from disk in chunks."
        ),
    },
    "shared_buffer_size": {
        "type": float,
        "default": 100,
        "name": "Shared buffer size limit",
        "choices": None,
        "unit": "MB",
        "allow_None": False,
        "tooltip": (
            "A shared buffer is used to efficiently transport data between the "
            "main App and multiprocessing Processes. This buffer must be large "
            "enough to store at least one instance of all result data."
        ),
    },
    "shared_buffer_max_n": {
        "type": int,
        "default": 20,
        "name": "Buffer dataframe limit",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The maximum number of datasets in the buffer. A dataset consists of "
            "all results for one frame. For performance reasons, the buffer should "
            "not be too large."
        ),
    },
    "max_image_size": {
        "type": float,
        "default": 100,
        "name": "Maximum image size",
        "choices": None,
        "unit": "Mpx",
        "allow_None": False,
        "tooltip": "The maximum size (in megapixels) of images.",
    },
    "use_detector_mask": {
        "type": bool,
        "default": False,
        "name": "Use detector mask",
        "choices": [True, False],
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "Flag to use a detector mask file and value. If False, no detector mask "
            "will be used."
        ),
    },
    "detector_mask_val": {
        "type": float,
        "default": 0,
        "name": "Masked pixels display value",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The value to be used for the pixels masked on the detector. Note that "
            "this value will only be used for displaying the images. For pyFAI "
            "integration, the pixels will be fully masked and not be included."
        ),
    },
    "mosaic_border_width": {
        "type": int,
        "default": 0,
        "name": "Mosaic tiling border width",
        "choices": None,
        "unit": "px",
        "allow_None": False,
        "tooltip": (
            "The width of the border inserted between adjacent frames"
            " in the mosaic creation."
        ),
    },
    "mosaic_border_value": {
        "type": float,
        "default": 0,
        "name": "Mosaic border value",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "The value to be put in the border pixels in mosaics.",
    },
    "run_type": {
        "type": str,
        "default": "Process in GUI",
        "name": "Run type",
        "choices": ["Process in GUI", "Command line"],
        "unit": "",
        "allow_None": False,
        "tooltip": "Specify how the processing shall be performed.",
    },
    "plugin_path": {
        "type": str,
        "default": "",
        "name": "Custom plugin paths",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The paths to all custom plugin locations. Individual entries must be "
            "separated by a double semicolon `;;`."
        ),
    },
    "plot_update_time": {
        "type": float,
        "default": 1.0,
        "name": "Plot update time",
        "choices": None,
        "allow_None": False,
        "unit": "s",
        "tooltip": (
            "The delay before any plot updates will be processed. This"
            " will prevent multiple frequent update of plots."
        ),
    },
    "max_number_curves": {
        "type": int,
        "default": 40,
        "name": "Maximum number of curves",
        "choices": None,
        "allow_None": False,
        "unit": "",
        "tooltip": (
            "The maximum number of curves to plot. Increasing this number will "
            "allow more curves to be plotted simultaneously, but at the cost of "
            "significant performance decrease."
        ),
    },
    "histogram_outlier_fraction_high": {
        "type": float,
        "default": 0.07,
        "name": "Histogram outlier fraction (high)",
        "choices": None,
        "allow_None": False,
        "unit": "",
        "tooltip": (
            "The fraction of pixels with high values which will be ignored when "
            "cropping the histogram for 2d plots. A value of 0.07 will mask all sensor "
            "gaps in the Eiger detector."
        ),
    },
    "histogram_outlier_fraction_low": {
        "type": float,
        "default": 0.02,
        "name": "Histogram outlier fraction (low)",
        "choices": None,
        "allow_None": False,
        "unit": "",
        "tooltip": (
            "The fraction of pixels with low values which will be ignored when "
            "cropping the histogram for 2d plots. "
        ),
    },
    "cmap_name": {
        "type": str,
        "default": "Gray",
        "name": "Default colormap",
        "choices": None,
        "allow_None": False,
        "unit": "",
        "tooltip": "The default colormap used in pydidas plots.",
    },
    "cmap_nan_color": {
        "type": str,
        "default": "#9AFEFF",
        "name": "Color for invalid data / no data",
        "choices": None,
        "allow_None": False,
        "unit": "",
        "tooltip": (
            "The RGB color used to fill missing or invalid data points. Invalid data "
            "points are labeled with np.NaN values."
        ),
    },
}

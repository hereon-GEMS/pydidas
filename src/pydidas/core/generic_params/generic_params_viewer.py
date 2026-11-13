# This file is part of pydidas.
#
# Copyright 2026, Helmholtz-Zentrum Hereon
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
The generic_params_viewer module holds all the required data to create generic
Parameters which are used for viewing images in the PyQtGraphImageViewer.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["GENERIC_PARAMS_VIEWER"]


GENERIC_PARAMS_VIEWER = {
    "colormap_val_low": {
        "type": float,
        "default": None,
        "name": "Lower display threshold",
        "choices": None,
        "unit": "",
        "allow_None": True,
        "tooltip": (
            "The lower display threshold of the image. If any finite value (i.e. "
            "not np.nan or None) is used, this value will set the lower threshold "
            "for the colormap. Any pixels with values below the threshold will be "
            "displayed in the lowest color of the colormap. If None, the minimum"
            "value of the image will be used automatically."
        ),
    },
    "colormap_val_high": {
        "type": float,
        "default": None,
        "name": "Upper display threshold",
        "choices": None,
        "unit": "",
        "allow_None": True,
        "tooltip": (
            "The upper display threshold of the image. If any finite value (i.e. "
            "not np.nan or None) is used, this value will set the upper threshold "
            "for the colormap. Any pixels with values above the threshold will be "
            "displayed in the highest color of the colormap. If None, the maximum "
            "value of the image will be used automatically."
        ),
    },
    "zoom_xlow": {
        "type": int,
        "default": 0,
        "name": "Zoom lower x limit",
        "choices": None,
        "unit": "px",
        "allow_None": False,
        "tooltip": "The lower x limit of the zoomed image.",
    },
    "zoom_xhigh": {
        "type": int,
        "default": None,
        "name": "Zoom upper x limit",
        "choices": None,
        "unit": "px",
        "allow_None": True,
        "tooltip": "The upper x limit of the zoomed image.",
    },
    "zoom_ylow": {
        "type": int,
        "default": 0,
        "name": "Zoom lower y limit",
        "choices": None,
        "unit": "px",
        "allow_None": False,
        "tooltip": "The lower y limit of the zoomed image.",
    },
    "zoom_yhigh": {
        "type": int,
        "default": None,
        "name": "Zoom upper y limit",
        "choices": None,
        "unit": "px",
        "allow_None": True,
        "tooltip": "The upper y limit of the zoomed image.",
    },
    "image_stats_min": {
        "type": float,
        "default": 0,
        "name": "Minimum value",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The minimum value in the image. This value is calculated from the "
            "image data and is not user-settable."
        ),
    },
    "image_stats_max": {
        "type": float,
        "default": 0,
        "name": "Maximum value",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The maximum value in the image. This value is calculated from the "
            "image data and is not user-settable."
        ),
    },
    "image_stats_mean": {
        "type": float,
        "default": 0,
        "name": "Mean value",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The mean value in the image. This value is calculated from the "
            "image data and is not user-settable."
        ),
    },
    "image_stats_std": {
        "type": float,
        "default": 0,
        "name": "Standard deviation",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The standard deviation in the image. This value is calculated from the "
            "image data and is not user-settable."
        ),
    },
    "marker_lock": {
        "type": bool,
        "default": False,
        "name": "Lock marker position",
        "choices": [True, False],
        "unit": "",
        "allow_None": False,
        "tooltip": ("Lock the marker position. If locked, the marker cannot be moved "),
    },
    "marker_x": {
        "type": int,
        "default": 0,
        "name": "Marker x position",
        "choices": None,
        "unit": "px",
        "allow_None": False,
        "tooltip": "The x position of the marker.",
    },
    "marker_y": {
        "type": int,
        "default": 0,
        "name": "Marker y position",
        "choices": None,
        "unit": "px",
        "allow_None": False,
        "tooltip": "The y position of the marker.",
    },
    "use_scale": {
        "type": str,
        "default": "linear",
        "name": "Scale for image",
        "choices": ["linear", "logarithmic", "arcsinh"],
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The scale to use for the image. Arcsinh is a scale which is fairly "
            "similar to logarithmic, but can handle negative values."
        ),
    },
}

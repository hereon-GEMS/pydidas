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
The generic_params_image_ops module holds all the required data to create generic
Parameters for image operations like binning and cropping.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["GENERIC_PARAMS_IMAGE_OPS"]


from numpy import float32


GENERIC_PARAMS_IMAGE_OPS = {
    "use_roi": {
        "type": int,
        "default": 0,
        "name": "Use ROI",
        "choices": [True, False],
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "Keyword to toggle use of the ROI for cropping the original images "
            "before processing them."
        ),
    },
    "roi_xlow": {
        "type": int,
        "default": 0,
        "name": "ROI lower x limit",
        "choices": None,
        "unit": "px",
        "allow_None": False,
        "tooltip": (
            "The lower boundary (in pixel) for cropping images in x, if use_roi is "
            "enabled. Negative values will be modulated with the image width."
        ),
    },
    "roi_xhigh": {
        "type": int,
        "default": None,
        "name": "ROI upper x limit",
        "choices": None,
        "unit": "px",
        "allow_None": True,
        "tooltip": (
            "The upper boundary (in pixel) for cropping images in x, if use_roi is "
            "enabled. Negative values will be modulated with the image width, i.e. "
            "-1 is equivalent with the full image size minus 1. To take the full "
            "image, use 'None' as value for the upper ROI limit."
        ),
    },
    "roi_ylow": {
        "type": int,
        "default": 0,
        "name": "ROI lower y limit",
        "choices": None,
        "unit": "px",
        "allow_None": False,
        "tooltip": (
            "The lower boundary (in pixel) for cropping images in y, if use_roi is "
            "enabled. Negative values will be modulated with the image width."
        ),
    },
    "roi_yhigh": {
        "type": int,
        "default": None,
        "name": "ROI upper y limit",
        "choices": None,
        "unit": "px",
        "allow_None": True,
        "tooltip": (
            "The upper boundary (in pixel) for cropping images in y, if use_roi is "
            "enabled. Negative values will be modulated with the image width, i.e. "
            "-1 is equivalent with the full image size minus 1. To take the full "
            "image, use 'None' as value for the upper ROI limit."
        ),
    },
    "use_thresholds": {
        "type": int,
        "default": 0,
        "name": "Use thresholds",
        "choices": [True, False],
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "Keyword to toggle use of the thresholds for clipping the data range "
            "in the original images before combining them."
        ),
    },
    "threshold_low": {
        "type": float,
        "default": None,
        "name": "Lower threshold",
        "choices": None,
        "unit": "",
        "allow_None": True,
        "tooltip": (
            "The lower threshold of the image. If any finite value (i.e. not "
            "np.nan or None) is used, the value of any pixels with a value below "
            "the threshold will be replaced by the threshold value. A value of "
            "np.nan or None will ignore the threshold."
        ),
    },
    "threshold_high": {
        "type": float,
        "default": None,
        "name": "Upper threshold",
        "choices": None,
        "unit": "",
        "allow_None": True,
        "tooltip": (
            "The upper threshold of the image. If any finite value (i.e. not "
            "np.nan or None) is used, the value of any pixels with a value below "
            "the threshold will be replaced by the threshold value. A value of "
            "np.nan or None will ignore the threshold."
        ),
    },
    "binning": {
        "type": int,
        "default": 1,
        "name": "Binning factor",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The re-binning factor for the images in the composite. "
            "The binning will be applied to the cropped images."
        ),
    },
    "image_shape": {
        "type": tuple,
        "default": (0, 0),
        "name": "Image shape",
        "choices": None,
        "unit": "px",
        "allow_None": False,
        "tooltip": "The shape of an image.",
    },
    "raw_image_shape": {
        "type": tuple,
        "default": (0, 0),
        "name": "Raw image shape",
        "choices": None,
        "unit": "px",
        "allow_None": False,
        "tooltip": "The image shape of the original image as loaded from the file.",
    },
    "datatype": {
        "type": None,
        "default": float32,
        "name": "Datatype",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "The datatype.",
    },
    "multiplicator": {
        "type": float,
        "default": 1.0,
        "name": "Multiplication factor",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The multiplication scaling factor to be applied to the resulting Dataset."
        ),
    },
}

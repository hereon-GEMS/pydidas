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
The generic_params_experiment module holds all the required data to create generic
Parameters for the experiment context.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["GENERIC_PARAMS_EXPERIMENT"]


GENERIC_PARAMS_EXPERIMENT = {
    "xray_wavelength": {
        "type": float,
        "default": 1,
        "name": "X-ray wavelength",
        "choices": None,
        "unit": "A",
        "allow_None": False,
        "tooltip": (
            "The X-ray wavelength. Any changes to the wavelength will"
            " also update the X-ray energy setting."
        ),
    },
    "xray_energy": {
        "type": float,
        "default": 12.398,
        "name": "X-ray energy",
        "choices": None,
        "unit": "keV",
        "allow_None": False,
        "tooltip": (
            "The X-ray energy. Changing this parameter will also "
            "update the X-ray wavelength setting."
        ),
    },
    "detector_name": {
        "type": str,
        "default": "detector",
        "name": "Detector name",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "The detector name in pyFAI nomenclature.",
    },
    "detector_npixx": {
        "type": int,
        "default": 0,
        "name": "Detector size X",
        "choices": None,
        "unit": "px",
        "allow_None": False,
        "tooltip": "The number of detector pixels in x direction (horizontal).",
    },
    "detector_npixy": {
        "type": int,
        "default": 0,
        "name": "Detector size Y",
        "choices": None,
        "unit": "px",
        "allow_None": False,
        "tooltip": "The number of detector pixels in x direction (vertical).",
    },
    "detector_pxsizex": {
        "type": float,
        "default": 100,
        "name": "Detector pixel size X",
        "choices": None,
        "unit": "um",
        "allow_None": False,
        "tooltip": "The detector pixel size in X-direction.",
    },
    "detector_pxsizey": {
        "type": float,
        "default": 100,
        "name": "Detector pixel size Y",
        "choices": None,
        "unit": "um",
        "allow_None": False,
        "tooltip": "The detector pixel size in Y-direction.",
    },
    "detector_pxsize": {
        "type": float,
        "default": 100,
        "name": "Detector pixel size",
        "choices": None,
        "unit": "um",
        "allow_None": False,
        "tooltip": "The detector pixel size in both X- and Y-direction.",
    },
    "detector_dist": {
        "type": float,
        "default": 1,
        "name": "Sample-detector distance",
        "choices": None,
        "unit": "m",
        "allow_None": False,
        "tooltip": "The sample-detector distance.",
    },
    "detector_mask_file": {
        "type": "Path",
        "default": "",
        "name": "Detector mask file",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "The path to the detector mask file.",
    },
    "detector_poni1": {
        "type": float,
        "default": 0,
        "name": "Detector PONI1",
        "choices": None,
        "unit": "m",
        "allow_None": False,
        "tooltip": (
            "The detector PONI1 (point of normal incidence; in y direction). This "
            "is measured in meters from the detector origin."
        ),
    },
    "detector_poni2": {
        "type": float,
        "default": 0,
        "name": "Detector PONI2",
        "choices": None,
        "unit": "m",
        "allow_None": False,
        "tooltip": (
            "The detector PONI2 (point of normal incidence; in x direction). This "
            "is measured in meters from the detector origin."
        ),
    },
    "detector_rot1": {
        "type": float,
        "default": 0,
        "name": "Detector Rot1",
        "choices": None,
        "unit": "rad",
        "allow_None": False,
        "tooltip": 'The detector rotation 1 (lefthanded around the "up"-axis)',
    },
    "detector_rot2": {
        "type": float,
        "default": 0,
        "name": "Detector Rot2",
        "choices": None,
        "unit": "rad",
        "allow_None": False,
        "tooltip": (
            "The detector rotation 2 (pitching the detector; positive direction is "
            "tilting the detector top upstream while keeping the bottom of the "
            "detector stationary."
        ),
    },
    "detector_rot3": {
        "type": float,
        "default": 0,
        "name": "Detector Rot3",
        "choices": None,
        "unit": "rad",
        "allow_None": False,
        "tooltip": (
            "The detector rotation 3 (around the beam axis; right-handed when "
            "looking downstream with the beam.)"
        ),
    },
    "beamcenter_x": {
        "type": float,
        "default": 0,
        "name": "Beamcenter x",
        "choices": None,
        "unit": "px",
        "allow_None": False,
        "tooltip": "The detector x-coordinate for the beamcenter.",
    },
    "beamcenter_y": {
        "type": float,
        "default": 0,
        "name": "Beamcenter y",
        "choices": None,
        "unit": "px",
        "allow_None": False,
        "tooltip": "The detector y-coordinate for the beamcenter.",
    },
    "detector_tilt_angle": {
        "type": float,
        "default": 0,
        "name": "detector tilt angle",
        "choices": None,
        "unit": "deg",
        "allow_None": False,
        "tooltip": "The detector tilt angle (relative to the beam normal).",
    },
    "detector_tilt_plane": {
        "type": float,
        "default": 0,
        "name": "detector tilt plane",
        "choices": None,
        "unit": "deg",
        "allow_None": False,
        "tooltip": "The detector tilt plane orientation (relative to positive x-axis).",
    },
    "detector_dist_fit2d": {
        "type": float,
        "default": 1,
        "name": "Sample-detector distance",
        "choices": None,
        "unit": "mm",
        "allow_None": False,
        "tooltip": "The sample-detector distance.",
    },
}

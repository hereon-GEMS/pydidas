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
The generic_params_pyfai module holds all the required data to create generic
Parameters for pyFAI integrations.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["GENERIC_PARAMS_PYFAI"]


GENERIC_PARAMS_PYFAI = {
    "rad_npoint": {
        "type": int,
        "default": 1000,
        "name": "Num points radial integration",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The number of bins in radial direction for the pyFAI integration."
        ),
    },
    "rad_unit": {
        "type": str,
        "default": "2theta / deg",
        "name": "Radial unit",
        "choices": ["Q / nm^-1", "Q / A^-1", "r / mm", "2theta / deg", "2theta / rad"],
        "unit": "",
        "allow_None": False,
        "tooltip": "The unit and type of the azimuthal profile.",
    },
    "rad_use_range": {
        "type": str,
        "default": "Full detector",
        "name": "Radial range",
        "choices": ["Full detector", "Specify radial range"],
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "Toggle to limit the radial integration range or use the full data "
            "range. If 'Specify radial range' is used, boundaries need to be defined "
            "in the lower and upper radial range Parameters."
        ),
    },
    "rad_range_lower": {
        "type": float,
        "default": 0,
        "name": "Radial lower range",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The lower boundary of the radial integration range. This setting is "
            "only used if the 'Specify radial range' is set. This value needs to be "
            "given in the unit selected as radial unit."
        ),
    },
    "rad_range_upper": {
        "type": float,
        "default": 0,
        "name": "Radial upper range",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The upper boundary of the radial integration range. This setting is "
            "only used if 'Specify radial range' is set. This value needs to be "
            "given in the unit selected as radial unit."
        ),
    },
    "azi_npoint": {
        "type": int,
        "default": 1000,
        "name": "Num points azimuthal integration",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The number of bins in azimuthal direction for the pyFAI integration."
        ),
    },
    "azi_unit": {
        "type": str,
        "default": "chi / deg",
        "name": "Azimuthal unit",
        "choices": ["chi / deg", "chi / rad"],
        "unit": "",
        "allow_None": False,
        "tooltip": "The unit and type of the azimuthal profile.",
    },
    "azi_use_range": {
        "type": str,
        "default": "Full detector",
        "name": "Azimuthal range",
        "choices": ["Full detector", "Specify azimuthal range"],
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "Toggle to limit the azimuthal integration range or use the full data "
            "range. If 'Specify azimuthal range' is used, boundaries need to be "
            "defined in the lower and upper azimuthal range Parameters."
        ),
    },
    "azi_range_lower": {
        "type": float,
        "default": 0,
        "name": "Azimuthal lower range",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The lower boundary of the azimuthal integration range. This setting "
            "is only used if 'Specify azimuthal range' is set. This value needs to be "
            "given in the unit selected as azimuthal unit."
        ),
    },
    "azi_range_upper": {
        "type": float,
        "default": 0,
        "name": "Azimuthal upper range",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The upper boundary of the azimuthal integration range. This setting "
            "is only used if 'Specify azimuthal range' is set. This value needs to be "
            "given in the unit selected as azimuthal unit."
        ),
    },
    "azi_sector_width": {
        "type": float,
        "default": 20,
        "name": "Azimuthal sector width",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "The width of each azimuthal sector (in azimuthal units).",
    },
    "azi_sector_centers": {
        "type": str,
        "default": "0; 90; 180; 270",
        "name": "Azimuthal sector centers",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The centers of the azimuthal sectors to be integrated (in azimuthal "
            "units). Separate multiple sectors by semicolons."
        ),
    },
    "int_method": {
        "type": str,
        "default": "CSR",
        "name": "PyFAI integration method",
        "choices": [
            "CSR",
            "CSR OpenCL",
            "CSR full",
            "CSR full OpenCL",
            "LUT",
            "LUT OpenCL",
            "LUT full",
            "LUT full OpenCL",
        ],
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The integration method. For a full reference, please"
            " visit the pyfai documentation available at: "
            "https://pyfai.readthedocs.io/"
        ),
    },
    "integration_direction": {
        "type": str,
        "default": "Azimuthal integration",
        "name": "Integration direction",
        "choices": [
            "Azimuthal integration",
            "Radial integration",
            "2D integration",
        ],
        "unit": "",
        "allow_None": False,
        "tooltip": "The integration direction.",
    },
    "detector_model": {
        "type": str,
        "default": "Custom detector",
        "name": "Detector model",
        "choices": ["Custom detector"],
        "unit": "",
        "allow_None": None,
        "tooltip": "The model name of the detector.",
    },
    "polarization_factor": {
        "type": float,
        "default": 0.99,
        "name": "Polarization factor",
        "choices": None,
        "unit": "",
        "allow_None": True,
        "tooltip": (
            "The Polarization factor. Must be a number between -1 (vertical) and +1 "
            "(horizontal). 0 corresponds to circular polarizazion, None corresponds to "
            "no correction."
        ),
    },
    "correct_solid_angle": {
        "type": bool,
        "default": True,
        "name": "Correct solid angle",
        "choices": [True, False],
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The correct solid angle Parameter in pyFAI (de)activates the correction "
            "for the solid angle of the detector pixels. Detector pixels further away "
            "from the beam axis see a smaller projected intensity. Using this "
            "parameter allows to correct for this effect, if set to True."
        ),
    },
}

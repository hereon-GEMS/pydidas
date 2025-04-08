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
The pyfai_names module holds names (constants) extracted from pyFAI.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "PYFAI_DETECTOR_MANUFACTURERS",
    "PYFAI_DETECTOR_NAMES",
    "PYFAI_MANUFACTURERS_OF_DETECTORS",
    "PYFAI_SHAPES_OF_DETECTOR_MODELS",
    "PYFAI_DETECTOR_MODELS_OF_SHAPES",
    "pyFAI_UNITS",
    "pyFAI_METHOD",
]


import pyFAI.detectors as __det


__class_names = __det._detector_class_names


pyFAI_UNITS = {
    "Q / nm^-1": "q_nm^-1",
    "Q / A^-1": "q_A^-1",
    "2theta / deg": "2th_deg",
    "2theta / rad": "2th_rad",
    "r / mm": "r_mm",
    "chi / deg": "chi_deg",
    "chi / rad": "chi_rad",
}

pyFAI_METHOD = {
    "CSR": ("bbox", "csr", "cython"),
    "CSR OpenCL": ("bbox", "csr", "opencl"),
    "CSR full": ("full", "csr", "cython"),
    "CSR full OpenCL": ("full", "csr", "opencl"),
    "LUT": ("bbox", "lut", "cython"),
    "LUT OpenCL": ("bbox", "lut", "opencl"),
    "LUT full": ("full", "lut", "cython"),
    "LUT full OpenCL": ("full", "lut", "opencl"),
}


PYFAI_DETECTOR_MANUFACTURERS = set()
PYFAI_DETECTOR_NAMES = set()
PYFAI_MANUFACTURERS_OF_DETECTORS = {}
PYFAI_SHAPES_OF_DETECTOR_MODELS = {}
PYFAI_DETECTOR_MODELS_OF_SHAPES = {}

for __name in __class_names:
    __cls = getattr(__det, __name)
    __manufacturer = "Custom" if __cls.MANUFACTURER is None else __cls.MANUFACTURER
    if isinstance(__manufacturer, list):
        __manufacturer = " / ".join(__manufacturer)
    __model = __cls.aliases
    if len(__model) > 0:
        PYFAI_DETECTOR_NAMES.update(__model)
        PYFAI_MANUFACTURERS_OF_DETECTORS[__model[0]] = __manufacturer
        PYFAI_SHAPES_OF_DETECTOR_MODELS[__model[0]] = __cls.MAX_SHAPE
        PYFAI_DETECTOR_MANUFACTURERS.add(__manufacturer)
        if __cls.MAX_SHAPE in PYFAI_DETECTOR_MODELS_OF_SHAPES:
            PYFAI_DETECTOR_MODELS_OF_SHAPES[__cls.MAX_SHAPE] = (
                PYFAI_DETECTOR_MODELS_OF_SHAPES[__cls.MAX_SHAPE]
                + [f"[{__manufacturer}] {__model[0]}"]
            )
        else:
            PYFAI_DETECTOR_MODELS_OF_SHAPES[__cls.MAX_SHAPE] = [
                f"[{__manufacturer}] {__model[0]}"
            ]

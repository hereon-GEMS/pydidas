# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "PYFAI_DETECTOR_MANUFACTURERS",
    "PYFAI_DETECTOR_MODELS_OF_SHAPES",
    "PYFAI_DETECTOR_NAMES",
    "PYFAI_MANUFACTURERS_OF_DETECTORS",
    "PYFAI_SHAPES_OF_DETECTOR_MODELS",
    "pyFAI_METHOD",
    "pyFAI_UNITS",
]


_pyfai_detector_data_initialized = False


def _initialize_pyfai_detector_data() -> None:
    """Populate the detector-name containers by lazily importing pyFAI."""
    global _pyfai_detector_data_initialized
    if _pyfai_detector_data_initialized:
        return
    # Set the flag before the import so re-entrant calls are handled gracefully.
    _pyfai_detector_data_initialized = True
    from pyFAI.detectors import Detector as _Detector

    for __class in _Detector.registry.values():
        __manufacturer = (
            "Custom" if __class.MANUFACTURER is None else __class.MANUFACTURER
        )
        if isinstance(__manufacturer, list):
            __manufacturer = " / ".join(__manufacturer)
        __model = __class.aliases
        if len(__model) > 0:
            PYFAI_DETECTOR_NAMES.update(__model)
            PYFAI_MANUFACTURERS_OF_DETECTORS[__model[0]] = __manufacturer
            PYFAI_SHAPES_OF_DETECTOR_MODELS[__model[0]] = __class.MAX_SHAPE
            PYFAI_DETECTOR_MANUFACTURERS.add(__manufacturer)
            if __class.MAX_SHAPE in PYFAI_DETECTOR_MODELS_OF_SHAPES:
                _label = f"[{__manufacturer}] {__model[0]}"
                if _label not in PYFAI_DETECTOR_MODELS_OF_SHAPES[__class.MAX_SHAPE]:
                    PYFAI_DETECTOR_MODELS_OF_SHAPES[__class.MAX_SHAPE] = (
                        PYFAI_DETECTOR_MODELS_OF_SHAPES[__class.MAX_SHAPE] + [_label]
                    )
            else:
                PYFAI_DETECTOR_MODELS_OF_SHAPES[__class.MAX_SHAPE] = [
                    f"[{__manufacturer}] {__model[0]}"
                ]


class _LazyPyfaiSet(set):
    """
    A set subclass that populates itself with pyFAI detector names on first access.

    This defers the import of pyFAI.detectors (and therefore the entire pyFAI
    package) until the set is actually queried, rather than at module import time.
    """

    def _ensure_initialized(self) -> None:
        _initialize_pyfai_detector_data()

    def __contains__(self, item: object) -> bool:
        self._ensure_initialized()
        return super().__contains__(item)

    def __iter__(self):
        self._ensure_initialized()
        return super().__iter__()

    def __len__(self) -> int:
        self._ensure_initialized()
        return super().__len__()

    def __bool__(self) -> bool:
        self._ensure_initialized()
        return super().__bool__()


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
PYFAI_DETECTOR_NAMES = _LazyPyfaiSet()
PYFAI_MANUFACTURERS_OF_DETECTORS = {}
PYFAI_SHAPES_OF_DETECTOR_MODELS = {}
PYFAI_DETECTOR_MODELS_OF_SHAPES = {}

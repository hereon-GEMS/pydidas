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
    "pyFAI_METHOD",
    "pyFAI_UNITS",
]

from pydidas.core.lazy_imports.lazy_objects import LazyDict, LazySet


def _pyfai_detector_manufacturers() -> set[str]:
    """
    Return the set of pyFAI detector manufacturers.

    Returns
    -------
    set[str]
        A set of unique detector manufacturers from pyFAI. Entries
        are all string entries of the .MANUFACTURER attribute of the
        pyFAI Detector classes. If a detector class has no manufacturer,
        it is labeled as "Custom". If a detector class has multiple
        manufacturers, they are joined with a " / " separator.
    """
    from pyFAI.detectors import Detector

    _manufacturers = set()
    for _class in Detector.registry.values():
        _manufacturer = _class.MANUFACTURER or "Custom"
        if isinstance(_manufacturer, list):
            _manufacturer = " / ".join(_manufacturer)
        _manufacturers.add(_manufacturer)
    return _manufacturers


def _pyfai_detector_names() -> set[str]:
    """
    Return the set of pyFAI detector names.

    Returns
    -------
    set[str]
        A set of unique detector names from pyFAI. Entries are all string
        entries of the .__name__ attribute of the pyFAI Detector classes,
        as well as any aliases defined in the .aliases attribute of those
        classes.
    """
    from pyFAI.detectors import Detector

    _names = set()
    for _class in Detector.registry.values():
        _aliases = _class.aliases
        if _aliases:
            _names.add(_class.__name__)
            _names.update(_aliases)
    return _names


def _pyfai_det_models_of_shapes() -> dict[tuple[int, int], list[str]]:
    """
    Return a dictionary mapping detector shapes to their corresponding models.

    Returns
    -------
    dict[tuple[int, int], list[str]]
        A dictionary where keys are tuples representing the maximum shape
        of detectors (height, width), and values are lists of strings
        representing the corresponding detector models. Each model is
        formatted as "[Manufacturer] ModelName".
    """
    from pyFAI.detectors import Detector

    _models_of_shapes = {}
    for _class in Detector.registry.values():
        if not hasattr(_class, "MAX_SHAPE"):
            continue
        _manufacturer = _class.MANUFACTURER or "Custom"
        if isinstance(_manufacturer, list):
            _manufacturer = " / ".join(_manufacturer)
        _model = _class.aliases[0] if _class.aliases else _class.__name__
        _shape = _class.MAX_SHAPE
        if _shape not in _models_of_shapes:
            _models_of_shapes[_shape] = []
        label = f"[{_manufacturer}] {_model}"
        if label not in _models_of_shapes[_shape]:
            _models_of_shapes[_shape].append(label)
    return _models_of_shapes


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


PYFAI_DETECTOR_MANUFACTURERS: set[str] = LazySet(_pyfai_detector_manufacturers)
PYFAI_DETECTOR_NAMES: set[str] = LazySet(_pyfai_detector_names)
PYFAI_DETECTOR_MODELS_OF_SHAPES: dict[tuple[int, int], list[str]] = LazyDict(
    _pyfai_det_models_of_shapes
)

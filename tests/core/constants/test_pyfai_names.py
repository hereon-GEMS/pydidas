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

"""Tests for pydidas.core.constants.pyfai_names."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import pytest

from pydidas.core.constants.pyfai_names import (
    PYFAI_DETECTOR_MANUFACTURERS,
    PYFAI_DETECTOR_MODELS_OF_SHAPES,
    PYFAI_DETECTOR_NAMES,
    _pyfai_det_models_of_shapes,
    _pyfai_detector_manufacturers,
    _pyfai_detector_names,
    pyFAI_METHOD,
    pyFAI_UNITS,
)
from pydidas.core.lazy_imports.lazy_objects import LazyDict, LazySet


# ---------------------------------------------------------------------------
# pyFAI_UNITS
# ---------------------------------------------------------------------------


def test_pyfai_units__is_dict():
    assert isinstance(pyFAI_UNITS, dict)


def test_pyfai_units__has_expected_keys():
    expected_keys = {
        "Q / nm^-1",
        "Q / A^-1",
        "2theta / deg",
        "2theta / rad",
        "r / mm",
        "chi / deg",
        "chi / rad",
    }
    assert set(pyFAI_UNITS.keys()) == expected_keys


def test_pyfai_units__values_are_strings():
    assert all(isinstance(v, str) for v in pyFAI_UNITS.values())


@pytest.mark.parametrize(
    "label, code",
    [
        ("Q / nm^-1", "q_nm^-1"),
        ("Q / A^-1", "q_A^-1"),
        ("2theta / deg", "2th_deg"),
        ("2theta / rad", "2th_rad"),
        ("r / mm", "r_mm"),
        ("chi / deg", "chi_deg"),
        ("chi / rad", "chi_rad"),
    ],
)
def test_pyfai_units__mapping(label, code):
    assert pyFAI_UNITS[label] == code


# ---------------------------------------------------------------------------
# pyFAI_METHOD
# ---------------------------------------------------------------------------


def test_pyfai_method__is_dict():
    assert isinstance(pyFAI_METHOD, dict)


def test_pyfai_method__has_expected_keys():
    expected_keys = {
        "CSR",
        "CSR OpenCL",
        "CSR full",
        "CSR full OpenCL",
        "LUT",
        "LUT OpenCL",
        "LUT full",
        "LUT full OpenCL",
    }
    assert set(pyFAI_METHOD.keys()) == expected_keys


def test_pyfai_method__values_are_3_tuples():
    for key, val in pyFAI_METHOD.items():
        assert isinstance(val, tuple) and len(val) == 3, (
            f"Value for '{key}' is not a 3-tuple"
        )


@pytest.mark.parametrize(
    "key, expected",
    [
        ("CSR", ("bbox", "csr", "cython")),
        ("CSR OpenCL", ("bbox", "csr", "opencl")),
        ("LUT", ("bbox", "lut", "cython")),
        ("LUT OpenCL", ("bbox", "lut", "opencl")),
        ("CSR full", ("full", "csr", "cython")),
        ("LUT full", ("full", "lut", "cython")),
    ],
)
def test_pyfai_method__values(key, expected):
    assert pyFAI_METHOD[key] == expected


# ---------------------------------------------------------------------------
# _pyfai_detector_manufacturers (private function)
# ---------------------------------------------------------------------------


def test_pyfai_detector_manufacturers__returns_set():
    result = _pyfai_detector_manufacturers()
    assert isinstance(result, set)


def test_pyfai_detector_manufacturers__non_empty():
    result = _pyfai_detector_manufacturers()
    assert len(result) > 0


def test_pyfai_detector_manufacturers__all_strings():
    result = _pyfai_detector_manufacturers()
    assert all(isinstance(m, str) for m in result)


def test_pyfai_detector_manufacturers__no_list_entries():
    result = _pyfai_detector_manufacturers()
    assert not any(isinstance(m, list) for m in result)


def test_pyfai_detector_manufacturers__custom_present():
    result = _pyfai_detector_manufacturers()
    assert "Custom" in result


def test_pyfai_detector_manufacturers__multimanufacturer_joined_with_slash():
    from pyFAI.detectors import Detector

    for _class in Detector.registry.values():
        if isinstance(_class.MANUFACTURER, list):
            expected = " / ".join(_class.MANUFACTURER)
            assert expected in _pyfai_detector_manufacturers()
            return
    # No multi-manufacturer class found — skip rather than fail
    pytest.skip("No multi-manufacturer pyFAI detector found in this installation")


# ---------------------------------------------------------------------------
# _pyfai_detector_names (private function)
# ---------------------------------------------------------------------------


def test_pyfai_detector_names__returns_set():
    result = _pyfai_detector_names()
    assert isinstance(result, set)


def test_pyfai_detector_names__non_empty():
    result = _pyfai_detector_names()
    assert len(result) > 0


def test_pyfai_detector_names__all_strings():
    result = _pyfai_detector_names()
    assert all(isinstance(n, str) for n in result)


def test_pyfai_detector_names__includes_detector():
    result = _pyfai_detector_names()
    assert "Pilatus 1M" in result


def test_pyfai_detector_names__classes_and_aliases_included():
    from pyFAI.detectors import Detector

    for _class in Detector.registry.values():
        if _class.aliases:
            result = _pyfai_detector_names()
            assert _class.__name__ in result
            for alias in _class.aliases:
                assert alias in result, f"Alias '{alias}' missing from names"
            return
    pytest.skip("No pyFAI detector with aliases found in this installation")


# ---------------------------------------------------------------------------
# _pyfai_det_models_of_shapes (private function)
# ---------------------------------------------------------------------------


def test_pyfai_det_models_of_shapes__returns_dict():
    result = _pyfai_det_models_of_shapes()
    assert isinstance(result, dict)


def test_pyfai_det_models_of_shapes__non_empty():
    result = _pyfai_det_models_of_shapes()
    assert len(result) > 0


def test_pyfai_det_models_of_shapes__keys_are_tuples_of_two_ints():
    result = _pyfai_det_models_of_shapes()
    for key in result:
        assert isinstance(key, tuple) and len(key) == 2, f"Key {key!r} is not a 2-tuple"
        assert all(isinstance(dim, int) for dim in key), (
            f"Key {key!r} elements are not all ints"
        )


def test_pyfai_det_models_of_shapes__values_are_lists_of_strings():
    result = _pyfai_det_models_of_shapes()
    for shape, models in result.items():
        assert isinstance(models, list), f"Shape {shape}: value is not a list"
        assert all(isinstance(m, str) for m in models), (
            f"Shape {shape}: not all model names are strings"
        )


def test_pyfai_det_models_of_shapes__model_label_format():
    result = _pyfai_det_models_of_shapes()
    for models in result.values():
        for label in models:
            assert label.startswith("["), f"Label '{label}' does not start with '['"
            assert "]" in label, f"Label '{label}' has no closing ']'"


def test_pyfai_det_models_of_shapes__no_duplicate_labels_per_shape():
    result = _pyfai_det_models_of_shapes()
    for shape, models in result.items():
        assert len(models) == len(set(models)), (
            f"Shape {shape} has duplicate labels: {models}"
        )


# ---------------------------------------------------------------------------
# PYFAI_DETECTOR_NAMES (LazySet)
# ---------------------------------------------------------------------------


def test_pyfai_detector_names_constant__is_lazy_set():
    assert isinstance(PYFAI_DETECTOR_NAMES, LazySet)


def test_pyfai_detector_names_constant__is_set():
    assert isinstance(PYFAI_DETECTOR_NAMES, set)


def test_pyfai_detector_names_constant__non_empty():
    assert len(PYFAI_DETECTOR_NAMES) > 0


def test_pyfai_detector_names_constant__contains_detector():
    assert "Pilatus 1M" in PYFAI_DETECTOR_NAMES


def test_pyfai_detector_names_constant__matches_function():
    assert {x for x in PYFAI_DETECTOR_NAMES} == _pyfai_detector_names()


# ---------------------------------------------------------------------------
# PYFAI_DETECTOR_MANUFACTURERS (LazySet)
# ---------------------------------------------------------------------------


def test_pyfai_detector_manufacturers_constant__is_lazy_set():
    assert isinstance(PYFAI_DETECTOR_MANUFACTURERS, LazySet)


def test_pyfai_detector_manufacturers_constant__is_set():
    assert isinstance(PYFAI_DETECTOR_MANUFACTURERS, set)


def test_pyfai_detector_manufacturers_constant__non_empty():
    assert len(PYFAI_DETECTOR_MANUFACTURERS) > 0


def test_pyfai_detector_manufacturers_constant__contains_custom():
    assert "Custom" in PYFAI_DETECTOR_MANUFACTURERS


def test_pyfai_detector_manufacturers_constant__matches_function():
    assert {x for x in PYFAI_DETECTOR_MANUFACTURERS} == _pyfai_detector_manufacturers()


# ---------------------------------------------------------------------------
# PYFAI_DETECTOR_MODELS_OF_SHAPES (LazyDict)
# ---------------------------------------------------------------------------


def test_pyfai_detector_models_of_shapes__is_lazy_dict():
    assert isinstance(PYFAI_DETECTOR_MODELS_OF_SHAPES, LazyDict)


def test_pyfai_detector_models_of_shapes__is_dict():
    assert isinstance(PYFAI_DETECTOR_MODELS_OF_SHAPES, dict)


def test_pyfai_detector_models_of_shapes__non_empty():
    assert len(PYFAI_DETECTOR_MODELS_OF_SHAPES) > 0


def test_pyfai_detector_models_of_shapes__keys_are_tuples():
    for key in PYFAI_DETECTOR_MODELS_OF_SHAPES:
        assert isinstance(key, tuple) and len(key) == 2


def test_pyfai_detector_models_of_shapes__values_are_lists():
    for key in PYFAI_DETECTOR_MODELS_OF_SHAPES:
        assert isinstance(PYFAI_DETECTOR_MODELS_OF_SHAPES[key], list)


def test_pyfai_detector_models_of_shapes__matches_function():
    expected = _pyfai_det_models_of_shapes()
    assert {
        k: PYFAI_DETECTOR_MODELS_OF_SHAPES[k] for k in PYFAI_DETECTOR_MODELS_OF_SHAPES
    } == expected


if __name__ == "__main__":
    pytest.main([__file__])

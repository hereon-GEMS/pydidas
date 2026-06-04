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

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import numpy as np
import pytest

from pydidas.contexts import Scan
from pydidas.core import UserConfigError
from pydidas.core.utils import get_random_string


_SCAN_SHAPE: tuple[int, ...] = (5, 7, 3, 2)
_SCAN_DELTA: tuple[float | int, ...] = (0.1, 0.5, 1, 1.5)
_SCAN_OFFSET: tuple[float | int, ...] = (3, -1, 0, 0.5)
_SCAN_DIM: int = 4


def set_scan_params(scan: Scan) -> None:
    scan.set_param_value("scan_dim", _SCAN_DIM)
    for index, val in enumerate(_SCAN_SHAPE):
        scan.set_param_value(f"scan_dim{index}_n_points", val)
    for index, val in enumerate(_SCAN_DELTA):
        scan.set_param_value(f"scan_dim{index}_delta", val)
    for index, val in enumerate(_SCAN_OFFSET):
        scan.set_param_value(f"scan_dim{index}_offset", val)


def get_scan_range(dim):
    return np.linspace(
        _SCAN_OFFSET[dim],
        (_SCAN_OFFSET[dim] + (_SCAN_SHAPE[dim] - 1) * _SCAN_DELTA[dim]),
        num=_SCAN_SHAPE[dim],
    )


def test_init():
    scan = Scan()
    assert isinstance(scan, Scan)


def test_n_total():
    scan = Scan()
    set_scan_params(scan)
    assert scan.n_points == np.prod(_SCAN_SHAPE)


def test_shape():
    scan = Scan()
    set_scan_params(scan)
    assert scan.shape == _SCAN_SHAPE


@pytest.mark.parametrize(
    "scan_dim, n_points, expected_squeezed",
    [
        (4, (5, 7, 3, 2), (5, 7, 3, 2)),  # no squeezing needed
        (4, (5, 1, 3, 1), (5, 3)),  # with single dimensions
        (4, (1, 1, 1, 1), ()),  # all dimensions one
        (3, (1, 10, 1), (10,)),  # single dimension nonzero
        (4, (5, 1, 7, 1), (5, 7)),  # alternating pattern
        (4, (1, 1, 4, 6), (4, 6)),  # ones at start
        (4, (3, 5, 1, 1), (3, 5)),  # ones at end
    ],
)
def test_squeezed_shape(scan_dim, n_points, expected_squeezed):
    """Test squeezed_shape property with various dimension configurations.

    Parameters
    ----------
    scan_dim : int
        The number of scan dimensions to set.
    n_points : tuple[int]
        The number of points for each dimension.
    expected_squeezed : tuple[int]
        The expected squeezed shape (dimensions with n_points == 1 removed).
    """
    scan = Scan()
    scan.set_param_value("scan_dim", scan_dim)
    for i, n in enumerate(n_points):
        scan.set_param_value(f"scan_dim{i}_n_points", n)
    assert scan.squeezed_shape == expected_squeezed


def test_squeezed_shape__default_scan():
    """Test squeezed_shape on a default (uninitialized) scan."""
    scan = Scan()
    # Default scan should have all dimensions as 1
    # Default scan_dim is 1, and scan_dim0_n_points should be 1
    _squeezed = scan.squeezed_shape
    assert isinstance(_squeezed, tuple)
    # The result should be empty or contain only 1s removed


def test_ndim():
    scan = Scan()
    set_scan_params(scan)
    assert scan.ndim == 4


@pytest.mark.parametrize(
    "n, m, delta, expected",
    [
        (8, 3, 1, 10),
        (10, 1, 1, 10),
        (4, 1, 3, 10),
        (8, 6, 4, 34),
        (6, 5, 3, 20),
        (6, 1, 4, 21),
        (6, 45, 15, 120),
    ],
)
@pytest.mark.parametrize("ndims", [1, 2, 3])
def test_n_frames_required(ndims, n, m, delta, expected):
    scan = Scan()
    scan.set_param_value("scan_dim", ndims)
    if ndims == 1:
        scan.set_param_value("scan_dim0_n_points", n)
    elif ndims == 2:
        scan.set_param_value("scan_dim0_n_points", n // 2)
        scan.set_param_value("scan_dim1_n_points", 2)
    elif ndims == 3:
        scan.set_param_value("scan_dim0_n_points", n // 2)
        scan.set_param_value("scan_dim1_n_points", 1)
        scan.set_param_value("scan_dim2_n_points", 2)
    scan.set_param_value("frame_indices_per_scan_point", delta)
    scan.set_param_value("scan_frames_per_point", m)
    assert scan.n_frames_required == expected


@pytest.mark.parametrize(
    "pattern", ["##test_###.tiff", "test_###0_##.tiff", "test_##_##_##.tiff"]
)
def test_file_naming_pattern_w_index__multiple_counters(pattern):
    scan = Scan()
    scan.set_param_value("scan_name_pattern", pattern)
    with pytest.raises(UserConfigError):
        _ = scan.processed_file_naming_pattern


@pytest.mark.parametrize(
    "pattern", ["test_1244.tiff", "test_0_22.npy", "test_22_ba_2.h5"]
)
def test_file_naming_pattern_w_index__no_counters(pattern):
    scan = Scan()
    scan.set_param_value("scan_name_pattern", pattern)
    assert scan.processed_file_naming_pattern == pattern


@pytest.mark.parametrize(
    "pattern",
    ["test_###.tiff", "test_######0_22.npy", "test_22_####_2.h5", "test_1a_#.h5"],
)
def test_update_filename_string(pattern):
    scan = Scan()
    scan.set_param_value("scan_name_pattern", pattern)
    _n_hash = pattern.count("#")
    _parts = pattern.split("#" * _n_hash)
    _parts.insert(1, "{index:0" + str(_n_hash) + "d}")
    assert scan.processed_file_naming_pattern == "".join(_parts)


def test_get_range_for_dim__wrong_dim():
    scan = Scan()
    set_scan_params(scan)
    with pytest.raises(UserConfigError):
        scan.get_range_for_dim(5)


def test_get_range_for_dim__empty_dim():
    scan = Scan()
    _range = scan.get_range_for_dim(1)
    assert isinstance(_range, np.ndarray)


def test_get_range_for_dim__normal():
    _index = 1
    scan = Scan()
    set_scan_params(scan)
    _range = scan.get_range_for_dim(_index)
    _target = get_scan_range(_index)
    assert np.allclose(_range, _target)


def test_get_metadata_for_dim():
    scan = Scan()
    set_scan_params(scan)
    for _index in range(4):
        _unit = get_random_string(5)
        _label = get_random_string(20)
        scan.set_param_value(f"scan_dim{_index}_unit", _unit)
        scan.set_param_value(f"scan_dim{_index}_label", _label)
        _scan_label, _scan_unit, _range = scan.get_metadata_for_dim(_index)
        assert _scan_label == _label
        assert _unit == _scan_unit
        assert np.allclose(get_scan_range(_index), _range)


@pytest.mark.parametrize("n_frames", [1, 2, 3, 4])
def test_get_indices_from_ordinal(n_frames):
    scan = Scan()
    set_scan_params(scan)
    scan.set_param_value("scan_frames_per_point", n_frames)
    _pos = tuple(i - 2 for i in _SCAN_SHAPE)
    _shape = _SCAN_SHAPE + (1,)
    _n = np.sum([_pos[i] * np.prod(_shape[i + 1 :]) for i in range(_SCAN_DIM)])
    _index = scan.get_indices_from_ordinal(_n)
    assert _index == _pos


def test_get_ordinal_from_indices__zero():
    scan = Scan()
    set_scan_params(scan)
    _index = scan.get_ordinal_from_indices((0, 0, 0, 0))
    assert _index == 0


def test_get_ordinal_from_indices__zero_as_ndarray():
    scan = Scan()
    set_scan_params(scan)
    _index = scan.get_ordinal_from_indices(np.array((0, 0, 0, 0)))
    assert _index == 0


def test_get_ordinal_from_indices__negative():
    scan = Scan()
    set_scan_params(scan)
    with pytest.raises(UserConfigError):
        scan.get_ordinal_from_indices((0, -1, 0, 0))


def test_get_ordinal_from_indices__in_scan():
    _indices = (2, 1, 2, 1)
    _frame = (
        _indices[3]
        + _SCAN_SHAPE[3] * _indices[2]
        + np.prod(_SCAN_SHAPE[2:]) * _indices[1]
        + np.prod(_SCAN_SHAPE[1:]) * _indices[0]
    )
    scan = Scan()
    set_scan_params(scan)
    _index = scan.get_ordinal_from_indices(_indices)
    assert _index == _frame


def test_axis_labels():
    scan = Scan()
    set_scan_params(scan)
    _labels = [get_random_string(5) for _ in range(_SCAN_DIM)]
    for _index in range(_SCAN_DIM):
        scan.set_param_value(f"scan_dim{_index}_label", _labels[_index])
    assert _labels == scan.axis_labels


def test_axis_units():
    scan = Scan()
    set_scan_params(scan)
    _units = [get_random_string(5) for _ in range(_SCAN_DIM)]
    for _index in range(_SCAN_DIM):
        scan.set_param_value(f"scan_dim{_index}_unit", _units[_index])
    assert _units == scan.axis_units


def test_axis_ranges():
    scan = Scan()
    set_scan_params(scan)
    _ranges = scan.axis_ranges
    for _index in range(_SCAN_DIM):
        _ref = get_scan_range(_index)
        assert np.allclose(_ref, _ranges[_index])


def test_update_from_scan():
    scan = Scan()
    set_scan_params(scan)
    _new_scan = Scan()
    _new_scan.update_from_scan(scan)
    for _key, _val in scan.get_param_values_as_dict().items():
        assert _val == _new_scan.get_param_value(_key)


def test_update_from_dictionary__missing_dim():
    _scan = {"scan_title": get_random_string(8), "scan_dim": 2}
    scan = Scan()
    with pytest.raises(KeyError):
        scan.update_from_dictionary(_scan)


def test_update_from_dictionary__empty_input():
    _title = get_random_string(8)
    scan = Scan()
    scan.set_param_value("scan_title", _title)
    scan.update_from_dictionary({})
    assert scan.get_param_value("scan_title") == _title


def test_update_from_dictionary__all_entries_present():
    _scan = {
        "scan_title": get_random_string(8),
        "scan_dim": 2,
        "scan_base_directory": "/dummy",
        "scan_name_pattern": "test_###",
        "pattern_number_offset": 1,
        "frame_indices_per_scan_point": 1,
        "scan_frames_per_point": 1,
        "scan_multi_frame_handling": "Sum",
        0: {
            "label": get_random_string(5),
            "unit": get_random_string(3),
            "delta": 1,
            "offset": -5,
            "n_points": 42,
        },
        1: {
            "label": get_random_string(5),
            "unit": get_random_string(3),
            "delta": 3,
            "offset": 12,
            "n_points": 8,
        },
    }
    scan = Scan()
    scan.update_from_dictionary(_scan)
    assert scan.get_param_value("scan_title") == _scan["scan_title"]
    assert scan.get_param_value("scan_dim") == _scan["scan_dim"]
    for _dim in [0, 1]:
        _dim_info: dict[str, str | int] = _scan[_dim]  # type: ignore[typeddict-unknown-key]
        for _entry in ["label", "unit", "offset", "delta", "n_points"]:
            assert _dim_info[_entry] == scan.get_param_value(f"scan_dim{_dim}_{_entry}")


def test_set_param_value__deprecated():
    scan = Scan()
    with pytest.warns(DeprecationWarning):
        scan.set_param_value("scan_start_index", 42)
    assert scan.get_param_value("pattern_number_offset") == 42


@pytest.mark.parametrize("indices", [1, 2, 4, 12])
@pytest.mark.parametrize("frames", [1, 3, 5])
@pytest.mark.parametrize("ordinal", [0, 1, 2, 42])
def test_get_frame_indices_from_ordinal(indices, frames, ordinal):
    scan = Scan()
    set_scan_params(scan)
    scan.set_param_value("scan_frames_per_point", frames)
    scan.set_param_value("frame_indices_per_scan_point", indices)
    _indices = scan.get_frame_indices_from_ordinal(ordinal)
    assert _indices == [ordinal * indices + _i for _i in range(frames)]


if __name__ == "__main__":
    pytest.main()

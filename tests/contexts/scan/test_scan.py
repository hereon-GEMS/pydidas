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

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from typing import Any

import numpy as np
import pytest

from pydidas.contexts import Scan
from pydidas.core import UserConfigError
from pydidas.core.utils import get_random_string


_scan_param_values = {
    "shape": (5, 7, 3, 2),
    "delta": (0.1, 0.5, 1, 1.5),
    "offset": (3, -1, 0, 0.5),
    "scan_dim": 4,
}


def set_scan_params(scan: Scan) -> dict[str, Any]:
    scan.set_param_value("scan_dim", _scan_param_values["scan_dim"])
    for index, val in enumerate(_scan_param_values["shape"]):
        scan.set_param_value(f"scan_dim{index}_n_points", val)
    for index, val in enumerate(_scan_param_values["delta"]):
        scan.set_param_value(f"scan_dim{index}_delta", val)
    for index, val in enumerate(_scan_param_values["offset"]):
        scan.set_param_value(f"scan_dim{index}_offset", val)


def get_scan_range(dim):
    return np.linspace(
        _scan_param_values["offset"][dim],
        (
            _scan_param_values["offset"][dim]
            + (_scan_param_values["shape"][dim] - 1) * _scan_param_values["delta"][dim]
        ),
        num=_scan_param_values["shape"][dim],
    )


def test_init():
    scan = Scan()
    assert isinstance(scan, Scan)


def test_n_total():
    scan = Scan()
    set_scan_params(scan)
    assert scan.n_points == np.prod(_scan_param_values["shape"])


def test_shape():
    scan = Scan()
    set_scan_params(scan)
    assert scan.shape == _scan_param_values["shape"]


def test_ndim():
    scan = Scan()
    set_scan_params(scan)
    assert scan.ndim == 4


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
        _scanlabel, _scanunit, _range = scan.get_metadata_for_dim(_index)
        assert _scanlabel == _label
        assert _unit == _scanunit
        assert np.allclose(get_scan_range(_index), _range)


@pytest.mark.parametrize("n_frames", [1, 2, 3, 4])
def test_get_index_position_in_scan(n_frames):
    scan = Scan()
    set_scan_params(scan)
    scan.set_param_value("scan_frames_per_scan_point", n_frames)
    _pos = tuple(i - 2 for i in _scan_param_values["shape"])
    _shape = _scan_param_values["shape"] + (1,)
    _n = np.sum(
        [
            _pos[i] * np.prod(_shape[i + 1 :])
            for i in range(_scan_param_values["scan_dim"])
        ]
    )
    _index = scan.get_index_position_in_scan(_n)
    assert _index == _pos


@pytest.mark.parametrize("n_frames", [1, 2, 3, 4])
def test_get_index_of_frame(n_frames):
    scan = Scan()
    set_scan_params(scan)
    _n = 60
    scan.set_param_value("scan_frames_per_scan_point", n_frames)
    _index = scan.get_index_of_frame(_n)
    assert _index == _n / n_frames


def test_get_frame_from_indices__zero():
    scan = Scan()
    set_scan_params(scan)
    _index = scan.get_frame_from_indices((0, 0, 0, 0))
    assert _index == 0


def test_get_frame_from_indices__zero_as_ndarray():
    scan = Scan()
    set_scan_params(scan)
    _index = scan.get_frame_from_indices(np.array((0, 0, 0, 0)))
    assert _index == 0


def test_get_frame_from_indices__negative():
    scan = Scan()
    set_scan_params(scan)
    with pytest.raises(UserConfigError):
        scan.get_frame_from_indices((0, -1, 0, 0))


def test_get_frame_from_indices__inscan():
    _indices = (2, 1, 2, 1)
    _frame = (
        _indices[3]
        + _scan_param_values["shape"][3] * _indices[2]
        + np.prod(_scan_param_values["shape"][2:]) * _indices[1]
        + np.prod(_scan_param_values["shape"][1:]) * _indices[0]
    )
    scan = Scan()
    set_scan_params(scan)
    _index = scan.get_frame_from_indices(_indices)
    assert _index == _frame


def test_get_frame_from_indices__multiplicity_gt_one():
    _indices = (2, 1, 2, 1)
    _frame = (
        _indices[3]
        + _scan_param_values["shape"][3] * _indices[2]
        + np.prod(_scan_param_values["shape"][2:]) * _indices[1]
        + np.prod(_scan_param_values["shape"][1:]) * _indices[0]
    ) * 3
    scan = Scan()
    set_scan_params(scan)
    scan.set_param_value("scan_frames_per_scan_point", 3)
    _index = scan.get_frame_from_indices(_indices)
    assert _index == _frame


def test_axis_labels():
    scan = Scan()
    set_scan_params(scan)
    _labels = [get_random_string(5) for _ in range(_scan_param_values["scan_dim"])]
    for _index in range(_scan_param_values["scan_dim"]):
        scan.set_param_value(f"scan_dim{_index}_label", _labels[_index])
    assert _labels == scan.axis_labels


def test_axis_units():
    scan = Scan()
    set_scan_params(scan)
    _units = [get_random_string(5) for _ in range(_scan_param_values["scan_dim"])]
    for _index in range(_scan_param_values["scan_dim"]):
        scan.set_param_value(f"scan_dim{_index}_unit", _units[_index])
    assert _units == scan.axis_units


def test_axis_ranges():
    scan = Scan()
    set_scan_params(scan)
    _ranges = scan.axis_ranges
    for _index in range(_scan_param_values["scan_dim"]):
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
        "file_number_offset": 1,
        "frame_indices_per_scan_point": 1,
        "scan_frames_per_scan_point": 1,
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
        for _entry in ["label", "unit", "offset", "delta", "n_points"]:
            assert _scan[_dim][_entry] == scan.get_param_value(
                f"scan_dim{_dim}_{_entry}"
            )


def test_set_param_value__deprecated():
    scan = Scan()
    with pytest.warns(DeprecationWarning):
        scan.set_param_value("scan_start_index", 42)
    assert scan.get_param_value("file_number_offset") == 42


if __name__ == "__main__":
    pytest.main()

# This file is part of pydidas.
#
# Copyright 2025 - 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2025 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import warnings

import numpy as np
import pytest

from pydidas.core import Dataset


_np_random_generator = np.random.default_rng()

_AXIS_SLICES = [0, 3, -1, -3, (0,), (2,), (0, 1), (1, 3), (2, 0), (1, 2, 3), (0, 2, 3)]
_IMPLEMENTED_METHODS = ["mean", "sum", "max", "min"]
_METHOD_TAKES_INT_ONLY = ["cumsum"]
_METHOD_REQUIRES_INITIAL = ["max", "min"]
_METHOD_TAKES_NO_DTYPE = ["max", "min"]

_AX_UNITS = ["m", "rad", "um", "nm^-1", "deg"]
_AX_RANGES = [
    10 - np.arange(10),
    0.1 + 0.2 * np.arange(10) ** 2,
    3 * np.arange(10),
    42 + 2 * np.arange(10),
    1 - 2.4 * np.arange(10),
]


@pytest.fixture
def test_dataset(request):
    ndim = int(request.param)
    return Dataset(
        np.random.random([10] * ndim),
        axis_labels=[f"axis{n}" for n in range(ndim)],
        axis_ranges=_AX_RANGES[:ndim],
        axis_units=_AX_UNITS[:ndim],
    )


@pytest.fixture
def random_dataset(request):
    ndim = int(request.param)
    shape = np.arange(ndim) + 6
    return Dataset(
        _np_random_generator.random(shape),
        axis_labels=[str(i) for i in range(ndim)],
        axis_units=[chr(97 + i) for i in range(ndim)],
        axis_ranges=[
            _np_random_generator.integers(-10, 10)
            + (0.1 + _np_random_generator.random()) * np.arange(shape[_dim])
            for _dim in range(ndim)
        ],
    )


@pytest.mark.parametrize("test_dataset", [2, 3, 4], indirect=True)
def test_roll__no_axis(test_dataset):
    with warnings.catch_warnings():
        warnings.simplefilter("error", UserWarning)
        _new = np.roll(test_dataset, 3)
    assert _new.shape == test_dataset.shape
    np.testing.assert_array_equal(_new.array, np.roll(test_dataset.array, 3))


@pytest.mark.parametrize("test_dataset", [1], indirect=True)
@pytest.mark.parametrize("shift", [-1, 0, 1, 3])
def test_roll__1d_no_axis(test_dataset, shift):
    _new = test_dataset.roll(shift)
    assert _new.shape == test_dataset.shape
    assert _new.axis_labels == test_dataset.axis_labels
    assert np.allclose(_new.axis_ranges[0], np.roll(test_dataset.axis_ranges[0], shift))
    assert _new.axis_units == test_dataset.axis_units


@pytest.mark.parametrize("test_dataset", [3, 4, 5], indirect=True)
@pytest.mark.parametrize("shift", [-1, 0, 1, 3])
@pytest.mark.parametrize("axis", [0, 1, 2])
def test_roll__w_axis(test_dataset, shift, axis):
    _new = test_dataset.roll(shift, axis=axis)
    assert _new.shape == test_dataset.shape
    assert _new.axis_labels == test_dataset.axis_labels
    assert np.allclose(
        _new.axis_ranges[axis], np.roll(test_dataset.axis_ranges[axis], shift)
    )
    assert _new.axis_units == test_dataset.axis_units


@pytest.mark.parametrize("test_dataset", [1, 2, 3], indirect=True)
@pytest.mark.parametrize("order", ["C", "F", "A", "K"])
@pytest.mark.parametrize("layout", ["C", "F", "transposed", "strided", "reversed"])
def test_ravel__values_metadata_and_memory_sharing(
    test_dataset: Dataset, order: str, layout: str
) -> None:
    ### This test was written by an AI tool
    if layout == "F":
        _source = Dataset(
            np.asfortranarray(test_dataset.array), **test_dataset.property_dict
        )
    elif layout == "transposed":
        _source = test_dataset.T
    elif layout == "strided":
        _source = test_dataset[::2]
    elif layout == "reversed":
        _source = test_dataset[::-1]
    else:
        _source = test_dataset
    _source.data_label = "Intensity"
    _source.data_unit = "counts"
    _source.metadata = {"measurement": 42}
    _shape = _source.shape
    _labels = _source.axis_labels
    _units = _source.axis_units
    _ranges = {_axis: _range.copy() for _axis, _range in _source.axis_ranges.items()}
    _array = _source.array
    _expected = _array.ravel(order=order)

    with warnings.catch_warnings():
        warnings.simplefilter("error", UserWarning)
        _result = _source.ravel(order=order)
        _converted = _result.astype(np.float32)
        assert isinstance(_result, Dataset)
        assert _result.shape == (_source.size,)
        np.testing.assert_array_equal(_result.array, _expected)
        np.testing.assert_array_equal(_converted.array, _expected.astype(np.float32))
        assert np.shares_memory(_source, _result) == np.shares_memory(_array, _expected)
        if _source.ndim == 1:
            assert _result.axis_labels == _labels
            assert _result.axis_units == _units
            np.testing.assert_array_equal(_result.axis_ranges[0], _ranges[0])
        else:
            assert _result.axis_labels == {0: "Flattened"}
            assert _result.axis_units == {0: ""}
            np.testing.assert_array_equal(
                _result.axis_ranges[0], np.arange(_result.size)
            )
        assert _result.data_label == "Intensity"
        assert _result.data_unit == "counts"
        assert _result.metadata == {"measurement": 42}
        assert _source.shape == _shape
        assert _source.axis_labels == _labels
        assert _source.axis_units == _units
        for _axis, _range in _ranges.items():
            np.testing.assert_array_equal(_source.axis_ranges[_axis], _range)


@pytest.mark.parametrize("test_dataset", [1, 2, 3], indirect=True)
def test_ravel__default_order(test_dataset: Dataset) -> None:
    _result = test_dataset.ravel()
    np.testing.assert_array_equal(_result.array, test_dataset.array.ravel(order="C"))


if __name__ == "__main__":
    pytest.main([__file__])

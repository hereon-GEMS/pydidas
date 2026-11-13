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
#
# This file was created using an AI tool and was modified by
# the pydidas team.

"""Shared fixtures for Dataset tests."""

import copy
from collections.abc import Callable
from typing import Any

import numpy as np
import pytest

from pydidas.core import Dataset
from pydidas.core.utils.dataset_utils import get_corresponding_dims


_np_random_generator = np.random.default_rng()

_LARGE_DSET = {
    "shape": (10, 12, 14, 16),
    "labels": ["a", "b", "c", "d"],
    "ranges": [np.arange(10), np.arange(12), np.arange(14), np.arange(16)],
    "units": ["ua", "ub", "uc", "ud"],
    "data_label": "data label",
    "data_unit": "data unit",
}


@pytest.fixture
def large_dataset() -> Dataset:
    ### This fixture was written by an AI tool.
    return Dataset(
        np.random.random(_LARGE_DSET["shape"]),
        axis_labels=_LARGE_DSET["labels"],
        axis_ranges=_LARGE_DSET["ranges"],
        axis_units=_LARGE_DSET["units"],
        data_label=_LARGE_DSET["data_label"],
        data_unit=_LARGE_DSET["data_unit"],
        metadata={},
    )


def _get_random_dataset(ndim: int, shape: tuple[int, ...] | None = None) -> Dataset:
    """Create a Dataset with random data and random axis ranges."""
    ### This function was written by an AI tool.
    if shape is None:
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


def _ax_tuple(obj: Dataset, axes: int | tuple[int, ...]) -> tuple[int, ...]:
    """Get the positive axis indices for the given axes."""
    return tuple(
        np.mod(_x, obj.ndim) for _x in (axes if isinstance(axes, tuple) else (axes,))
    )


def _assert_new_metadata_correct(
    new_array: Dataset, slicing_axes: tuple[int, ...] | list, function_name: str
):
    """Assert that the metadata of a reduced large dataset is correct."""
    ### This function was written by an AI tool.
    assert new_array.data_label == (
        f"{function_name.capitalize()} of " + _LARGE_DSET["data_label"]
    )
    assert new_array.data_unit == _LARGE_DSET["data_unit"]
    for _key in ["axis_labels", "axis_units"]:
        _ref = [
            _item
            for _i, _item in enumerate(_LARGE_DSET[_key[5:]])
            if _i not in slicing_axes
        ]
        assert _ref == list(getattr(new_array, _key).values())
    _ref_ranges = [
        _range
        for _i, _range in enumerate(_LARGE_DSET["ranges"])
        if _i not in slicing_axes
    ]
    for _ref, _new in zip(_ref_ranges, list(new_array.axis_ranges.values())):
        assert np.allclose(_ref, _new)


def _assert_reshape_metadata_correct(obj: Dataset):
    """Assert that the metadata of a reshaped large dataset is correct."""
    ### This function was written by an AI tool.
    _dim_matches = get_corresponding_dims(_LARGE_DSET["shape"], obj.shape)
    for _index, _len in enumerate(obj.shape):
        if _index in _dim_matches:
            _original_index = _dim_matches[_index]
            assert obj.axis_labels[_index] == _LARGE_DSET["labels"][_original_index]
            assert obj.axis_units[_index] == _LARGE_DSET["units"][_original_index]
            assert np.allclose(
                obj.axis_ranges[_index], _LARGE_DSET["ranges"][_original_index]
            )
        else:
            assert obj.axis_labels[_index] == ""
            assert obj.axis_units[_index] == ""
            assert np.allclose(obj.axis_ranges[_index], np.arange(_len))


@pytest.fixture
def large_dataset_reference() -> dict[str, Any]:
    ### This fixture was written by an AI tool.
    return copy.deepcopy(_LARGE_DSET)


@pytest.fixture
def get_large_dset_prop(large_dataset_reference: dict[str, Any]) -> Callable:
    ### This fixture was written by an AI tool.
    def get_property(key: str, indices: tuple[int, ...]) -> list[Any]:
        key = key.removeprefix("axis_")
        return [
            item for i, item in enumerate(large_dataset_reference[key]) if i in indices
        ]

    return get_property


@pytest.fixture
def get_random_dataset() -> Callable:
    ### This fixture was written by an AI tool.
    return _get_random_dataset


@pytest.fixture
def ax_tuple() -> Callable:
    ### This fixture was written by an AI tool.
    return _ax_tuple


@pytest.fixture
def assert_new_metadata_correct() -> Callable:
    ### This fixture was written by an AI tool.
    return _assert_new_metadata_correct


@pytest.fixture
def assert_reshape_metadata_correct() -> Callable:
    ### This fixture was written by an AI tool.
    return _assert_reshape_metadata_correct

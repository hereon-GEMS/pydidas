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

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import h5py
import numpy as np
import pytest

from pydidas.core.exceptions import UserConfigError
from pydidas.core.utils.hdf5.nxs_dataset_utils import check_nxdata_adherence


def _write_nxdata_file(
    _fname,
    *,
    nx_class: str = "NXdata",
    signal: str = "data",
    axes=None,
    data_shape=(),
) -> None:
    """Create a minimal HDF5 file structure used by the adherence tests."""
    if axes is None:
        axes = [f"ax_{i}" for i in range(len(data_shape))]
    _data = 1 if data_shape == () else np.ones(data_shape)
    with h5py.File(_fname, "w") as h5f:
        group = h5f.create_group("entry/data")
        group.attrs["NX_class"] = nx_class
        group.attrs["signal"] = signal
        group.attrs["axes"] = axes
        group.create_dataset("data", data=_data, shape=data_shape)
        for _ax, _n in zip(axes, data_shape):
            h5f.create_dataset(f"entry/data/{_ax}", data=np.ones(_n), shape=(_n,))


def test_check_nxdata_adherence__w_valid_scalar_dataset(empty_temp_path) -> None:
    _fname = empty_temp_path / "valid_scalar.nxs"
    _write_nxdata_file(_fname)
    check_nxdata_adherence(_fname, "entry/data/data")


@pytest.mark.parametrize("shape", [(42,), (2, 3), (3, 5, 3)])
def test_check_nxdata_adherence__w_valid_ndim_dataset(empty_temp_path, shape) -> None:
    _fname = empty_temp_path / "valid_ndim.nxs"
    _write_nxdata_file(
        _fname, axes=[f"ax_{_i}" for _i, _ in enumerate(shape)], data_shape=shape
    )
    check_nxdata_adherence(_fname, "entry/data/data")


def test_check_nxdata_adherence__w_missing_file(empty_temp_path) -> None:
    _fname = empty_temp_path / "missing.nxs"
    with pytest.raises(UserConfigError, match="does not exist"):
        check_nxdata_adherence(_fname, "entry/data/data")


def test_check_nxdata_adherence__w_directory(empty_temp_path) -> None:
    _dir = empty_temp_path / "dir_test"
    _dir.mkdir(parents=True, exist_ok=True)
    with pytest.raises(UserConfigError, match="does not exist"):
        check_nxdata_adherence(_dir, "entry/data/data")


def test_check_nxdata_adherence__w_npy(empty_temp_path) -> None:
    _fname = empty_temp_path / "test.npy"
    np.save(_fname, np.array([1, 2, 3]))
    with pytest.raises(UserConfigError, match="Unable to read the selected file"):
        check_nxdata_adherence(_fname, "entry/data/data")


def test_check_nxdata_adherence__w_missing_dataset(empty_temp_path) -> None:
    _fname = empty_temp_path / "missing_dataset.nxs"
    _write_nxdata_file(_fname)
    with pytest.raises(UserConfigError, match="Unable to read the selected file"):
        check_nxdata_adherence(_fname, "entry/data/not_present")


def test_check_nxdata_adherence__w_wrong_nx_class(empty_temp_path) -> None:
    _fname = empty_temp_path / "wrong_nx_class.nxs"
    _write_nxdata_file(_fname, nx_class="NXentry")
    with pytest.raises(UserConfigError, match="does not adhere to the NXdata standard"):
        check_nxdata_adherence(_fname, "entry/data/data")


def test_check_nxdata_adherence__w_wrong_signal_key(empty_temp_path) -> None:
    _fname = empty_temp_path / "wrong_signal.nxs"
    _write_nxdata_file(_fname, signal="other")
    with pytest.raises(UserConfigError, match="does not adhere to the NXdata standard"):
        check_nxdata_adherence(_fname, "entry/data/data")


def test_check_nxdata_adherence__w_axes_length_mismatch(empty_temp_path) -> None:
    _fname = empty_temp_path / "axes_len_mismatch.nxs"
    _write_nxdata_file(_fname, axes=["axis_0"], data_shape=(2, 3))
    with pytest.raises(UserConfigError, match="does not adhere to the NXdata standard"):
        check_nxdata_adherence(_fname, "entry/data/data")


def test_check_nxdata_adherence__w_illegal_axis(empty_temp_path) -> None:
    _fname = empty_temp_path / "axes_len_mismatch.nxs"
    _write_nxdata_file(_fname, data_shape=(2, 3))
    with h5py.File(_fname, "r+") as _f:
        del _f["entry/data/ax_0"]
        _f["entry/data/ax_0"] = np.arange(42)
    with pytest.raises(UserConfigError, match="does not adhere to the NXdata standard"):
        check_nxdata_adherence(_fname, "entry/data/data")


if __name__ == "__main__":
    pytest.main([__file__])

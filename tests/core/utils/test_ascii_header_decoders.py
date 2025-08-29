# This file is part of pydidas.
#
# Copyright 2025, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import numpy as np
import pytest

from pydidas.core import Dataset, FileReadError
from pydidas.core.utils.ascii_header_decoders import (
    decode_chi_header,
    decode_specfile_header,
    decode_txt_header,
)


_x_data = np.linspace(-10, 11, 62)
_y_data = np.sin(_x_data) + 0.1 * np.random.random(_x_data.size)

_test_data = Dataset(
    _y_data,
    axis_ranges=[_x_data],
    axis_labels=["2theta"],
    axis_units=["deg"],
    data_label="test data",
    data_unit="counts",
)


@pytest.mark.parametrize(
    "written_ax_label, ax_label, ax_unit",
    [
        ["2theta", "2theta", ""],
        ["2theta (deg)", "2theta", "deg"],
        ["2theta_deg", "2theta", "deg"],
        ["2theta [deg]", "2theta [deg]", ""],
        ["2theta_2_deg", "2theta_2", "deg"],
        ["2theta (test) (deg)", "2theta (test)", "deg"],
    ],
)
def test_decode_chi_header__w_correct_ax_label(
    temp_path, written_ax_label, ax_label, ax_unit
):
    with open(temp_path / "test.chi", "w") as f:
        f.write("test.h5\n")
        f.write(f"{written_ax_label}\n")
        f.write("y data / counts\n")
        f.write("\t62\n")
        for x, y in zip(_x_data, _y_data):
            f.write(f"{x:.6e}\t{y:.6e}\n")
    _data_l, _data_u, _ax_l, _ax_u = decode_chi_header(temp_path / "test.chi")
    assert _ax_l == ax_label
    assert _ax_u == ax_unit
    assert _data_l == "y data"
    assert _data_u == "counts"


def test_decode_chi_header__incorrect_header(temp_path):
    with open(temp_path / "test.chi", "w") as f:
        f.write("test.h5\n")
        for x, y in zip(_x_data, _y_data):
            f.write(f"{x:.6e}\t{y:.6e}\n")
    with pytest.raises(FileReadError):
        _data = decode_chi_header(temp_path / "test.chi")


def test_decode_chi_header__no_file(temp_path):
    with pytest.raises(FileReadError):
        _data = decode_chi_header(temp_path / "test_42.chi")


@pytest.mark.parametrize(
    "written_label, label, unit",
    [
        ("", "", ""),
        ("2theta", "2theta", ""),
        ("2theta (deg)", "2theta", "deg"),
        ("2theta / deg", "2theta", "deg"),
        ("2theta [deg]", "2theta", "deg"),
        ("2theta random val / deg", "2theta random val", "deg"),
        ("chi angle /", "chi angle", ""),
    ],
)
def test_decode_specfile_header__specfile_1col(temp_path, written_label, label, unit):
    _header = f"F test.dat\nS 1 test.h5\nN 1\nL {written_label}\n"
    np.savetxt(
        temp_path / "test.dat", _x_data, header=_header, fmt="%.6e", comments="#"
    )
    _labels, _units = decode_specfile_header(temp_path / "test.dat")
    assert _labels == ["", label]
    assert _units == ["", unit]


@pytest.mark.parametrize(
    "written_label, xlabel, xunit, ylabel, yunit",
    [
        ("", "", "", "", ""),
        ("2theta y data", "", "", "2theta y data", ""),
        ("2theta intensity", "2theta", "", "intensity", ""),
        ("2theta (deg) y data (counts)", "2theta", "deg", "y data", "counts"),
        ("2theta / deg y data_counts", "2theta", "deg", "y data_counts", ""),
        ("2theta y data_counts / ct", "", "", "2theta y data_counts", "ct"),
        ("2theta [deg] y data [counts]", "2theta", "deg", "y data", "counts"),
        ("2theta / deg y data  / counts", "2theta", "deg", "y data", "counts"),
        ("chi angle / deg y data  / ct", "chi angle", "deg", "y data", "ct"),
        ("chi angle / deg y data  /", "chi angle", "deg", "y data", ""),
    ],
)
def test_decode_specfile_header__specfile_2col(
    temp_path, written_label, xlabel, xunit, ylabel, yunit
):
    _header = f"F test.dat\nS 1 test.h5\nN 2\nL {written_label}\n"
    np.savetxt(
        temp_path / "test.dat",
        np.column_stack((_x_data, _y_data)),
        header=_header,
        fmt="%.6e",
        comments="#",
    )
    _labels, _units = decode_specfile_header(temp_path / "test.dat")
    assert _labels == [xlabel, ylabel]
    assert _units == [xunit, yunit]


@pytest.mark.parametrize(
    "written_label",
    [
        "",
        "2theta y_data",
        "2theta / deg y_data / cts",
    ],
)
def test_decode_specfile_header__specfile_2col_no_x_col(temp_path, written_label):
    _header = f"F test.dat\nS 1 test.h5\nN 2\nL {written_label}\n"
    np.savetxt(
        temp_path / "test.dat",
        np.column_stack((_x_data, _y_data)),
        header=_header,
        fmt="%.6e",
        comments="#",
    )
    _labels, _units = decode_specfile_header(
        temp_path / "test.dat", read_x_column=False
    )
    assert _units == ["", "", ""]
    if written_label == "":
        assert _labels == ["", "", ""]
    elif written_label == "2theta y_data":
        assert _labels == ["", "0: 2theta; 1: y_data", "2theta; y_data"]
    elif written_label == "2theta / deg y_data / cts":
        assert _labels == ["", "0: 2theta; 1: y_data", "2theta / deg; y_data / cts"]


@pytest.mark.parametrize("ncols", [1, 2, 3, 4, 5])
@pytest.mark.parametrize("x_col", [True, False])
def test_decode_specfile_header__specfile_no_header(temp_path, ncols, x_col):
    if ncols == 1 and x_col:
        pytest.skip("not a valid case")
    np.savetxt(
        temp_path / "test.dat",
        np.column_stack((_x_data,) + (ncols - 1) * (_y_data,)),
        fmt="%.6e",
    )
    _labels, _units = decode_specfile_header(temp_path / "test.dat", x_col)
    if ncols == 1 or (ncols == 2 and x_col):
        assert _labels == ["", ""]
        assert _units == ["", ""]
    else:
        assert _labels == ["", "", ""]
        assert _units == ["", "", ""]


def test_decode_specfile_header__specfile_no_ncols_in_header(temp_path):
    np.savetxt(
        temp_path / "test.dat",
        np.column_stack((_x_data, _y_data)),
        fmt="%.6e",
        header="F test.dat\nS 1 test.h5\n",
        comments="#",
    )
    _labels, _units = decode_specfile_header(temp_path / "test.dat")
    assert _labels == ["", ""]
    assert _units == ["", ""]


@pytest.mark.parametrize(
    "labels", ["x / unit_a y / u_b z / u_c t / ms", "x y z t", "x y", ""]
)
def test_decode_specfile_header__specfile_4col(temp_path, labels):
    _header = f"F test.dat\nS 1 test.h5\nN 4\nL {labels}\n"
    _temp_data = np.column_stack((_x_data, _y_data, _y_data, _y_data))
    np.savetxt(
        temp_path / "test.dat", _temp_data, header=_header, fmt="%.6e", comments="#"
    )
    _labels, _units = decode_specfile_header(temp_path / "test.dat")
    if "unit_" in labels:
        assert _labels == ["x", "0: y; 1: z; 2: t", "y / u_b; z / u_c; t / ms"]
    elif labels == "":
        assert _labels == ["", "", ""]
    elif labels == "x y z t":
        assert _labels == ["x", "0: y; 1: z; 2: t", "y; z; t"]
    elif labels == "x y":
        assert _labels == [
            "x",
            "0: y; 1: no label; 2: no label",
            "y; no label; no label",
        ]
    assert _units == ["unit_a", "", ""] if "unit" in labels else ["", "", ""]


def test_decode_specfile_header__no_file(temp_path):
    with pytest.raises(FileReadError):
        _data = decode_specfile_header(temp_path / "test_42.dat")


def test_decode_txt_header__no_file(temp_path):
    with pytest.raises(FileReadError):
        _ = decode_specfile_header(temp_path / "test_42.txt")


@pytest.mark.parametrize("ax_label", ["chi", None])
@pytest.mark.parametrize("ax_unit", ["deg", None])
@pytest.mark.parametrize("data_label", ["Intensity", None])
@pytest.mark.parametrize("data_unit", ["cts", None])
def test_decode_txt_header(temp_path, ax_label, ax_unit, data_label, data_unit):
    if (temp_path / "test.txt").exists():
        (temp_path / "test.txt").unlink()
    with open(temp_path / "test.txt", "w") as f:
        f.write("# Metadata:\n")
        if ax_label is not None:
            f.write(f"# Axis label: {ax_label}\n")
        if ax_unit is not None:
            f.write(f"# Axis unit: {ax_unit}\n")
        if data_label is not None:
            f.write(f"# Data label: {data_label}\n")
        if data_unit is not None:
            f.write(f"# Data unit: {data_unit}\n")
        f.write("# --- end of metadata ---\n")
        f.write("# axis\tvalue\n")
        for x, y in zip(_x_data, _y_data):
            f.write(f"{x:.6e}\t{y:.6e}\n")
    _metadata = decode_txt_header(temp_path / "test.txt")
    assert _metadata.get("ax_label") == ax_label
    assert _metadata.get("ax_unit") == ax_unit
    assert _metadata.get("data_label") == data_label
    assert _metadata.get("data_unit") == data_unit


if __name__ == "__main__":
    pytest.main()

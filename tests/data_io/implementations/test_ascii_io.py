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
from pydidas.data_io.implementations.ascii_io import AsciiIo


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
def test_import_from_file__chi__w_correct_ax_label(
    temp_path, written_ax_label, ax_label, ax_unit
):
    with open(temp_path / "test.chi", "w") as f:
        f.write("test.h5\n")
        f.write(f"{written_ax_label}\n")
        f.write("y data\n")
        f.write("\t62\n")
        for x, y in zip(_x_data, _y_data):
            f.write(f"{x:.6e}\t{y:.6e}\n")
    _data = AsciiIo.import_from_file(temp_path / "test.chi")
    assert np.allclose(_data, _y_data)
    assert np.allclose(_data.axis_ranges[0], _x_data)
    assert _data.axis_labels[0] == ax_label
    assert _data.axis_units[0] == ax_unit


def test_import_from_file__chi__incorrect_header(temp_path):
    with open(temp_path / "test.chi", "w") as f:
        f.write("test.h5\n")
        for x, y in zip(_x_data, _y_data):
            f.write(f"{x:.6e}\t{y:.6e}\n")
    with pytest.raises(FileReadError):
        _data = AsciiIo.import_from_file(temp_path / "test.chi")


@pytest.mark.parametrize(
    "labels, xlabel, xunit, ylabel, yunit",
    [
        (("2theta", "y data"), "", "", "2theta y data", ""),
        (("2theta (deg)", "y data (counts)"), "2theta", "deg", "y data", "counts"),
        (("2theta / deg", "y data_counts"), "2theta", "deg", "y data_counts", ""),
        (("2theta [deg]", "y data [counts]"), "2theta", "deg", "y data", "counts"),
        (("2theta / deg", "y data  / counts"), "2theta", "deg", "y data", "counts"),
        (("chi angle / deg", "y data  / ct"), "chi angle", "deg", "y data", "ct"),
        (("chi angle / deg", "y data  /"), "chi angle", "deg", "y data", ""),
    ],
)
def test_import_from_file__specfile_2col(
    temp_path, labels, xlabel, xunit, ylabel, yunit
):
    with open(temp_path / "test.dat", "w") as f:
        f.write("#F test.dat")
        f.write("#S 1 test.h5\n")
        f.write("#N 2\n")
        f.write(f"#L {labels[0]} {labels[1]}\n")
        for x, y in zip(_x_data, _y_data):
            f.write(f"{x:.6e}\t{y:.6e}\n")
    _data = AsciiIo.import_from_file(temp_path / "test.dat")
    assert np.allclose(_data, _y_data)
    assert np.allclose(_data.axis_ranges[0], _x_data)
    assert _data.axis_labels[0] == xlabel
    assert _data.axis_units[0] == xunit
    assert _data.data_label == ylabel
    assert _data.data_unit == yunit


@pytest.mark.parametrize(
    "labels", ["x / unit_a y / unit_b z / unit_c t / ms", "x y z t"]
)
def test_import_from_file__specfile_4col(temp_path, labels):
    with open(temp_path / "test.dat", "w") as f:
        f.write("#F test.dat")
        f.write("#S 1 test.h5\n")
        f.write("#N 4\n")
        f.write(f"#L {labels}\n")
        for x, y, z, t in zip(_x_data, _y_data, _y_data, _y_data):
            f.write(f"{x:.6e}\t{y:.6e}\t{z:.6e}\t{t:.6e}\n")
    _data = AsciiIo.import_from_file(temp_path / "test.dat")
    assert np.allclose(_data, np.asarray((_y_data, _y_data, _y_data)).T)
    assert np.allclose(_data.axis_ranges[0], _x_data)
    assert _data.axis_labels == {0: "x", 1: "0: y; 1: z; 2: t"}
    assert _data.axis_units == {0: "unit_a" if "unit_" in labels else "", 1: ""}
    assert (
        _data.data_label == "y / unit_b; z / unit_c; t / ms"
        if "unit_" in labels
        else "y z t"
    )
    assert _data.data_unit == ""


def test_export_to_file__chi(temp_path):
    AsciiIo.export_to_file(temp_path / "test_export.chi", _test_data, overwrite=True)
    with open(temp_path / "test_export.chi", "r") as f:
        _lines = f.readlines()
    assert _lines[0].strip() == "test_export.chi"
    assert _lines[1].strip() == _test_data.get_axis_description(0, sep="(")
    assert _lines[2].strip() == _test_data.get_data_description(sep="(")
    assert int(_lines[3].strip()) == _test_data.size
    _data = np.loadtxt(temp_path / "test_export.chi", skiprows=4)
    assert np.allclose(_data[:, 0], _test_data.axis_ranges[0])
    assert np.allclose(_data[:, 1], _test_data.array)


if __name__ == "__main__":
    pytest.main()

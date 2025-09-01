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

from pydidas.core import Dataset, FileReadError, UserConfigError
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


def get_data_with_ncols(ncols):
    if ncols == 1:
        return _test_data
    _new = np.column_stack((_test_data,) * ncols)
    _properties = _test_data.property_dict
    _properties["axis_labels"][1] = "stack axis"
    _properties["axis_units"][1] = ""
    _properties["axis_ranges"][1] = np.arange(ncols)
    return Dataset(_new, **_properties)


def test_export_to_file__higher_data_dim(temp_path):
    _temp_data = np.ones((10, 10, 10))
    with pytest.raises(UserConfigError):
        AsciiIo.export_to_file(
            temp_path / "test_export_3d.csv", _temp_data, overwrite=True
        )


def test_export_to_file__wrong_format(temp_path):
    with pytest.raises(UserConfigError):
        AsciiIo.export_to_file(
            temp_path / "test_export.silly_format", _test_data, overwrite=True
        )


@pytest.mark.parametrize("x_column", [True, False])
@pytest.mark.parametrize("input_type", [Dataset, np.ndarray])
@pytest.mark.parametrize("ncols", [1, 2, 3])
def test_export_to_file__x_column_keyword(temp_path, x_column, input_type, ncols):
    _temp_data = get_data_with_ncols(ncols)
    if input_type == np.ndarray:
        _temp_data = _temp_data.array
    # use .csv as example because it does not write and metadata
    AsciiIo.export_to_file(
        temp_path / "test_export.csv", _temp_data, x_column=x_column, overwrite=True
    )
    _reimported = np.loadtxt(temp_path / "test_export.csv", delimiter=",")
    if x_column:
        assert np.allclose(_reimported[:, 1:].squeeze(), _temp_data)
        if input_type == Dataset:
            assert np.allclose(_reimported[:, 0], _test_data.axis_ranges[0])
        else:
            assert np.allclose(_reimported[:, 0], np.arange(_temp_data.shape[0]))
    else:
        assert np.allclose(_reimported, _temp_data)


def test_export_to_file__w_str_filename(temp_path):
    AsciiIo.export_to_file(
        str(temp_path / "test_export.csv"), _test_data, overwrite=True
    )
    _imported_data = np.loadtxt(temp_path / "test_export.csv", delimiter=",")
    assert np.allclose(_imported_data[:, 0], _test_data.axis_ranges[0])
    assert np.allclose(_imported_data[:, 1], _test_data.array)


def test_export_to_file__chi__no_x_column(temp_path):
    with pytest.raises(UserConfigError):
        AsciiIo.export_to_file(
            temp_path / "test_export.chi", _test_data, x_column=False, overwrite=True
        )


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


def test_export_to_chi__2d_data(temp_path):
    _data = get_data_with_ncols(3)
    with pytest.raises(UserConfigError):
        AsciiIo.export_to_file(temp_path / "test_export.chi", _data, overwrite=True)


@pytest.mark.parametrize("ncols", [1, 2, 3])
@pytest.mark.parametrize("x_column", [True, False])
@pytest.mark.parametrize("metadata", [{}, {"test_key": "test_value"}])
def test_export_to_file__txt(temp_path, ncols, x_column, metadata):
    _temp_data = get_data_with_ncols(ncols)
    _temp_data.metadata = metadata
    AsciiIo.export_to_file(
        temp_path / "test_export.txt", _temp_data, x_column=x_column, overwrite=True
    )
    with open(temp_path / "test_export.txt", "r") as f:
        _lines = f.readlines()
    if x_column:
        assert f"# Axis label: {_temp_data.axis_labels[0]}\n" in _lines
        assert f"# Axis unit: {_temp_data.axis_units[0]}\n" in _lines
    if metadata:
        for _key, _val in metadata.items():
            assert f"#     {_key}: {_val}\n" in _lines
    assert f"# First column is x-axis: {x_column}\n" in _lines
    assert f"# Data label: {_temp_data.data_label}\n" in _lines
    assert f"# Data unit: {_temp_data.data_unit}\n" in _lines
    _imported_data = np.loadtxt(temp_path / "test_export.txt")
    if x_column:
        assert np.allclose(_imported_data[:, 0], _temp_data.axis_ranges[0])
        _imported_data = _imported_data[:, 1:].squeeze()
    assert np.allclose(_imported_data, _temp_data)


@pytest.mark.parametrize("ncols", [1, 2, 3])
@pytest.mark.parametrize("x_column", [True, False])
def test_export_to_file__specfile(temp_path, ncols, x_column):
    _temp_data = get_data_with_ncols(ncols)
    AsciiIo.export_to_file(
        temp_path / "test_export.dat", _temp_data, x_column=x_column, overwrite=True
    )
    with open(temp_path / "test_export.dat", "r") as f:
        _lines = f.readlines()
    assert "#F test_export.dat\n" in _lines
    assert f"#N {ncols + x_column}\n" in _lines
    _imported_data = np.loadtxt(temp_path / "test_export.dat")
    if x_column:
        assert np.allclose(_imported_data[:, 0], _temp_data.axis_ranges[0])
        _imported_data = _imported_data[:, 1:].squeeze()
    assert np.allclose(_imported_data, _temp_data)


def test_import_from_file__wrong_ext(temp_path):
    with pytest.raises(UserConfigError):
        AsciiIo.import_from_file(temp_path / "test.silly_ext")


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
    _header = f"test.h5\n{written_ax_label}\ny data / counts\n\t62\n"
    written_data = np.column_stack((_x_data, _y_data))
    np.savetxt(temp_path / "test_import.chi", written_data, header=_header, comments="")
    _data = AsciiIo.import_from_file(temp_path / "test_import.chi")
    assert np.allclose(_data, _y_data)
    assert np.allclose(_data.axis_ranges[0], _x_data)
    assert _data.axis_labels[0] == ax_label
    assert _data.axis_units[0] == ax_unit
    assert _data.data_label == "y data"
    assert _data.data_unit == "counts"


def test_import_from_file__chi__incorrect_header(temp_path):
    _header = "test.h5\n"
    written_data = np.column_stack((_x_data, _y_data))
    np.savetxt(temp_path / "test.chi", written_data, header=_header, comments="")
    with pytest.raises(FileReadError):
        _data = AsciiIo.import_from_file(temp_path / "test.chi")


@pytest.mark.parametrize("labels", ["x / unit_a", "x"])
def test_import_from_file__specfile_1col_w_xcol(temp_path, labels):
    _header = f"F test.dat\nS 1 test.h5\nN 1\nL {labels}\n"
    np.savetxt(temp_path / "test.dat", _x_data, header=_header, comments="#")
    with pytest.raises(UserConfigError):
        _data = AsciiIo.import_from_file(temp_path / "test.dat", x_column=True)


@pytest.mark.parametrize("labels", ["x / unit_a", "x"])
def test_import_from_file__specfile_1col(temp_path, labels):
    _header = f"F test.dat\nS 1 test.h5\nN 1\nL {labels}\n"
    np.savetxt(temp_path / "test.dat", _x_data, header=_header, comments="#")
    _data = AsciiIo.import_from_file(temp_path / "test.dat", x_column=False)
    assert np.allclose(_data, _x_data)
    assert np.allclose(_data.axis_ranges[0], np.arange(_x_data.size))
    assert _data.axis_labels == {0: ""}
    assert _data.axis_units == {0: ""}
    assert _data.data_label == "x"
    assert _data.data_unit == ("unit_a" if "unit_" in labels else "")


@pytest.mark.parametrize(
    "written_label, xlabel, xunit, ylabel, yunit",
    [
        ("2theta y data", "", "", "2theta y data", ""),
        ("2theta (deg) y data (counts)", "2theta", "deg", "y data", "counts"),
        ("2theta / deg y data_counts", "2theta", "deg", "y data_counts", ""),
        ("2theta [deg] y data [counts]", "2theta", "deg", "y data", "counts"),
        ("2theta / deg y data  / counts", "2theta", "deg", "y data", "counts"),
        ("chi angle / deg y data  / ct", "chi angle", "deg", "y data", "ct"),
        ("chi angle / deg y data  /", "chi angle", "deg", "y data", ""),
    ],
)
def test_import_from_file__specfile_2col_w_xcolumn(
    temp_path, written_label, xlabel, xunit, ylabel, yunit
):
    _header = f"F test.dat\nS 1 test.h5\nN 2\nL {written_label}\n"
    _temp_data = np.column_stack((_x_data, _y_data))
    np.savetxt(temp_path / "test.dat", _temp_data, header=_header, comments="#")
    _data = AsciiIo.import_from_file(temp_path / "test.dat", x_column=True)
    assert np.allclose(_data, _y_data)
    assert np.allclose(_data.axis_ranges[0], _x_data)
    assert _data.axis_labels[0] == xlabel
    assert _data.axis_units[0] == xunit
    assert _data.data_label == ylabel
    assert _data.data_unit == yunit


@pytest.mark.parametrize(
    "labels", ["x / unit_a y / u_b z / u_c t / ms", "x y z t", "x y", "a b c d e"]
)
@pytest.mark.parametrize("x_column", [True, False])
def test_import_from_file__specfile_4col(temp_path, labels, x_column):
    _header = f"F test.dat\nS 1 test.h5\nN 4\nL {labels}\n"
    _temp_data = np.column_stack((_x_data, _y_data, _y_data, _y_data))
    np.savetxt(temp_path / "test.dat", _temp_data, header=_header, comments="#")
    _data = AsciiIo.import_from_file(temp_path / "test.dat", x_column=x_column)
    if x_column:
        assert np.allclose(_data, np.asarray((_y_data, _y_data, _y_data)).T)
        assert np.allclose(_data.axis_ranges[0], _x_data)
    else:
        assert np.allclose(_data, np.asarray((_x_data, _y_data, _y_data, _y_data)).T)
        assert np.allclose(_data.axis_ranges[0], np.arange(_x_data.size))
    assert _data.axis_units == {
        0: "unit_a" if (x_column and "unit" in labels) else "",
        1: "",
    }
    if labels == "x y" and x_column:
        assert _data.axis_labels == {0: "x", 1: "0: y; 1: no label; 2: no label"}
        assert _data.data_label == "y; no label; no label"
    elif labels == "x y" and not x_column:
        assert _data.axis_labels == {0: "", 1: "0: x; 1: y; 2: no label; 3: no label"}
        assert _data.data_label == "x; y; no label; no label"
    elif labels == "a b c d e":
        assert _data.axis_labels == {0: "", 1: ""}
        assert _data.axis_units == {0: "", 1: ""}
        assert _data.data_label == "a b c d e"
    elif x_column:
        assert _data.axis_labels == {0: "x", 1: "0: y; 1: z; 2: t"}
        assert _data.axis_units == {0: "unit_a" if "unit_" in labels else "", 1: ""}
        assert (
            _data.data_label == "y / u_b; z / u_c; t / ms"
            if "unit_" in labels
            else "y z t"
        )
    else:
        assert _data.axis_labels == {0: "", 1: "0: x; 1: y; 2: z; 3: t"}
        assert (
            _data.data_label == "x / unit_a; y / u_b; z / u_c; t / ms"
            if "unit_" in labels
            else "x y z t"
        )
    assert _data.data_unit == ""


@pytest.mark.parametrize(
    "written_label", ["chi y_data", "chi / deg y_data / ct", "non matching labels"]
)
def test_import_from_file__specfile_2col_no_xcolumn(temp_path, written_label):
    _header = f"F test.dat\nS 1 test.h5\nN 2\nL {written_label}\n"
    _temp_data = np.column_stack((_x_data, _y_data))
    np.savetxt(temp_path / "test.dat", _temp_data, header=_header, comments="#")
    _data = AsciiIo.import_from_file(temp_path / "test.dat", x_column=False)
    assert np.allclose(_data, _temp_data)
    assert np.allclose(_data.axis_ranges[0], np.arange(_temp_data.shape[0]))
    if written_label == "non matching labels":
        assert _data.axis_labels == {0: "", 1: ""}
    else:
        assert _data.axis_labels == {0: "", 1: "0: chi; 1: y_data"}
    assert _data.axis_units == {0: "", 1: ""}
    assert _data.data_label == written_label.replace(" y_data", "; y_data")
    assert _data.data_unit == ""


@pytest.mark.parametrize("x_column", [True, False])
@pytest.mark.parametrize("ncols", [1, 2, 3, 4])
@pytest.mark.parametrize("extension", ["txt", "csv"])
@pytest.mark.parametrize("header", [True, False])
def test_import_from_file__txt(temp_path, x_column, ncols, extension, header):
    _temp_data = get_data_with_ncols(ncols)
    _fname = temp_path / f"test.{extension}"
    AsciiIo.export_to_file(
        _fname, _temp_data, x_column=x_column, write_header=header, overwrite=True
    )
    _data = AsciiIo.import_from_file(_fname, x_column=x_column)
    assert np.allclose(_data, _temp_data)
    _ax_ref = np.arange(_data.shape[0]) if not x_column else _temp_data.axis_ranges[0]
    assert np.allclose(_data.axis_ranges[0], _ax_ref)
    match ncols:
        case 1:
            assert _data.axis_labels == {
                0: "2theta" if (header and x_column) else "axis_0"
            }
            assert _data.axis_units == {0: "deg" if (header and x_column) else ""}
        case _:
            if header and x_column:
                assert _data.axis_labels == {0: "2theta", 1: ""}
                assert _data.axis_units == {0: "deg", 1: ""}
            else:
                assert _data.axis_labels == {0: "axis_0", 1: ""}
                assert _data.axis_units == {0: "", 1: ""}
    assert _data.data_label == ("test data" if header else "")
    assert _data.data_unit == ("counts" if header else "")


def test_import_from_file__txt__1d_w_xcolumn(temp_path):
    _temp_data = get_data_with_ncols(1)
    _fname = temp_path / "test_1d_no_x.txt"
    AsciiIo.export_to_file(
        _fname, _temp_data, x_column=False, write_header=False, overwrite=True
    )
    with pytest.raises(UserConfigError):
        AsciiIo.import_from_file(_fname, x_column=True)


if __name__ == "__main__":
    pytest.main()

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

import datetime
import time
from pathlib import Path

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
    metadata={"test_metadata": 42, "creator": "pytest"},
)

_TEST_DIR = Path(__file__).parents[2] / "_data"


def write_fio_file_with_n_col(filename, ncols=2):
    _fio_header = (
        "!\n! Comments\n!\n%c\nA random comment\nAnother comment\n!\n! Parameter\n!\n"
        "%p\nparam0 = 1\nparam1 = 2.0\nparam2 = -42\nparam3 = abc\n!\n! Data\n!\n%d\n"
    ) + "\n".join(f" Col {i + 1} c{i}_label DOUBLE" for i in range(ncols))
    _data = np.random.random((25, ncols))
    np.savetxt(filename, _data, header=_fio_header, comments="")
    return _data


def write_asc_file(filename, skip_keys: list[str] | None = None, write_header=True):
    _full_header = [
        "*TYPE		=  Raw\n",
        "*CLASS		=  ASCII CLASS\n",
        "*SAMPLE		= Test sample\n",
        "*COMMENT	=\n\n",
        "*SCAN_AXIS	=  2theta/theta\n",
        "*XUNIT		=  deg\n",
        "*YUNIT		=  cps\n",
        "*START		=  10\n",
        "*STOP		=  60\n",
        "*STEP		=  0.1\n",
        "*COUNT		=  501\n",
    ]
    if skip_keys and write_header:
        for _key in skip_keys:
            _full_header = [
                line for line in _full_header if not line.startswith(f"*{_key}")
            ]
    _full_header = "".join(_full_header) if write_header else ""
    _raw_data = (50 * np.random.random((501))).astype(int)
    _x_range = np.linspace(10, 60, 501)
    with open(filename, "w") as f:
        f.write(_full_header)
        for i in range(0, _raw_data.size, 4):
            _tmp = _raw_data[i : min(i + 4, _raw_data.size)]
            f.write(", ".join(f"{val:d}" for val in _tmp) + "\n")
    return _raw_data, _x_range


def get_data_with_ncols(ncols):
    if ncols == 1:
        return _test_data
    _new = (_test_data * (0.5 + np.arange(ncols)[:, None])).T
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
@pytest.mark.parametrize("x_column_index", [0, 1])
def test_import_from_file__specfile_2col_w_xcolumn(
    temp_path, written_label, xlabel, xunit, ylabel, yunit, x_column_index
):
    _header = f"F test.dat\nS 1 test.h5\n\nN 2\nL {written_label}\n"
    _temp_data = np.column_stack((_x_data, _y_data))
    np.savetxt(temp_path / "test.dat", _temp_data, header=_header, comments="#")
    _data = AsciiIo.import_from_file(
        temp_path / "test.dat", x_column=True, x_column_index=x_column_index
    )
    assert np.allclose(_data, _y_data if x_column_index == 0 else _x_data)
    assert np.allclose(
        _data.axis_ranges[0], _x_data if x_column_index == 0 else _y_data
    )
    if xlabel and ylabel:
        assert _data.axis_labels[0] == (xlabel if x_column_index == 0 else ylabel)
        assert _data.data_label == (ylabel if x_column_index == 0 else xlabel)
    else:
        assert _data.axis_labels == {0: ""}
        assert _data.data_label == ylabel
    assert _data.axis_units[0] == (xunit if x_column_index == 0 else yunit)
    assert _data.data_unit == (yunit if x_column_index == 0 else xunit)


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
        assert _data.metadata.get("raw_data_x_column") == 0
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


@pytest.mark.parametrize("x_column", [0, 1, 2, 3])
def test_import_from_file__specfile_4col_w_col_index(temp_path, x_column):
    _header = "F test.dat\nS 1 test.h5\nN 4\nL x / xu y / yu z / zu t / tu\n"
    _temp_data = (_y_data * (0.5 + np.arange(4))[:, None]).T
    np.savetxt(temp_path / "test.dat", _temp_data, header=_header, comments="#")
    _data = AsciiIo.import_from_file(
        temp_path / "test.dat", x_column=True, x_column_index=x_column
    )
    _ref_labels = ["x", "y", "z", "t"]
    _ref_units = ["xu", "yu", "zu", "tu"]
    _x_label = _ref_labels.pop(x_column)
    _x_unit = _ref_units.pop(x_column)
    _data_label = "; ".join(f"{_l} / {_u}" for _l, _u in zip(_ref_labels, _ref_units))
    _ax1_label = "; ".join(f"{i}: {_l}" for i, _l in enumerate(_ref_labels))
    assert np.allclose(_data, np.delete(_temp_data, x_column, axis=1))
    assert np.allclose(_data.axis_ranges[0], _y_data * (0.5 + x_column))
    assert _data.axis_labels == {0: _x_label, 1: _ax1_label}
    assert _data.axis_units == {0: _x_unit, 1: ""}
    assert _data.data_label == _data_label
    assert _data.data_unit == ""
    assert _data.metadata.get("raw_data_x_column") == x_column


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
    assert _data.metadata.get("raw_data_x_column", None) is None


@pytest.mark.parametrize("x_column", [True, False])
@pytest.mark.parametrize("ncols", [1, 2, 3, 4])
@pytest.mark.parametrize("extension", [".txt", ".csv"])
@pytest.mark.parametrize("header", [True, False])
def test_import_from_file__txt(temp_path, x_column, ncols, extension, header):
    _temp_data = get_data_with_ncols(ncols)
    _fname = temp_path / f"test{extension}"
    AsciiIo.export_to_file(
        _fname, _temp_data, x_column=x_column, write_header=header, overwrite=True
    )
    _data = AsciiIo.import_from_file(_fname, x_column=x_column)
    assert np.allclose(_data, _temp_data)
    _ax_ref = np.arange(_data.shape[0]) if not x_column else _temp_data.axis_ranges[0]
    assert np.allclose(_data.axis_ranges[0], _ax_ref)
    match ncols:
        case 1:
            assert _data.axis_labels == {0: "2theta" if (header and x_column) else ""}
            assert _data.axis_units == {0: "deg" if (header and x_column) else ""}
        case _:
            if header and x_column:
                assert _data.axis_labels == {0: "2theta", 1: ""}
                assert _data.axis_units == {0: "deg", 1: ""}
            else:
                assert _data.axis_labels == {0: "", 1: ""}
                assert _data.axis_units == {0: "", 1: ""}
    assert _data.data_label == ("test data" if header else "")
    assert _data.data_unit == ("counts" if header else "")
    assert _data.metadata.get("raw_data_x_column", -1) == (0 if x_column else -1)


@pytest.mark.parametrize("x_index", [0, 1, 2])
def test_import_from_file__txt__w_x_index(temp_path, x_index):
    _temp_data = get_data_with_ncols(3) + np.arange(3)[None, :]
    _fname = temp_path / "test.txt"
    AsciiIo.export_to_file(
        _fname, _temp_data, x_column=False, write_header=True, overwrite=True
    )
    _data = AsciiIo.import_from_file(_fname, x_column=True, x_column_index=x_index)
    assert np.allclose(_data, np.delete(_temp_data, x_index, axis=1))
    assert np.allclose(_data.axis_ranges[0], _temp_data[:, x_index])
    assert _data.metadata.get("raw_data_x_column", -1) == x_index


def test_import_from_file__txt__w_metadata_x_column_and_index_none(temp_path):
    _fname = temp_path / "test.txt"
    AsciiIo.export_to_file(
        _fname, _test_data, x_column=True, write_header=True, overwrite=True
    )
    _data = AsciiIo.import_from_file(_fname, x_column=False, x_column_index=None)
    assert np.allclose(_data, _test_data)
    assert np.allclose(_data.axis_ranges[0], _test_data.axis_ranges[0])


def test_import_from_file__txt__1d_w_xcolumn(temp_path):
    _temp_data = get_data_with_ncols(1)
    _fname = temp_path / "test_1d_no_x.txt"
    AsciiIo.export_to_file(
        _fname, _temp_data, x_column=False, write_header=False, overwrite=True
    )
    with open(_fname, "r") as f:
        _lines = f.readlines()
    with pytest.raises(UserConfigError):
        AsciiIo.import_from_file(_fname, x_column=True)


def test_import_from_file__fio__1d_w_xcol():
    with pytest.raises(UserConfigError):
        AsciiIo.import_from_file(_TEST_DIR / "fio_spectrum.fio", x_column=True)


def test_import_from_file__fio__1d_no_xcol():
    _fname = _TEST_DIR / "fio_spectrum.fio"
    _data = AsciiIo.import_from_file(_fname, x_column=False)
    assert np.allclose(_data, np.loadtxt(_fname, skiprows=13).squeeze())
    assert np.allclose(_data.axis_ranges[0], np.arange(_data.size))
    assert _data.axis_labels[0] == "index"
    assert _data.data_label == "test_spectrum"
    assert _data.metadata.get("raw_data_x_column", None) is None


def test_import_from_file__fio__empty_file(temp_path):
    _fname = temp_path / "test_empty.fio"
    with open(_fname, "w") as f:
        f.write("")
    with pytest.raises(FileReadError):
        AsciiIo.import_from_file(_fname)


def test_import_from_file__fio__no_data_in_file(temp_path):
    _fname = temp_path / "test_no_data.fio"
    with open(_fname, "w") as f:
        f.write(
            "!Test\n%c\nA comment%\n! No data section\n%d \n Col 0 Test DOUBLE\n"
            " Col 1 Test2 DOUBLE\n! Final comment"
        )
    with pytest.raises(FileReadError):
        AsciiIo.import_from_file(_fname)


@pytest.mark.parametrize("xcol", [0, 1])
def test_import_from_file__fio__2d_w_xcolumn(temp_path, xcol):
    _fname = temp_path / "test.fio"
    _raw_data = write_fio_file_with_n_col(_fname, ncols=2)
    _data = AsciiIo.import_from_file(_fname, x_column=True, x_column_index=xcol)
    _keys = ["c0_label", "c1_label"]
    assert _data.ndim == 1
    assert np.allclose(_data, _raw_data[:, 1 - xcol].squeeze())
    assert np.allclose(_data.axis_ranges[0], _raw_data[:, xcol])
    assert _data.axis_labels[0] == _keys[xcol]
    assert _data.data_label == _keys[1 - xcol]
    assert _data.metadata.get("raw_data_x_column", -1) == xcol


@pytest.mark.parametrize("x_column", [0, 1, 2, 3])
def test_import_from_file__fio_file__w_xcol(temp_path, x_column):
    _fname = temp_path / "test.fio"
    _raw_data = write_fio_file_with_n_col(_fname, ncols=4)
    _data = AsciiIo.import_from_file(_fname, x_column=True, x_column_index=x_column)
    _keys = ["c0_label", "c1_label", "c2_label", "c3_label"]
    _xlabel = _keys.pop(x_column)
    _x_range = _raw_data[:, x_column]
    _raw_data = np.delete(_raw_data, x_column, axis=1)
    assert _data.axis_labels[0] == _xlabel
    assert _data.axis_labels[1] == "; ".join(f"{i}: {_k}" for i, _k in enumerate(_keys))
    assert _data.axis_units[0] == ""
    assert np.allclose(_data.axis_ranges[0], _x_range)
    assert np.allclose(_data, _raw_data)
    assert _data.data_label == "; ".join(_keys)
    assert _data.data_unit == ""
    assert _data.metadata.get("raw_data_x_column", -1) == x_column


def test_import_from_file__fio_file__no_xcol(temp_path):
    _fname = temp_path / "test.fio"
    _raw_data = write_fio_file_with_n_col(_fname, ncols=4)
    _data = AsciiIo.import_from_file(_fname, x_column=False)
    _keys = ["c0_label", "c1_label", "c2_label", "c3_label"]
    assert np.allclose(_data, _raw_data)
    assert np.allclose(_data.axis_ranges[0], np.arange(_raw_data.shape[0]))
    assert _data.axis_labels[0] == "index"
    assert _data.axis_labels[1] == "; ".join(f"{i}: {_k}" for i, _k in enumerate(_keys))
    assert _data.axis_units == {0: "", 1: ""}
    assert _data.data_label == "; ".join(_keys)
    assert _data.metadata.get("raw_data_x_column", None) is None


def test_import_from_file__asc__full_header(temp_path):
    _raw_data, _x_range = write_asc_file(temp_path / "test.asc")
    _data = AsciiIo.import_from_file(temp_path / "test.asc")
    assert np.allclose(_data, _raw_data)
    assert np.allclose(_data.axis_ranges[0], _x_range)
    assert _data.axis_labels[0] == "2theta/theta"
    assert _data.axis_units[0] == "deg"
    assert _data.data_label == "Test sample"
    assert _data.data_unit == "cps"
    assert _data.metadata.get("raw_data_x_column", None) is None


@pytest.mark.parametrize(
    "skip_key", ["XUNIT", "YUNIT", "START", "STOP", "STEP", "SAMPLE", "SCAN_AXIS"]
)
def test_import_from_file__asc__partial_header(temp_path, skip_key):
    _raw_data, _x_range = write_asc_file(temp_path / "test.asc", skip_keys=[skip_key])
    _data = AsciiIo.import_from_file(temp_path / "test.asc")
    _ax = "" if skip_key == "SCAN_AXIS" else "2theta/theta"
    if skip_key in ["START", "STOP", "STEP"]:
        _x_range = np.arange(_raw_data.size)
        _ax = "index"
    assert np.allclose(_data, _raw_data)
    assert np.allclose(_data.axis_ranges[0], _x_range)
    assert _data.axis_labels[0] == _ax
    assert _data.axis_units[0] == ("deg" if skip_key != "XUNIT" else "")
    assert _data.data_label == ("Test sample" if skip_key != "SAMPLE" else "")
    assert _data.data_unit == ("cps" if skip_key != "YUNIT" else "")
    assert _data.metadata.get("raw_data_x_column", None) is None


def test_import_from_file__asc__no_header(temp_path):
    _raw_data, _x_data = write_asc_file(temp_path / "test.asc", write_header=False)
    _data = AsciiIo.import_from_file(temp_path / "test.asc")
    assert _data.shape == (501,)
    assert np.allclose(_data, _raw_data)
    assert np.allclose(_data.axis_ranges[0], np.arange(_raw_data.size))
    assert _data.axis_labels[0] == "index"
    assert _data.axis_units[0] == ""
    assert _data.data_label == ""
    assert _data.data_unit == ""


def test_read_metadata_from_file__wrong_ext(temp_path):
    with pytest.raises(UserConfigError):
        _metadata = AsciiIo.read_metadata_from_file(temp_path / "test_empty.dummy")


@pytest.mark.parametrize("suffix", AsciiIo.extensions_import)
def test_read_metadata_from_file__empty_file(temp_path, suffix):
    _fname = temp_path / f"test_empty{suffix}"
    with open(_fname, "w") as f:
        f.write("")
    _metadata = AsciiIo.read_metadata_from_file(_fname)
    if suffix == ".fio":
        assert _metadata == {"comments": [], "parameters": {}, "data_columns": []}
    else:
        assert _metadata == {}


def test_read_metadata_from_file__chi(temp_path):
    _fname = temp_path / "test.chi"
    AsciiIo.export_to_file(_fname, _test_data, overwrite=True)
    _metadata = AsciiIo.read_metadata_from_file(_fname)
    assert _metadata["title"] == _fname.name
    assert _metadata["x_axis"] == _test_data.get_axis_description(0, sep="(")
    assert _metadata["data"] == _test_data.get_data_description(sep="(")
    assert _metadata["n_points"] == _test_data.size


def test_read_metadata_from_file__specfile(temp_path):
    _fname = temp_path / "test.dat"
    _epoch = time.time()
    _datetime = datetime.datetime.now()
    AsciiIo.export_to_file(_fname, _test_data, x_column=True, overwrite=True)
    _metadata = AsciiIo.read_metadata_from_file(_fname)
    assert _metadata["filename"] == _fname.name
    assert _metadata["epoch"] - _epoch < 5  # within 5 seconds
    assert (
        _datetime
        - datetime.datetime.strptime(_metadata["date"], "%a %b %d %H:%M:%S %Y")
    ).seconds < 5
    assert _metadata["n_columns"] == 2
    assert _metadata["scan_title"] == "1 pydidas results"
    assert _metadata["labels"] == _test_data.get_axis_description(
        0, sep="("
    ) + " " + _test_data.get_data_description(sep="(")


def test_read_metadata_from_file__specfile__corrupt_header(temp_path):
    with open(temp_path / "test.dat", "w") as f:
        f.write("#N ab\n1 2 3\n4 5 6\n7 8 9\n")
    with pytest.raises(UserConfigError):
        _metadata = AsciiIo.read_metadata_from_file(temp_path / "test.dat")


@pytest.mark.parametrize("ncols", [1, 2, 3])
@pytest.mark.parametrize("x_column", [True, False])
def test_read_metadata_from_file__txt(temp_path, ncols, x_column):
    _fname = temp_path / "test.txt"
    _data = get_data_with_ncols(ncols)
    AsciiIo.export_to_file(_fname, _data, x_column=x_column, overwrite=True)
    _metadata = AsciiIo.read_metadata_from_file(_fname)
    assert _metadata["metadata"] == _data.metadata
    if x_column:
        assert _metadata["Axis label"] == _data.axis_labels[0]
        assert _metadata["Axis unit"] == _data.axis_units[0]
    else:
        assert "Axis label" not in _metadata
        assert "Axis unit" not in _metadata
    assert _metadata["First column is x-axis"] == str(x_column)
    assert _metadata["Data label"] == _data.data_label
    assert _metadata["Data unit"] == _data.data_unit
    assert "Metadata" not in _metadata


def test_read_metadata_from_file__txt_corrupt_header(temp_path):
    _fname = temp_path / "test.txt"
    with open(_fname, "w") as f:
        f.write("# This is a corrupt header line:\n1 2 3\n4 5 6\n7 8 9\n")
    _metadata = AsciiIo.read_metadata_from_file(_fname)


def test_read_metadata_from_file__fio_corrupt_header(temp_path):
    _fname = temp_path / "test.fio"
    with open(_fname, "w") as f:
        f.write("%p\ntest\n")
    with pytest.raises(UserConfigError):
        AsciiIo.read_metadata_from_file(_fname)


@pytest.mark.parametrize("ncols", [1, 2, 3])
def test_read_metadata_from_file__fio(temp_path, ncols):
    _fname = temp_path / "test.fio"
    _data = write_fio_file_with_n_col(_fname, ncols=ncols)
    _metadata = AsciiIo.read_metadata_from_file(_fname)
    assert _metadata["comments"] == ["A random comment", "Another comment"]
    assert _metadata["parameters"] == {
        "param0": 1,
        "param1": 2.0,
        "param2": -42,
        "param3": "abc",
    }
    assert _metadata["data_columns"] == [
        (
            f"Col {i + 1} c{i}_label DOUBLE    [note: in Python indexing, this column "
            f"is indexed as #{i}]"
        )
        for i in range(ncols)
    ]


@pytest.mark.parametrize("skip_key", ["XUNIT", "YUNIT", "START", "STOP", "STEP"])
def test_read_metadata_from_file__asc(temp_path, skip_key):
    _fname = temp_path / "test.asc"
    _, _ = write_asc_file(_fname, skip_keys=[skip_key])
    _metadata = AsciiIo.read_metadata_from_file(_fname)
    with open(_fname, "r") as f:
        _metadata_ref = {
            _key.removeprefix("*").strip(): _val.strip()
            for _line in f.readlines()
            if _line.startswith("*") and "=" in _line
            for _key, _val in [_line.split("=", 1)]
        }
    for _key, _val in _metadata_ref.items():
        assert _metadata[_key] == _val


if __name__ == "__main__":
    pytest.main()

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

"""
Module with the TiffIo class for importing and exporting tiff data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["decode_chi_header", "decode_specfile_header", "decode_txt_header"]


from pathlib import Path

from pydidas.core import FileReadError
from pydidas.core.utils import CatchFileErrors


def decode_chi_header(filename: Path | str) -> tuple[str, str, str, str]:
    """
    Decode the header of a CHI file.

    Parameters
    ----------
    filename : Path | str
        The filename of the CHI file to be decoded.

    Returns
    -------
    tuple[str, str, str, str]
        The data label, data unit, x-label and x-unit.
    """
    with CatchFileErrors(filename), open(filename, "r") as _file:
        _lines = _file.readlines()
    try:
        _size = int(_lines[3].strip())
    except Exception:
        raise FileReadError("Cannot read CHI header.")
    _meta: dict[str, str] = {}
    for _key, _line_no in (("data", 2), ("ax", 1)):
        _label = _lines[_line_no].strip()
        _unit = ""
        if "(" in _label and ")" in _label:
            _label, _unit = _label.strip().rsplit("(", 1)
            _unit = _unit.rstrip(")")
        elif "_" in _label:
            _label, _unit = _label.strip().rsplit("_", 1)
        elif "/" in _label:
            _label, _unit = _label.split("/", 1)
        _meta[f"{_key}_label"] = _label.strip()
        _meta[f"{_key}_unit"] = _unit.strip()
    return _meta["data_label"], _meta["data_unit"], _meta["ax_label"], _meta["ax_unit"]


def __split_key_list(key_list: list[str]) -> tuple[list[str], list[str]]:
    """Split a list of labels and units into separate lists."""
    _units = []
    _labels = []
    _curr = ""
    while key_list:
        _label = key_list.pop(0)
        if _label == "/":
            _labels.append(_curr)
            if key_list:
                _units.append(key_list.pop(0))
            _curr = ""
        elif _label.startswith("(") or _label.startswith("["):
            _labels.append(_curr)
            _units.append(_label.lstrip("([").rstrip("])"))
            _curr = ""
        else:
            _curr = (_curr + " " + _label).strip()
    if _curr:
        _labels.append(_curr)
        _units.append("")
    return _labels, _units


def decode_specfile_header(
    filename: Path | str, read_x_column: bool = True
) -> tuple[list[str], list[str]]:  # noqa
    """
    Decode the header of a SpecFile (.dat) file.

    Parameters
    ----------
    filename : Path | str
        The filename of the SpecFile to be decoded.
    read_x_column : bool, optional
        Whether to read the first column as x column label and unit. If False,
        all columns are assumed to be y data columns. The default is True.

    Returns
    -------
    tuple[list[str], list[str]]
        The axis labels and axis units.
    """
    _n_col = None
    _raw_labels = ""
    with CatchFileErrors(filename), open(filename, "r") as _file:
        _lines = _file.readlines()
    for _line in _lines:
        if _line.startswith("#N") and _n_col is None:
            _n_col = int(_line.removeprefix("#N"))
        elif _line.startswith("#L"):
            _raw_labels = _line.removeprefix("#L").strip()
        elif not _line.startswith("#") and _n_col is None:
            _n_col = len(_line.split())
        if _n_col is not None and _raw_labels:
            break
    _labels_split = _raw_labels.split()
    _units = []
    # Create initial label and unit lists
    if len(_labels_split) == _n_col == 2 and read_x_column:
        return _labels_split, ["", ""]
    elif len(_labels_split) <= _n_col:
        _labels = _labels_split + [""] * (_n_col - len(_labels_split))
        _units = [""] * _n_col
    else:
        _labels, _units = __split_key_list(_labels_split)

    # Modify label and unit lists to fit n_col and read_x_column parameter
    if _n_col == 1:
        _labels = [""] * (2 - len(_labels)) + _labels
        _units = [""] * (2 - len(_units)) + _units
    elif _n_col == 2 and read_x_column:
        if len(_labels) > len(_units):
            _units = _units + [""] * (len(_labels) - len(_units))
        else:
            _units = [""] * (_n_col - len(_units)) + _units
        _labels = [""] * (_n_col - len(_labels)) + _labels
    else:
        _labels = _labels + [""] * (_n_col - len(_labels))
        if "" in _labels and any(_labels):
            _labels = [_l if _l else "no label" for _l in _labels]
        _units = _units + [""] * (_n_col - len(_units))
        _i_start = 1 if read_x_column else 0
        _col_label = (
            ""
            if not all(_labels)
            else "; ".join(
                f"{i}: {_l if _l else 'no label'}"
                for i, _l in enumerate(_labels[_i_start:])
            )
        )
        _data_label = "; ".join(
            (f"{_l} / {_u}" if _u else _l)
            for _l, _u in zip(_labels[_i_start:], _units[_i_start:])
            if _l or _u
        )
        _labels = [_labels[0] if read_x_column else "", _col_label, _data_label]
        _units = [_units[0] if _units and read_x_column else "", "", ""]
    return _labels, _units


def decode_txt_header(filename: Path | str) -> dict[str, str]:
    """
    Decode the header of a TXT file.

    Parameters
    ----------
    filename : Path | str
        The filename of the TXT file to be decoded.

    Returns
    -------
    dict[str, str]
        The dictionary with any found keys.
    """
    with CatchFileErrors(filename), open(filename, "r") as _file:
        _lines = _file.readlines()
    _metadata = {}
    for _line in _lines:
        if _line.startswith("# Axis label:"):
            _metadata["ax_label"] = _line.removeprefix("# Axis label:").strip()
        elif _line.startswith("# Axis unit:"):
            _metadata["ax_unit"] = _line.removeprefix("# Axis unit:").strip()
        elif _line.startswith("# Data label:"):
            _metadata["data_label"] = _line.removeprefix("# Data label:").strip()
        elif _line.startswith("# Data unit:"):
            _metadata["data_unit"] = _line.removeprefix("# Data unit:").strip()
        if not _line.startswith("#"):
            break
    return _metadata

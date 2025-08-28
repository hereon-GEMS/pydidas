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


def decode_chi_header(filename: Path | str) -> tuple[str, str, str]:
    """
    Decode the header of a CHI file.

    Parameters
    ----------
    filename : Path | str
        The filename of the CHI file to be decoded.

    Returns
    -------
    tuple[str, str, str]
        The data label, x-label and x-unit.
    """
    with CatchFileErrors(filename), open(filename, "r") as _file:
        _lines = _file.readlines()
    try:
        _size = int(_lines[3].strip())
    except Exception:
        raise FileReadError("Cannot read CHI header.")
    _data_label = _lines[2].strip()
    _ax_unit = ""
    _ax_label = _lines[1].strip()
    if "(" in _ax_label and ")" in _ax_label:
        _ax_label, _ax_unit = _ax_label.strip().rsplit("(", 1)
        _ax_unit = _ax_unit.rstrip(")")
    elif "_" in _ax_label:
        _ax_label, _ax_unit = _ax_label.strip().rsplit("_", 1)
    return _data_label, _ax_label.strip(), _ax_unit.strip()


def decode_specfile_header(filename: Path | str) -> tuple[list[str], list[str]]:  # noqa
    """
    Decode the header of a SpecFile (.dat) file.

    Parameters
    ----------
    filename : Path | str
        The filename of the SpecFile to be decoded.

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
        if _line.startswith("#N"):
            _n_col = int(_line.removeprefix("#N"))
            break
    for _line in _lines:
        if _line.startswith("#L"):
            _raw_labels = _line.removeprefix("#L").strip()
            break
    if not _n_col:
        for _line in _lines:
            if not _line.startswith("#"):
                _n_col = len(_line.split())
                break
    _labels_split = _raw_labels.split()
    _units = []
    if len(_labels_split) == _n_col == 2:
        return _labels_split, ["", ""]
    elif len(_labels_split) == _n_col:
        _labels = _labels_split
    else:
        _labels = []
        _curr = ""
        while _labels_split:
            _label = _labels_split.pop(0)
            if _label == "/":
                _labels.append(_curr)
                if _labels_split:
                    _units.append(_labels_split.pop(0))
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
    if _n_col == 1:
        _labels = [""] * (2 - len(_labels)) + _labels
        _units = [""] * (2 - len(_units)) + _units
    elif _n_col == 2:
        if len(_labels) > len(_units):
            _units = _units + [""] * (len(_labels) - len(_units))
        else:
            _units = [""] * (_n_col - len(_units)) + _units
        _labels = [""] * (_n_col - len(_labels)) + _labels
    else:
        _labels = _labels + [""] * (_n_col - len(_labels))
        _units = _units + [""] * (_n_col - len(_units))
        _labels = [
            _labels[0],
            "; ".join(
                f"{i}: {_l if _l else 'no label'}"
                for i, _l in enumerate(_labels[1:], start=0)
            ),
            "; ".join(
                (f"{_l} / {_u}" if _u else _l)
                for _l, _u in zip(_labels[1:], _units[1:])
                if _l or _u
            ),
        ]
        _units = [_units[0] if _units else "", "", ""]
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

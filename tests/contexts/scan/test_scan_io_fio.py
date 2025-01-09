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


import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional

import pytest

from pydidas.contexts import ScanContext
from pydidas.contexts.scan import Scan
from pydidas.contexts.scan.scan_io_fio import ScanIoFio
from pydidas.core import UserConfigError


_TEST_DIR = Path(__file__).parents[2]


@pytest.fixture
def reset_scan_context():
    _scan = ScanContext()
    _scan.restore_all_defaults(confirm=True)
    _scan.set_param_value("scan_dim", 4)


@pytest.fixture
def temp_dir():
    _temp_path = Path(tempfile.mkdtemp())
    yield _temp_path
    shutil.rmtree(_temp_path)


def assert_general_1d_scan_params_in_order(scan: ScanContext, filename: Path):
    """
    Asserts the general scan parameters have been reset correctly during the import.
    """
    assert scan.get_param_value("scan_dim") == 1
    assert scan.get_param_value("scan_start_index") == 0
    assert scan.get_param_value("scan_index_stepping") == 1
    assert scan.get_param_value("scan_multiplicity") == 1
    assert scan.get_param_value("scan_name_pattern") == Path(filename.stem)
    assert scan.get_param_value("scan_base_directory") == filename.parents[1]


@pytest.mark.parametrize("scan", [ScanContext(), Scan(), None])
@pytest.mark.parametrize("scan_type", ["ascan", "dscan"])
def test_import_from_single_file__validation(
    scan: Optional[Scan], scan_type: str, reset_scan_context
):
    _filename = _TEST_DIR.joinpath("_data", f"test_single_fio_{scan_type}.fio")
    ScanIoFio.import_from_file(_filename, scan=scan)
    if scan is None:
        scan = ScanContext()
    assert scan.get_param_value("scan_dim0_offset") == 10.0
    assert scan.get_param_value("scan_dim0_delta") == 2.0
    assert scan.get_param_value("scan_dim0_label") == "cube1_x"
    assert scan.get_param_value("scan_dim0_n_points") == 35
    assert_general_1d_scan_params_in_order(scan, _filename)
    if scan != ScanContext():
        assert ScanContext().get_param_value("scan_dim") == 4


def test_import_from_single_file__corrupt(reset_scan_context, temp_dir):
    _filepath = temp_dir.joinpath("test.fio")
    with open(_filepath, "w") as _file:
        _file.write("corrupt\n\n")
        _file.write("ascan x -5 5 11 1.0\n")
        _file.write("dscan y -5 5 11 1.0\n")
    ScanIoFio.imported_params = {"test_entry": True}
    with pytest.raises(UserConfigError):
        ScanIoFio.import_from_file(_filepath)
    assert ScanIoFio.imported_params == {}


def test_import_from_single_file__empty(reset_scan_context, temp_dir):
    _filepath = temp_dir.joinpath("test.fio")
    with open(_filepath, "w") as _file:
        _file.write("")
    ScanIoFio.imported_params = {"test_entry": True}
    with pytest.raises(UserConfigError):
        ScanIoFio.import_from_file(_filepath)
    assert ScanIoFio.imported_params == {}


@pytest.mark.parametrize("scan", [ScanContext(), Scan(), None])
@pytest.mark.parametrize("scan_type", ["ascan", "dscan"])
def test_import_from_multiple_files__validation(scan: Optional[Scan], scan_type: str, reset_scan_context):
    filenames = [
        _TEST_DIR.joinpath("_data", f"2d_mesh_fio_{scan_type}", f"2dmesh_{i:05d}.fio")
        for i in range(1, 11)
    ]

    ScanIoFio.import_from_file(filenames, scan=scan)

    if scan is None:
        scan = ScanContext()
    #
    print(scan_type, scan.param_values)

    assert 9.9 < scan.get_param_value("scan_dim0_offset") < 10.1
    assert 2.05 < scan.get_param_value("scan_dim0_delta") < 2.15
    assert scan.get_param_value("scan_dim0_label") == "cube1_y"
    assert scan.get_param_value("scan_dim0_n_points") == 10

    assert scan.get_param_value("scan_dim1_offset") == 10.0
    assert 2.0 < scan.get_param_value("scan_dim1_delta") < 2.1
    assert scan.get_param_value("scan_dim1_label") == "cube1_x"
    assert scan.get_param_value("scan_dim1_n_points") == 34


def test_import_from_file__corrupt_file():
    SCAN = ScanContext()
    # _test_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    # filenames = [_test_dir+r'\_data\test_single_fio.fio']
    _tmppath = tempfile.mkdtemp()
    _tmpfile = tempfile.mkstemp(dir=_tmppath)
    with pytest.raises(UserConfigError):
        ScanIoFio.import_from_file([_tmpfile[1]], scan=SCAN)
    assert ScanIoFio.imported_params == {}
    os.close(_tmpfile[0])
    os.remove(_tmpfile[1])

    os.rmdir(_tmppath)


if __name__ == "__main__":
    pytest.main()

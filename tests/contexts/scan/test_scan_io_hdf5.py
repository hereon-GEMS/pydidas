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


import shutil
import tempfile
from pathlib import Path
from typing import Any

import h5py
import numpy as np
import pytest

from pydidas.contexts import Scan, ScanContext
from pydidas.contexts.scan.scan_io_hdf5 import ScanIoHdf5
from pydidas.core import UserConfigError
from pydidas.core.utils import create_nx_entry_groups, get_random_string
from pydidas.core.utils.hdf5_dataset_utils import (
    export_context_to_hdf5,
    read_and_decode_hdf5_dataset,
)


SCAN = ScanContext()
SCAN_IO_HDF5 = ScanIoHdf5

PARAMS_WITH_INT = [
    "scan_dim0_n_points",
    "scan_dim1_n_points",
    "scan_dim2_n_points",
    "scan_dim3_n_points",
    "scan_start_index",
    "scan_multiplicity",
    "scan_index_stepping",
]
PARAMS_WITH_STR = [
    "scan_dim0_label",
    "scan_dim0_unit",
    "scan_dim1_label",
    "scan_dim1_unit",
    "scan_dim2_label",
    "scan_dim2_unit",
    "scan_dim3_label",
    "scan_dim3_unit",
    "scan_name_pattern",
    "scan_base_directory",
    "scan_title",
]


@pytest.fixture(scope="module")
def temp_dir() -> Path:
    """Fixture to create a temporary directory."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def modify_scan_context(temp_dir) -> dict[str, Any]:
    """Fixture to modify the DiffractionExperimentContext."""
    _randomize_scan(SCAN, temp_dir)
    yield {_key: _param.value_for_export for _key, _param in SCAN.params.items()}
    SCAN.restore_all_defaults(True)


def _randomize_scan(scan: Scan, local_dir: Path):
    for _key, _param in scan.params.items():
        if _key in PARAMS_WITH_INT:
            _val = int(1000 * np.random.rand()) + 5
        elif _key in PARAMS_WITH_STR:
            _val = get_random_string(6)
        elif _key == "scan_dim":
            _val = np.random.randint(1, 5)
        elif _key == "scan_multi_image_handling":
            _val = np.random.choice(["Average", "Sum", "Maximum"])
        else:
            _val = np.round(0.5 + 5 * np.random.rand(), decimals=5)
        scan.set_param_value(_key, _val)


@pytest.fixture
def create_hdf5_file(temp_dir) -> Path:
    """Fixture to create a temporary HDF5 file."""
    hdf5_filename = temp_dir / "scan_io_hdf5.h5"
    export_context_to_hdf5(hdf5_filename, SCAN, "entry/pydidas_config/scan")
    return hdf5_filename


def test_export_to_file__correct(modify_scan_context, temp_dir):
    """Test the export_to_file method."""
    hdf5_file = temp_dir / "scan_io_hdf5.h5"
    SCAN_IO_HDF5.export_to_file(hdf5_file)
    with h5py.File(hdf5_file, "r") as file:
        _group = file["entry/pydidas_config/scan"]
        for _key, _param in SCAN.params.items():
            assert (
                read_and_decode_hdf5_dataset(_group[_key]) == modify_scan_context[_key]
            )


def test_export_to_file__w_scan(temp_dir):
    """Test the export_to_file method with a custom Scan."""
    local_SCAN = Scan()
    _randomize_scan(local_SCAN, temp_dir)
    hdf5_file = temp_dir / "local_scan_io_hdf5.h5"
    SCAN_IO_HDF5.export_to_file(hdf5_file, scan=local_SCAN)
    with h5py.File(hdf5_file, "r") as file:
        _group = file["entry/pydidas_config/scan"]
        for _key, _param in SCAN.params.items():
            assert (
                read_and_decode_hdf5_dataset(_group[_key])
                == local_SCAN.params[_key].value_for_export
            )


def test_import_from_file__empty_file(temp_dir):
    _fname = temp_dir / "empty_file.h5"
    with h5py.File(_fname, "w") as file:
        create_nx_entry_groups(
            file, "entry/pydidas_config/scan", group_type="NXcollection"
        )
    with pytest.raises(UserConfigError):
        SCAN_IO_HDF5.import_from_file(_fname)


def test_import_from_file(temp_dir, modify_scan_context, create_hdf5_file):
    """Test the import_from_file method."""
    SCAN_IO_HDF5.import_from_file(create_hdf5_file)
    for _key, _param in SCAN.params.items():
        assert SCAN.params[_key].value_for_export == modify_scan_context[_key]


def test_import_from_file__to_local_context(
    temp_dir, modify_scan_context, create_hdf5_file
):
    """Test the import_from_file method."""
    local_SCAN = Scan()
    SCAN_IO_HDF5.import_from_file(create_hdf5_file, scan=local_SCAN)
    for _key, _param in local_SCAN.params.items():
        assert SCAN.params[_key].value_for_export == modify_scan_context[_key]


if __name__ == "__main__":
    pytest.main()

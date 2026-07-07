# This h5file is part of pydidas.
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


import shutil
import tempfile
from pathlib import Path
from typing import Any, Generator

import h5py
import numpy as np
import pytest

from pydidas.contexts import DiffractionExperiment, Scan, ScanContext
from pydidas.contexts.scan.scan import SCAN_LEGACY_PARAMS
from pydidas.contexts.scan.scan_io_hdf5 import ScanIoHdf5
from pydidas.core import UserConfigError
from pydidas.core.utils import get_random_string
from pydidas.core.utils.hdf5 import (
    get_hdf5_populated_dataset_keys,
    nxs_create_recursive_groups,
    read_and_decode_hdf5_dataset,
)
from pydidas.core.utils.hdf5.nxs_export import nxs_export_context
from pydidas.unittest_objects import create_hdf5_results_file
from pydidas.unittest_objects.create_dataset_ import create_dataset
from pydidas.workflow.processing_tree import ProcessingTree


SCAN = ScanContext()
SCAN_IO_HDF5 = ScanIoHdf5

PARAMS_WITH_INT = [
    "scan_dim0_n_points",
    "scan_dim1_n_points",
    "scan_dim2_n_points",
    "scan_dim3_n_points",
    "pattern_number_offset",
    "pattern_number_delta",
    "scan_frames_per_point",
    "frame_indices_per_scan_point",
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
_TEST_DIR = Path(__file__).parents[2]
_TEST_DATA = create_dataset(3)


@pytest.fixture(scope="module")
def temp_dir() -> Generator[Path, Any, Any]:
    """Fixture to create a temporary directory."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def modify_scan_context() -> Generator[dict[str, Any], Any, Any]:
    """Fixture to modify the DiffractionExperimentContext."""
    _randomize_scan(SCAN)
    yield {_key: _param.value_for_export for _key, _param in SCAN.params.items()}
    SCAN.restore_all_defaults(True)


def _randomize_scan(scan: Scan):
    for _key, _param in scan.params.items():
        if _key in PARAMS_WITH_INT:
            _val = int(1000 * np.random.rand()) + 5
        elif _key in PARAMS_WITH_STR:
            _val = get_random_string(6)
        elif _key == "scan_dim":
            _val = np.random.randint(1, 5)
        elif _key == "scan_multi_frame_handling":
            _val = np.random.choice(["Average", "Sum", "Maximum"])
        else:
            _val = np.round(0.5 + 5 * np.random.rand(), decimals=5)
        scan.set_param_value(_key, _val)


@pytest.fixture
def create_hdf5_file(temp_dir) -> Path:
    """Fixture to create a temporary HDF5 h5file."""
    hdf5_filename = temp_dir / "scan_io_hdf5.h5"
    with h5py.File(hdf5_filename, "a") as h5file:
        nxs_export_context(h5file, SCAN, "entry/pydidas_scan")
    return hdf5_filename


def read_hdf5_file(file_path: Path) -> dict[str, Any]:
    """Read the HDF5 h5file and return the data as a dictionary."""
    with h5py.File(file_path, "r") as h5file:
        data = {}
        group = h5file["entry/pydidas_scan"]
        for key in group.keys():
            data[key] = read_and_decode_hdf5_dataset(group[key])
    return data


def test_export_to_file__correct(modify_scan_context, temp_dir):
    """Test the export_to_file method."""
    hdf5_file = temp_dir / "scan_io_hdf5.h5"
    SCAN_IO_HDF5.export_to_file(hdf5_file)
    with h5py.File(hdf5_file, "r") as h5file:
        _group = h5file["entry/pydidas_scan"]
        for _key, _param in SCAN.params.items():
            assert (
                read_and_decode_hdf5_dataset(_group[_key]) == modify_scan_context[_key]
            )
        assert "entry/instrument/detector/frame_start_number" in h5file
        assert h5file["entry/instrument"].attrs.get("NX_class") == "NXinstrument"
        assert h5file["entry/instrument/detector"].attrs.get("NX_class") == "NXdetector"


def test_export_to_file__w_scan(temp_dir):
    """Test the export_to_file method with a custom Scan."""
    _local_scan = Scan()
    _randomize_scan(_local_scan)
    hdf5_file = temp_dir / "local_scan_io_hdf5.h5"
    SCAN_IO_HDF5.export_to_file(hdf5_file, scan=_local_scan)
    with h5py.File(hdf5_file, "r") as h5file:
        _group = h5file["entry/pydidas_scan"]
        for _key, _param in SCAN.params.items():
            assert (
                read_and_decode_hdf5_dataset(_group[_key])
                == _local_scan.params[_key].value_for_export
            )


def test_import_from_file__empty_file(temp_dir):
    _fname = temp_dir / "empty_file.h5"
    with h5py.File(_fname, "w") as h5file:
        nxs_create_recursive_groups(
            h5file, "entry/pydidas_scan", group_type="NXcollection"
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
    _local_scan = Scan()
    SCAN_IO_HDF5.import_from_file(create_hdf5_file, scan=_local_scan)
    for _key, _param in _local_scan.params.items():
        assert SCAN.params[_key].value_for_export == modify_scan_context[_key]


@pytest.mark.parametrize(
    "fname",
    [
        "load_test_scan_context_legacy_v250616.h5",
        "load_test_scan_context_legacy_v251028.h5",
        "load_test_scan_context_legacy_v260519.h5",
    ],
)
def test_import_from_file__from_exported_legacy_file(fname):
    _fname = _TEST_DIR / "_data" / fname
    _prefix = "/entry/pydidas_config/scan/"
    with h5py.File(_fname, "r") as h5file:
        _keys = [
            _key.removeprefix(_prefix)
            for _key in get_hdf5_populated_dataset_keys(
                h5file[_prefix], min_dim=0, min_size=0
            )
        ]
        _imported_values = {
            _key: read_and_decode_hdf5_dataset(h5file[f"{_prefix}{_key}"])
            for _key in _keys
        }
    SCAN_IO_HDF5.import_from_file(_fname)
    for _key, _val in _imported_values.items():
        _scan_key = SCAN_LEGACY_PARAMS[_key] if _key in SCAN_LEGACY_PARAMS else _key
        if _scan_key == "xray_energy":
            continue
        assert _val == SCAN.params[_scan_key].value_for_export


def test_import_from_file__other_key(temp_dir):
    _fname = temp_dir / "test_other_key.h5"
    with h5py.File(_fname, "a") as h5file:
        nxs_export_context(h5file, SCAN, "entry/other/custom_scan")
    with pytest.raises(UserConfigError):
        SCAN_IO_HDF5.import_from_file(_fname)


def test_import_from_file__no_file(temp_dir):
    with pytest.raises(UserConfigError):
        SCAN_IO_HDF5.import_from_file(temp_dir / "test_42_random.h5")


def test__export_matches_template(modify_scan_context, temp_path):
    _ref_filename = temp_path / "test_export_template.hdf5"
    _filename = temp_path / "test_export.hdf5"
    create_hdf5_results_file(
        _ref_filename, _TEST_DATA, SCAN, DiffractionExperiment(), ProcessingTree()
    )
    SCAN_IO_HDF5.export_to_file(_filename)
    with h5py.File(_filename, "r") as _h5file:
        _keys = _h5file.keys()
        _exported_data = {_key: _h5file[_key] for _key in _keys}
        _exported_attrs = {
            _key: {_k: _v for _k, _v in _h5file[_key].attrs.items()} for _key in _keys
        }
    with h5py.File(_ref_filename, "r") as _h5file:
        _keys = _h5file.keys()
        _ref_data = {_key: _h5file[_key] for _key in _keys}
        _ref_attrs = {
            _key: {_k: _v for _k, _v in _h5file[_key].attrs.items()} for _key in _keys
        }
    for _key, _val in _exported_data.items():
        if isinstance(_val, np.ndarray):
            assert np.allclose(_val, _ref_data[_key])
        else:
            assert _val == _ref_data[_key]
        for _attr_key, _attr_val in _exported_attrs[_key].items():
            assert _attr_val == _ref_attrs[_key][_attr_key]


if __name__ == "__main__":
    pytest.main()

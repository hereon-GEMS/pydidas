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


import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any

import h5py
import numpy as np
import pytest

from pydidas.contexts import DiffractionExperimentContext, Scan
from pydidas.contexts.diff_exp import DiffractionExperiment
from pydidas.contexts.diff_exp.diff_exp_io_hdf5 import DiffractionExperimentIoHdf5
from pydidas.core import UserConfigError
from pydidas.core.utils import get_random_string
from pydidas.core.utils.hdf5 import (
    nxs_create_recursive_groups,
    read_and_decode_hdf5_dataset,
)
from pydidas.core.utils.hdf5.nxs_export import (
    nxs_export_context,
    nxs_write_root_metadata,
)
from pydidas.unittest_objects import create_hdf5_results_file
from pydidas.unittest_objects.create_dataset_ import create_dataset
from pydidas.workflow import ProcessingTree


EXP = DiffractionExperimentContext()
EXP_IO_HDF5 = DiffractionExperimentIoHdf5
_LEGACY_FILES = list((Path(__file__).parents[2] / "_data" / "NeXus").iterdir())
_TEST_DATA = create_dataset(3)


@pytest.fixture(scope="module")
def temp_dir() -> Generator[Path, Any, Any]:
    """Fixture to create a temporary directory."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def modify_diffraction_exp_context(temp_dir) -> Generator[dict[str, Any], Any, Any]:
    """Fixture to modify the DiffractionExperimentContext."""
    _randomize_diffraction_exp(EXP, temp_dir)
    yield {_key: _param.value_for_export for _key, _param in EXP.params.items()}
    EXP.restore_all_defaults(True)


def _randomize_diffraction_exp(exp: DiffractionExperiment, local_dir: Path):
    for _key in exp.params:
        if _key in ["detector_npixx", "detector_npixy"]:
            _val = int(1000 * np.random.rand()) + 5
        elif _key in ["detector_mask_file"]:
            _val = local_dir / "mask.tif"
        elif _key in ["detector_name"]:
            _val = get_random_string(6)
        else:
            _val = np.round(0.5 + 5 * np.random.rand(), decimals=5)
        exp.set_param_value(_key, _val)


@pytest.fixture
def hdf5_io_file(temp_dir) -> Path:
    """Fixture to create a temporary HDF5 file."""
    hdf5_filename = temp_dir / "diffraction_exp_io_hdf5.h5"
    with h5py.File(hdf5_filename, "w") as h5file:
        nxs_export_context(h5file, EXP, "entry/pydidas_diffraction_exp")
    return hdf5_filename


def test_export_to_file__correct(modify_diffraction_exp_context, temp_dir):
    """Test the export_to_file method."""
    hdf5_file = temp_dir / "diffraction_exp_io_hdf5.h5"
    EXP_IO_HDF5.export_to_file(hdf5_file)
    with h5py.File(hdf5_file, "r") as file:
        _group = file["entry/pydidas_diffraction_exp"]
        for _key in EXP.params:
            assert (
                read_and_decode_hdf5_dataset(_group[_key])
                == modify_diffraction_exp_context[_key]
            )


def test_export_to_file__w_diffraction_exp(temp_dir):
    """Test the export_to_file method with a custom DiffractionExperiment."""
    _local_exp = DiffractionExperiment()
    _randomize_diffraction_exp(_local_exp, temp_dir)
    hdf5_file = temp_dir / "local_diffraction_exp_io_hdf5.h5"
    EXP_IO_HDF5.export_to_file(hdf5_file, diffraction_exp=_local_exp)
    with h5py.File(hdf5_file, "r") as file:
        _group = file["entry/pydidas_diffraction_exp"]
        for _key in EXP.params:
            assert read_and_decode_hdf5_dataset(_group[_key]) == pytest.approx(
                _local_exp.params[_key].value_for_export
            )


def test_import_from_file__empty_file(temp_dir):
    _fname = temp_dir / "empty_file.h5"
    with h5py.File(_fname, "w") as file:
        nxs_create_recursive_groups(
            file, "entry/pydidas_diffraction_exp", group_type="NXcollection"
        )
    with pytest.raises(UserConfigError):
        EXP_IO_HDF5.import_from_file(_fname)


def test_import_from_file(modify_diffraction_exp_context, hdf5_io_file):
    EXP_IO_HDF5.import_from_file(hdf5_io_file)
    _imported_values = EXP.get_param_values_as_dict(filter_types_for_export=True)
    for _key, _value in _imported_values.items():
        assert pytest.approx(_value) == modify_diffraction_exp_context[_key]


@pytest.mark.parametrize("filename", _LEGACY_FILES)
def test_import_from_file__w_legacy_files(filename, modify_diffraction_exp_context):
    EXP_IO_HDF5.import_from_file(filename)
    _imported_values = EXP.get_param_values_as_dict(filter_types_for_export=True)
    for _key, _value in _imported_values.items():
        # just verify that data was loaded and the random data overwritten
        assert modify_diffraction_exp_context[_key] != _value


def test_import_from_file__to_local_context(
    modify_diffraction_exp_context, hdf5_io_file
):
    _local_exp = DiffractionExperiment()
    EXP_IO_HDF5.import_from_file(hdf5_io_file, diffraction_exp=_local_exp)
    for _key, _param in _local_exp.params.items():
        assert _param.value_for_export == pytest.approx(
            modify_diffraction_exp_context[_key]
        )


def test_import_from_file__w_illegal_location(modify_diffraction_exp_context, temp_dir):
    _filename = temp_dir / "incompatible_diffraction_exp_io_hdf5.h5"
    with h5py.File(_filename, "w") as h5file:
        nxs_write_root_metadata(h5file)
    with pytest.raises(UserConfigError):
        EXP_IO_HDF5.import_from_file(_filename)


def test__export_matches_template(modify_diffraction_exp_context, temp_path):
    _ref_filename = temp_path / "test_export_template.hdf5"
    _filename = temp_path / "test_export.hdf5"
    create_hdf5_results_file(_ref_filename, _TEST_DATA, Scan(), EXP, ProcessingTree())
    EXP_IO_HDF5.export_to_file(_filename)
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
    pytest.main([__file__])

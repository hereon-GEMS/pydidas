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

from pydidas.contexts import DiffractionExperimentContext
from pydidas.contexts.diff_exp import DiffractionExperiment
from pydidas.contexts.diff_exp.diff_exp_io_hdf5 import DiffractionExperimentIoHdf5
from pydidas.core import UserConfigError
from pydidas.core.utils import create_nx_entry_groups, get_random_string
from pydidas.core.utils.hdf5_dataset_utils import (
    export_context_to_hdf5,
    read_and_decode_hdf5_dataset,
)


EXP = DiffractionExperimentContext()
EXP_IO_HDF5 = DiffractionExperimentIoHdf5


@pytest.fixture(scope="module")
def temp_dir() -> Path:
    """Fixture to create a temporary directory."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def modify_diffraction_exp_context(temp_dir) -> dict[str, Any]:
    """Fixture to modify the DiffractionExperimentContext."""
    _randomize_diffraction_exp(EXP, temp_dir)
    yield {_key: _param.value_for_export for _key, _param in EXP.params.items()}
    EXP.restore_all_defaults(True)


def _randomize_diffraction_exp(exp: DiffractionExperiment, local_dir: Path):
    for _key, _param in exp.params.items():
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
def create_hdf5_file(temp_dir) -> Path:
    """Fixture to create a temporary HDF5 file."""
    hdf5_filename = temp_dir / "diffraction_exp_io_hdf5.h5"
    export_context_to_hdf5(hdf5_filename, EXP, "entry/pydidas_config/diffraction_exp")
    return hdf5_filename


def test_export_to_file__correct(modify_diffraction_exp_context, temp_dir):
    """Test the export_to_file method."""
    hdf5_file = temp_dir / "diffraction_exp_io_hdf5.h5"
    EXP_IO_HDF5.export_to_file(hdf5_file)
    with h5py.File(hdf5_file, "r") as file:
        _group = file["entry/pydidas_config/diffraction_exp"]
        for _key, _param in EXP.params.items():
            assert (
                read_and_decode_hdf5_dataset(_group[_key])
                == modify_diffraction_exp_context[_key]
            )


def test_export_to_file__w_diffraction_exp(temp_dir):
    """Test the export_to_file method with a custom DiffractionExperiment."""
    local_EXP = DiffractionExperiment()
    _randomize_diffraction_exp(local_EXP, temp_dir)
    hdf5_file = temp_dir / "local_diffraction_exp_io_hdf5.h5"
    EXP_IO_HDF5.export_to_file(hdf5_file, diffraction_exp=local_EXP)
    with h5py.File(hdf5_file, "r") as file:
        _group = file["entry/pydidas_config/diffraction_exp"]
        for _key, _param in EXP.params.items():
            assert (
                read_and_decode_hdf5_dataset(_group[_key])
                == local_EXP.params[_key].value_for_export
            )


def test_import_from_file__empty_file(temp_dir):
    _fname = temp_dir / "empty_file.h5"
    with h5py.File(_fname, "w") as file:
        create_nx_entry_groups(
            file, "entry/pydidas_config/diffraction_exp", group_type="NXcollection"
        )
    with pytest.raises(UserConfigError):
        EXP_IO_HDF5.import_from_file(_fname)


def test_import_from_file(temp_dir, modify_diffraction_exp_context, create_hdf5_file):
    """Test the import_from_file method."""
    EXP_IO_HDF5.import_from_file(create_hdf5_file)
    for _key, _param in EXP.params.items():
        assert EXP.params[_key].value_for_export == modify_diffraction_exp_context[_key]


def test_import_from_file__to_local_context(
    temp_dir, modify_diffraction_exp_context, create_hdf5_file
):
    """Test the import_from_file method."""
    local_EXP = DiffractionExperiment()
    EXP_IO_HDF5.import_from_file(create_hdf5_file, diffraction_exp=local_EXP)
    for _key, _param in local_EXP.params.items():
        assert EXP.params[_key].value_for_export == modify_diffraction_exp_context[_key]


if __name__ == "__main__":
    pytest.main()

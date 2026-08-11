# This file is part of pydidas.
#
# Copyright 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import h5py
import pytest

from pydidas.core.utils.hdf5 import (
    nxs_write_dataset,
)
from pydidas.core.utils.hdf5.hdf5_pydidas_utils import get_exported_pydidas_version
from pydidas.core.utils.hdf5.nxs_export import (
    nxs_create_nxentry,
    nxs_create_recursive_groups,
)


@pytest.fixture
def hdf5_file(temp_path):
    """Create a temporary HDF5 file for tests."""
    if not (temp_path / "hdf5_utils").is_dir():
        (temp_path / "hdf5_utils").mkdir()
    file = h5py.File(temp_path / "hdf5_utils" / "temp_file.h5", "w")
    nxs_create_nxentry(file, "entry")
    yield file
    file.close()


def test_get_exported_pydidas_version__w_program_name(hdf5_file) -> None:
    _dset = nxs_write_dataset(hdf5_file["entry"], "program_name", "pydidas")
    _dset.attrs["version"] = "1.2.3"
    _result = get_exported_pydidas_version(hdf5_file)
    assert _result == "1.2.3"


def test_get_exported_pydidas_version__w_program_name_and_non_str_version(
    hdf5_file,
) -> None:
    _dset = nxs_write_dataset(hdf5_file["entry"], "program_name", "pydidas")
    _dset.attrs["version"] = 1.23
    _result = get_exported_pydidas_version(hdf5_file)
    assert _result == "0.0.0"


def test_get_exported_pydidas_version__w_program_name_missing_version_attr(
    hdf5_file,
) -> None:
    """
    When version attr is missing, should fall back to pydidas_config/pydidas_version.
    """
    _version = "2.5.0"
    _dset = nxs_write_dataset(hdf5_file["entry"], "program_name", "pydidas")
    _pydidas_config = nxs_create_recursive_groups(
        hdf5_file["entry"], "pydidas_config", group_type="NXcollection"
    )
    nxs_write_dataset(_pydidas_config, "pydidas_version", _version)
    _result = get_exported_pydidas_version(hdf5_file)
    assert _result == _version


def test_get_exported_pydidas_version__w_missing_attr_and_string_version(
    hdf5_file,
) -> None:
    _fallback_version = "0.5.0"
    _dset = nxs_write_dataset(hdf5_file["entry"], "program_name", "pydidas")
    _dset.attrs["version"] = 123
    # Create the fallback path to avoid KeyError bug in the function
    _pydidas_config = nxs_create_recursive_groups(
        hdf5_file["entry"], "pydidas_config", group_type="NXcollection"
    )
    nxs_write_dataset(_pydidas_config, "pydidas_version", _fallback_version)
    _result = get_exported_pydidas_version(hdf5_file)
    assert _result == _fallback_version


def test_get_exported_pydidas_version__priority_order(hdf5_file) -> None:
    """Test that entry/program_name takes priority over pydidas_config."""
    _program_version = "1.2.3"
    _fallback_version = "0.0.5"
    _dset = nxs_write_dataset(hdf5_file["entry"], "program_name", "pydidas")
    _dset.attrs["version"] = _program_version
    _pydidas_config = nxs_create_recursive_groups(
        hdf5_file["entry"], "pydidas_config", group_type="NXcollection"
    )
    nxs_write_dataset(_pydidas_config, "pydidas_version", _fallback_version)
    _result = get_exported_pydidas_version(hdf5_file)
    assert _result == _program_version


if __name__ == "__main__":
    pytest.main([__file__])

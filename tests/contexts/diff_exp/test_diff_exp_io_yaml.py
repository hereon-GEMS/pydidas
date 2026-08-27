# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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

"""Unit tests for DiffractionExperimentIoYaml."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"

import shutil
from pathlib import Path

import numpy as np
import pytest  # pyright: ignore[reportMissingImports]
import yaml  # pyright: ignore[reportMissingModuleSource]

from pydidas.contexts import DiffractionExperimentContext
from pydidas.contexts.diff_exp import DiffractionExperiment
from pydidas.contexts.diff_exp.diff_exp_io_yaml import DiffractionExperimentIoYaml
from pydidas.core import UserConfigError


EXP = DiffractionExperimentContext()
EXP_IO_YAML = DiffractionExperimentIoYaml


@pytest.fixture
def test_yaml_path() -> str:
    _test_dir = Path(__file__).parents[2]
    return str(_test_dir / "_data" / "load_test_diffraction_exp_context_")


def test_import_from_file__correct(test_yaml_path):
    EXP_IO_YAML.import_from_file(test_yaml_path + "yaml.yml")
    with open(test_yaml_path + "yaml.yml", "r") as _file:
        _data = yaml.safe_load(_file)
    for key in [
        "dist",
        "poni1",
        "poni2",
        "rot1",
        "rot2",
        "rot3",
    ]:
        _full_key = f"detector_{key}"
        assert EXP.get_param_value(_full_key) == _data[_full_key]


def test_import_from_file__w_diffraction_exp(test_yaml_path):
    _exp = DiffractionExperiment()
    EXP_IO_YAML.import_from_file(test_yaml_path + "yaml.yml", diffraction_exp=_exp)
    with open(test_yaml_path + "yaml.yml", "r") as _file:
        _data = yaml.safe_load(_file)
    for key in [
        "dist",
        "poni1",
        "poni2",
        "rot1",
        "rot2",
        "rot3",
    ]:
        _full_key = f"detector_{key}"
        assert _exp.get_param_value(_full_key) == _data[_full_key]


def test_import_from_file__missing_keys(temp_path):
    """Test importing from a YAML file with missing required keys."""
    with open(temp_path / "yaml.yml", "w") as _file:
        _file.write("no_entry: True")
    with pytest.raises(UserConfigError):
        EXP_IO_YAML.import_from_file(temp_path / "yaml.yml")


def test_import_from_file__wrong_format(temp_path):
    with open(temp_path / "yaml.yml", "w") as _file:
        _file.write("{no_entry=True; test=True}")
    with pytest.raises(UserConfigError):
        EXP_IO_YAML.import_from_file(temp_path / "yaml.yml")


def test_import_from_file__binary_data(temp_path):
    _fname = temp_path / "npy_binary_data.yml"
    np.save(_fname.with_suffix(".npy"), np.ones(5))
    shutil.move(_fname.with_suffix(".npy"), _fname)
    with pytest.raises(UserConfigError):
        EXP_IO_YAML.import_from_file(_fname)


def test_export_to_file(temp_path):
    _fname = temp_path / "yaml_export.yml"
    EXP_IO_YAML.export_to_file(_fname)
    with open(_fname, "r") as _file:
        _data = yaml.safe_load(_file)
    for _key, _param in EXP.params.items():
        if _key == "xray_energy":
            continue
        assert _data[_key] == pytest.approx(_param.value_for_export)


if __name__ == "__main__":
    pytest.main([__file__])

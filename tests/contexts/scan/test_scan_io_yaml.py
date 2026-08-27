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

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from pathlib import Path

import numpy as np
import pytest
import yaml

from pydidas.contexts import ScanContext
from pydidas.contexts.scan import Scan
from pydidas.contexts.scan.scan_io_yaml import ScanIoYaml
from pydidas.core import UserConfigError


@pytest.fixture
def test_path():
    """Return the path to the test data directory."""
    return Path(__file__).parents[2] / "_data"


@pytest.fixture
def test_yaml_file(test_path):
    """Return the path to the test YAML file."""
    return test_path / "load_test_scan_context.yml"


@pytest.fixture
def scan_context():
    """Return a fresh ScanContext instance."""
    return ScanContext()


@pytest.fixture
def scan_io_yaml():
    """Return the ScanIoYaml class."""
    return ScanIoYaml


def test_import_from_file__correct(scan_io_yaml, test_yaml_file, scan_context):
    scan_io_yaml.import_from_file(test_yaml_file)
    with open(test_yaml_file, "r") as stream:
        _data = yaml.safe_load(stream)
    for key in scan_context.params:
        assert scan_context.get_param(key).value_for_export == _data[key]


def test_import_from_file__w_legacy_keys(scan_io_yaml, test_path, scan_context):
    scan_io_yaml.import_from_file(test_path / "load_test_scan_context_legacy.yml")
    with open(test_path / "load_test_scan_context.yml", "r") as stream:
        _data = yaml.safe_load(stream)
    for key in scan_context.params:
        assert scan_context.get_param(key).value_for_export == _data[key]


def test_import_from_file__given_scan(scan_io_yaml, test_yaml_file, scan_context):
    _scan = Scan()
    scan_io_yaml.import_from_file(test_yaml_file, scan=_scan)
    with open(test_yaml_file, "r") as stream:
        _data = yaml.safe_load(stream)
    for key in scan_context.params:
        assert _scan.get_param(key).value_for_export == _data[key]


def test_import_from_file__missing_keys(scan_io_yaml, tmp_path):
    _fname = tmp_path / "yaml_missing_key.yml"
    with open(_fname, "w") as stream:
        stream.write("no_entry: True")
    with pytest.raises(UserConfigError):
        scan_io_yaml.import_from_file(_fname)


def test_import_from_file__wrong_format(scan_io_yaml, tmp_path):
    _fname = tmp_path / "yaml_wrong_format.yml"
    with open(_fname, "w") as stream:
        stream.write("no_entry =True")
    with pytest.raises(UserConfigError):
        scan_io_yaml.import_from_file(_fname)


def test_import_from_file__legacy_format(scan_io_yaml, test_path, scan_context):
    _scan = Scan()
    scan_io_yaml.import_from_file(
        test_path / "load_test_scan_context_legacy.yml", scan=_scan
    )
    _scan2 = Scan()
    scan_io_yaml.import_from_file(test_path / "load_test_scan_context.yml", scan=_scan2)
    for key in scan_context.params:
        if key != "xray_energy":
            assert _scan.get_param_value(key) == _scan2.get_param_value(key)


def test_import_from_file__yaml_error(scan_io_yaml, tmp_path):
    _fname = tmp_path / "yaml_error.yml"
    np.save(_fname, np.array([1, 2, 3]))  # Save a numpy array instead of YAML
    # remove the suffix to simulate a binary file with YAML extension
    _fname_npy = tmp_path / "yaml_error.yml.npy"
    _fname_npy.rename(_fname)
    with pytest.raises(yaml.YAMLError):
        scan_io_yaml.import_from_file(_fname)


def test_export_to_file(scan_io_yaml, tmp_path, scan_context):
    _fname = tmp_path / "yaml_export.yml"
    scan_io_yaml.export_to_file(_fname)
    with open(_fname, "r") as stream:
        _data = yaml.safe_load(stream)
    for key in scan_context.params:
        if key != "xray_energy":
            assert scan_context.get_param(key).value_for_export == _data[key]

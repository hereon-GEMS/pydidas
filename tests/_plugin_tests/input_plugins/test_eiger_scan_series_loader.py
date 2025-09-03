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
from pathlib import Path

import pytest
from qtpy import QtCore

from pydidas.contexts import ScanContext
from pydidas.core import FileReadError
from pydidas.plugins import BasePlugin
from pydidas.unittest_objects import LocalPluginCollection


COLLECTION = LocalPluginCollection()

SCAN = ScanContext()


@pytest.fixture(scope="module")
def config():
    yield
    # necessary due to use of 'LocalPluginCollection':
    qs = QtCore.QSettings("Hereon", "pydidas")
    qs.remove("unittesting")


@pytest.fixture
def plugin(config):
    SCAN.restore_all_defaults(True)
    return COLLECTION.get_plugin_by_name("EigerScanSeriesLoader")()


def test_creation():
    plugin = COLLECTION.get_plugin_by_name("EigerScanSeriesLoader")()
    assert isinstance(plugin, BasePlugin)


def test_pre_execute__no_input():
    plugin = COLLECTION.get_plugin_by_name("EigerScanSeriesLoader")()
    with pytest.raises(FileReadError):
        plugin.pre_execute()


@pytest.mark.parametrize("eiger_dir", ["eiger9m", "eiger10m"])
@pytest.mark.parametrize("eiger_filename_suffix", ["_data_000001.h5", "_scan42.hdf5"])
@pytest.mark.parametrize(
    "scan_name_pattern", ["test_scan", "test_###_a1", "###_scan", "test_#####"]
)
def test_update_filename_string(
    plugin, eiger_dir, eiger_filename_suffix, scan_name_pattern
):
    plugin.set_param_value("eiger_dir", eiger_dir)
    plugin.set_param_value("eiger_filename_suffix", eiger_filename_suffix)
    SCAN.set_param_value("scan_name_pattern", scan_name_pattern)
    _proc_pattern = SCAN.processed_file_naming_pattern
    plugin.update_filename_string()
    assert plugin.filename_string == f".{os.sep}" + str(
        Path() / _proc_pattern / eiger_dir / f"{_proc_pattern}{eiger_filename_suffix}"
    )


def test_update_filename_string__w_suffix_in_name(plugin):
    _eiger_dir = "eiger4x"
    _eiger_filename_suffix = "_data_007.h5"
    plugin.set_param_value("eiger_dir", _eiger_dir)
    plugin.set_param_value("eiger_filename_suffix", _eiger_filename_suffix)
    SCAN.set_param_value("scan_name_pattern", "test_###_a1" + _eiger_filename_suffix)
    _proc_pattern = SCAN.processed_file_naming_pattern
    plugin.update_filename_string()
    assert plugin.filename_string == os.sep.join(
        [".", "test_{index:03d}_a1", "eiger4x", "test_{index:03d}_a1_data_007.h5"]
    )


if __name__ == "__main__":
    pytest.main()

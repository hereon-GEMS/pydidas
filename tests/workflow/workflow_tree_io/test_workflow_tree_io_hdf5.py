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
from pathlib import Path

import h5py
import pytest

import pydidas
from pydidas.core import UserConfigError
from pydidas.core.utils.hdf5 import read_and_decode_hdf5_dataset
from pydidas.workflow import ProcessingTree, WorkflowTree
from pydidas.workflow.processing_tree_io.processing_tree_io_hdf5 import (
    ProcessingTreeIoHdf5,
)


PLUGIN_COLL = pydidas.plugins.PluginCollection()


@pytest.fixture(scope="module")
def temp_dir() -> Path:
    """Fixture to create a temporary directory."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_tree() -> ProcessingTree:
    """Fixture to create a test ProcessingTree."""
    _pluginclass = PLUGIN_COLL.get_plugin_by_name("PyFAIazimuthalIntegration")
    _plugin = _pluginclass()
    _tree = WorkflowTree()
    _tree.clear()
    _tree.create_and_add_node(_plugin)
    _tree.create_and_add_node(_plugin)
    _tree.create_and_add_node(_plugin, parent=_tree.nodes[0])
    return _tree


def export_to_file(filename: Path | str, tree: ProcessingTree):
    with h5py.File(filename, "a") as _file:
        _entry = _file.create_group("entry")
        _config = _entry.create_group("pydidas_config")
        _config.create_dataset("workflow", data=tree.export_to_string())
        _config.create_dataset("pydidas_version", data=pydidas.VERSION)


def test_export_to_file(temp_dir, test_tree):
    _filename = temp_dir / "test_export.hdf5"
    ProcessingTreeIoHdf5.export_to_file(_filename, test_tree, overwrite=True)
    with h5py.File(_filename, "r") as f:
        _tree_repr = read_and_decode_hdf5_dataset(f["entry/pydidas_config/workflow"])
        _version = read_and_decode_hdf5_dataset(
            f["entry/pydidas_config/pydidas_version"]
        )
    assert _tree_repr == test_tree.export_to_string()
    assert _version == pydidas.VERSION


def test_import_from_file__w_version(temp_dir, test_tree):
    _filename = temp_dir / "test_import.hdf5"
    export_to_file(_filename, test_tree)
    _new = ProcessingTreeIoHdf5.import_from_file(_filename)
    assert set(_new.nodes) == set(test_tree.nodes)
    for _id, _node in _new.nodes.items():
        assert set(_node.plugin.params) == set(test_tree.nodes[_id].plugin.params)


def test_import_from_file__w_version_and_error(temp_dir):
    _filename = temp_dir / "test_incorrect_import.hdf5"
    with h5py.File(_filename, "w") as _f:
        _f["entry/pydidas_config/workflow"] = "1234"
    with pytest.raises(UserConfigError):
        ProcessingTreeIoHdf5.import_from_file(_filename)


def test_import_from_file__old_version_no_error(temp_dir, test_tree):
    _filename = temp_dir / "test_old_version_import.hdf5"
    export_to_file(_filename, test_tree)
    with h5py.File(_filename, "a") as _f:
        _f["entry/pydidas_config/pydidas_verion"] = "0.0.0"
    _new = ProcessingTreeIoHdf5.import_from_file(_filename)
    assert set(_new.nodes) == set(test_tree.nodes)
    for _id, _node in _new.nodes.items():
        assert set(_node.plugin.params) == set(test_tree.nodes[_id].plugin.params)


def test_import_from_file__old_version_w_error(temp_dir):
    _filename = temp_dir / "test_old_version_import.hdf5"
    with h5py.File(_filename, "w") as _f:
        _f["entry/pydidas_config/pydidas_verion"] = "0.0.0"
        _f["entry/pydidas_config/workflow"] = "1234"
    with pytest.raises(UserConfigError):
        ProcessingTreeIoHdf5.import_from_file(_filename)


if __name__ == "__main__":
    pytest.main()

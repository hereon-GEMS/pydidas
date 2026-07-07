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


from pathlib import Path

import h5py
import numpy as np
import pytest

import pydidas
from pydidas.contexts import Scan
from pydidas.contexts.diff_exp.diff_exp import DiffractionExperiment
from pydidas.core import UserConfigError
from pydidas.core.utils.hdf5 import read_and_decode_hdf5_dataset
from pydidas.unittest_objects.create_dataset_ import create_dataset
from pydidas.unittest_objects.create_hdf5_io_file_ import create_hdf5_results_file
from pydidas.workflow import ProcessingTree
from pydidas.workflow.processing_tree_io.processing_tree_io_hdf5 import (
    ProcessingTreeIoHdf5,
)


PLUGIN_COLL = pydidas.plugins.PluginCollection()
_LEGACY_DIR = Path(__file__).parents[2] / "_data" / "NeXus"
_TEST_DATA = create_dataset(3)


def test_export_to_file(temp_path, test_tree):
    _filename = temp_path / "test_export.hdf5"
    ProcessingTreeIoHdf5.export_to_file(_filename, test_tree, overwrite=True)
    _n_tree = len(test_tree.nodes)
    with h5py.File(_filename, "r") as _h5file:
        assert "/entry/pydidas_workflow/workflow_info/nodes" in _h5file
        assert _h5file["/entry/pydidas_workflow/workflow_info/num_nodes"][()] == _n_tree
        for _i in range(_n_tree):
            _group = _h5file[f"/entry/pydidas_workflow/workflow_node_{_i:02d}"]
            _node = test_tree.nodes[_i]
            assert read_and_decode_hdf5_dataset(_group["node_id"]) == _node.node_id
            assert read_and_decode_hdf5_dataset(_group["parent"]) == (
                _node.parent.node_id if _node.parent else None
            )
            assert np.allclose(
                read_and_decode_hdf5_dataset(_group["children"]),
                [child.node_id for child in _node.children],
            )
            assert (
                read_and_decode_hdf5_dataset(_group["plugin_class"])
                == _node.plugin.__class__.__name__
            )
            for _key, _param in _node.plugin.params.items():
                if _key.startswith("_"):
                    assert _key not in _group
                else:
                    _ref = _param.value_for_export
                    _val = read_and_decode_hdf5_dataset(_group[_key])
                    if isinstance(_ref, (np.ndarray, list, tuple)):
                        assert np.array_equal(_val, _ref)
                    else:
                        assert _param.value_for_export == _val


def test_export_to_file__existing_entry(temp_path, test_tree):
    _filename = temp_path / "test_export.hdf5"
    ProcessingTreeIoHdf5.export_to_file(_filename, test_tree, overwrite=True)
    _tree = ProcessingTree()
    ProcessingTreeIoHdf5.export_to_file(_filename, _tree, overwrite=True)
    with h5py.File(_filename, "r") as _h5file:
        assert "/entry/pydidas_workflow/workflow_info/nodes" in _h5file
        assert _h5file["/entry/pydidas_workflow/workflow_info/num_nodes"][()] == 0
        _workflow_group = _h5file["/entry/pydidas_workflow"]
        for _i in range(5):
            assert f"workflow_node_{_i:02d}" not in _workflow_group


@pytest.mark.parametrize(
    "filename", ["legacy_file_v240118.h5", "legacy_file_v260519.h5"]
)
def test_import_from_file__w_legacy_data(filename):
    _filename = _LEGACY_DIR / filename
    _new = ProcessingTreeIoHdf5.import_from_file(_filename)
    assert isinstance(_new, ProcessingTree)


def test_import_from_file__w_legacy_version_and_error(temp_path):
    _filename = temp_path / "test_incorrect_legacy_import.hdf5"
    with h5py.File(_filename, "w") as _f:
        _f["entry/pydidas_config/workflow"] = "1234"
    with pytest.raises(UserConfigError):
        ProcessingTreeIoHdf5.import_from_file(_filename)


@pytest.mark.parametrize("version", ["a.b.c", 0.0, 42, "0.1.2"])
def test_import_from_file__w_version_and_error(temp_path, version):
    _filename = temp_path / "test_incorrect_import.hdf5"
    with h5py.File(_filename, "w") as _f:
        _f["entry/program_name"] = "pydidas"
        _f["entry/program_name"].attrs["version"] = version
    with pytest.raises(UserConfigError):
        ProcessingTreeIoHdf5.import_from_file(_filename)


def test_import_from_file(temp_path, test_tree):
    _filename = temp_path / "test_version_import.hdf5"
    test_tree.export_to_file(_filename)
    _new_tree = ProcessingTreeIoHdf5.import_from_file(_filename)
    for _id, _node in _new_tree.nodes.items():
        assert test_tree.nodes[_id].dump() == _node.dump()


def test__export_matches_template(temp_path, test_tree):
    _ref_filename = temp_path / "test_export_template.hdf5"
    _filename = temp_path / "test_export.hdf5"
    create_hdf5_results_file(
        _ref_filename, _TEST_DATA, Scan(), DiffractionExperiment(), test_tree
    )
    ProcessingTreeIoHdf5.export_to_file(_filename, test_tree)
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

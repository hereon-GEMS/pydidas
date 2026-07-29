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

import h5py
import numpy as np
import pytest

from tests.workflow.processing_result_io.test_processing_result_io_base import (
    SharedTestProcessingResultIo,
)

from pydidas.contexts.diff_exp.diff_exp import DiffractionExperiment
from pydidas.contexts.scan.scan import Scan
from pydidas.core.constants.file_extensions import HDF5_EXTENSIONS
from pydidas.core.exceptions import FileReadError
from pydidas.core.utils.hdf5.hdf5_dataset_utils import read_and_decode_hdf5_dataset
from pydidas.core.utils.iterable_utils import replace_item_in_iterable
from pydidas.plugins.plugin_result_info import PluginResultInfo
from pydidas.unittest_objects.create_dataset_ import create_dataset
from pydidas.workflow.processing_tree import ProcessingTree
from pydidas.workflow.result_io import ProcessingResultIoMeta
from pydidas.workflow.result_io.processing_result_io_hdf5 import ProcessingResultIoHdf5


META = ProcessingResultIoMeta
H5SAVER = ProcessingResultIoHdf5
_TEST_FILES = list((Path(__file__).parents[2] / "_data" / "NeXus").iterdir())


@pytest.fixture
def saver():
    return H5SAVER()


@pytest.fixture
def prepared_saver(
    node_info,
    random_scan,
    random_diff_exp,
    test_tree,
    empty_temp_path,
):
    saver = H5SAVER()
    saver.prepare_files_and_directories(
        empty_temp_path,
        node_info,
        scan=random_scan,
        diffraction_exp=random_diff_exp,
        processing_tree=test_tree,
    )
    return saver


@pytest.fixture
def node_info(random_scan):
    return {
        0: PluginResultInfo(
            label="",
            node_id=0,
            shape=random_scan.shape + (10, 20),
            plugin_name="InputTest",
        ),
        1: PluginResultInfo(
            label="result_node",
            node_id=1,
            shape=random_scan.shape + (10,),
            plugin_name="Proc_Dummy",
        ),
    }


class TestProcessingResultIoHdf5Generic(SharedTestProcessingResultIo): ...


@pytest.mark.parametrize("key", H5SAVER.extensions + [H5SAVER.format_name])
def test__metaclass_findability(key):
    _savers = META.get_savers(key)
    assert len(_savers) == 1
    _instance = list(_savers.values())[0]
    assert isinstance(_instance, H5SAVER)


def test__class_attributes():
    for _ext in HDF5_EXTENSIONS:
        assert _ext in H5SAVER.extensions
    assert H5SAVER.format_name == "HDF5"
    assert H5SAVER.default_suffix == ".nxs"


def test_init():
    _saver = H5SAVER()
    assert isinstance(_saver, H5SAVER)
    assert _saver._config["metadata_written"] is False


@pytest.mark.slow
def test_prepare_files_and_directories(
    saver,
    node_info,
    random_scan,
    random_diff_exp,
    test_tree,
    empty_temp_path,
):
    saver.prepare_files_and_directories(
        empty_temp_path,
        node_info,
        scan=random_scan,
        diffraction_exp=random_diff_exp,
        processing_tree=test_tree,
    )
    assert saver._config["metadata_written"] is False
    for _id, _name in [(0, "node_00.nxs"), (1, "node_01_result_node.nxs")]:
        assert (empty_temp_path / _name).is_file()
        with h5py.File(empty_temp_path / _name, "r") as _h5file:
            assert _id == read_and_decode_hdf5_dataset(
                _h5file["entry/node_info/node_id"]
            )
            assert node_info[_id].label == read_and_decode_hdf5_dataset(
                _h5file["entry/node_info/node_label"]
            )
            assert node_info[_id].plugin_name == read_and_decode_hdf5_dataset(
                _h5file["entry/node_info/plugin_name"]
            )
            assert "entry/data" in _h5file
            assert "entry/pydidas_scan" in _h5file
            assert "entry/pydidas_diffraction_exp" in _h5file
            assert "entry/pydidas_workflow" in _h5file


@pytest.mark.slow
@pytest.mark.parametrize("squeeze", [True, False])
def test_export_full_data_to_file(
    saver, node_info, empty_temp_path, random_scan, random_diff_exp, test_tree, squeeze
):
    if squeeze:
        random_scan.set_param_value("scan_dim1_n_points", 1)
        for _id, _node_info in node_info.items():
            _node_info.shape = replace_item_in_iterable(_node_info.shape, 1, 1)  # type: ignore[arg-type]
    saver.prepare_files_and_directories(
        empty_temp_path,
        node_info,
        scan=random_scan,
        diffraction_exp=random_diff_exp,
        processing_tree=test_tree,
    )
    _results = {
        _id: create_dataset(len(_info.shape), shape=_info.shape)
        for _id, _info in node_info.items()
    }
    saver.export_full_data_to_file(_results, squeeze=squeeze)
    assert saver._config.get("metadata_written", False) is True
    for _id in node_info.keys():
        _name = saver.get_filenames(node_info)[_id]
        _data_ref = _results[_id].squeeze() if squeeze else _results[_id]
        assert (empty_temp_path / _name).is_file()
        with h5py.File(empty_temp_path / _name, "r") as _h5file:
            for _key in ["title", "signal", "axes"]:
                assert _key in _h5file["entry/data"].attrs
            _data = read_and_decode_hdf5_dataset(_h5file["entry/data/data"])
            assert _data.shape == _data_ref.shape
            assert np.allclose(_data, _data_ref)
            _squeeze_str = "1" if squeeze else ""
            assert _squeeze_str == read_and_decode_hdf5_dataset(
                _h5file["entry/node_info/squeezed_scan_dims"]
            )


@pytest.mark.slow
def test_export_full_data_to_file__verify_duplicate_call_does_not_raise(
    saver, node_info, empty_temp_path, random_scan, random_diff_exp, test_tree
):
    saver.prepare_files_and_directories(
        empty_temp_path,
        node_info,
        scan=random_scan,
        diffraction_exp=random_diff_exp,
        processing_tree=test_tree,
    )
    _results = {
        _id: create_dataset(len(_info.shape), shape=_info.shape)
        for _id, _info in node_info.items()
    }
    saver.export_full_data_to_file(_results)
    _callback = saver.export_full_data_to_file(_results)
    assert _callback is None


@pytest.mark.parametrize("use_dict", [True, False])
def test_create_result_nxdata_entry(
    prepared_saver,
    node_info,
    empty_temp_path,
    use_dict,
):
    _metadata = {
        _id: create_dataset(len(_info.shape), shape=_info.shape)
        for _id, _info in node_info.items()
    }
    _ranges = {_id: _val.axis_ranges for _id, _val in _metadata.items()}
    if use_dict:
        _metadata = {_id: _val.property_dict for _id, _val in _metadata.items()}
    prepared_saver.create_result_nxdata_entry(_metadata)
    for _id in node_info.keys():
        _name = prepared_saver.get_filenames(node_info)[_id]
        assert (empty_temp_path / _name).is_file()
        with h5py.File(empty_temp_path / _name, "r") as _h5file:
            for _key in ["title", "signal", "axes"]:
                assert _key in _h5file["entry/data"].attrs
            _data = read_and_decode_hdf5_dataset(_h5file["entry/data/data"])
            for _dim, _ax in _ranges[_id].items():
                _data = read_and_decode_hdf5_dataset(_h5file[f"entry/data/axis_{_dim}"])
                assert np.allclose(_data, _ax)


@pytest.mark.slow
@pytest.mark.parametrize("index", [1, 4, 42])
def test_export_frame_to_file(
    prepared_saver, random_scan, node_info, empty_temp_path, index
):
    _indices = random_scan.get_indices_from_ordinal(index)
    _indices_m1 = random_scan.get_indices_from_ordinal(index - 1)
    _indices_p1 = random_scan.get_indices_from_ordinal(index + 1)
    _frame_results = {
        0: create_dataset(2, shape=(10, 20)),
        1: create_dataset(1, shape=(10,)),
    }
    prepared_saver.export_frame_to_file(index, _frame_results)
    prepared_saver.export_frame_to_file(index + 1, _frame_results)
    for _id in _frame_results.keys():
        _name = prepared_saver.get_filenames(node_info)[_id]
        with h5py.File(empty_temp_path / _name, "r") as _h5file:
            _no_data = _h5file["entry/data/data"][_indices_m1]
            _data = _h5file["entry/data/data"][_indices]
            _data2 = _h5file["entry/data/data"][_indices_p1]
            assert np.allclose(_data, _frame_results[_id])


@pytest.mark.parametrize("filename", _TEST_FILES)
def test_import_results_from_file(saver, filename):
    _data, _node_info, _scan, _exp, _tree = saver.import_results_from_file(filename)
    assert isinstance(_data, np.ndarray)
    assert isinstance(_node_info, dict)
    assert isinstance(_scan, Scan)
    assert isinstance(_exp, DiffractionExperiment)
    assert isinstance(_tree, ProcessingTree)


def test_import_results_from_file__empty_file(saver, temp_path):
    _fname = temp_path / "empty_file.nxs"
    _fname.write_text("")
    with pytest.raises(FileReadError):
        saver.import_results_from_file(_fname)


if __name__ == "__main__":
    pytest.main([__file__])

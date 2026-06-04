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


import random
import shutil
from numbers import Integral, Real
from pathlib import Path

import h5py
import numpy as np
import pytest

from pydidas.contexts import (
    DiffractionExperimentContext,
    Scan,
    ScanContext,
)
from pydidas.core import Dataset, UserConfigError
from pydidas.core.utils import get_random_string
from pydidas.core.utils.hdf5 import read_and_decode_hdf5_dataset
from pydidas.unittest_objects import create_hdf5_results_file
from pydidas.unittest_objects.create_dataset_ import create_dataset
from pydidas.workflow import ProcessingResults, WorkflowTree
from pydidas.workflow.result_io import ProcessingResultIoMeta
from pydidas.workflow.result_io.processing_result_io_hdf5 import ProcessingResultIoHdf5


TREE = WorkflowTree()
SCAN = ScanContext()
EXP = DiffractionExperimentContext()
RESULTS = ProcessingResults()
META = ProcessingResultIoMeta
H5SAVER = ProcessingResultIoHdf5


def _make_scan_with_size1_dims(n_dim: int, *size_1_dims: int) -> Scan:
    _scan = Scan()
    _default_shape = (3, 7, 5, 11)
    _units = ("mm", "deg", "um", "rad")
    _offsets = (0.5, -2, 11, 4.2)
    _deltas = (0.1, -0.2, 0.4, 0.75)
    _scan.set_param_value("scan_dim", n_dim)
    for _dim in range(n_dim):
        _scan.set_param_value(f"scan_dim{_dim}_label", f"motor{_dim}")
        _size = 1 if _dim in size_1_dims else _default_shape[_dim]
        _scan.set_param_value(f"scan_dim{_dim}_n_points", _size)
        _scan.set_param_value(f"scan_dim{_dim}_delta", _deltas[_dim])
        _scan.set_param_value(f"scan_dim{_dim}_offset", _offsets[_dim])
        _scan.set_param_value(f"scan_dim{_dim}_unit", _units[_dim])
    return _scan


@pytest.fixture(scope="module")
def setup_module_data(temp_path):
    """
    Module-level fixture to set up test data.

    This fixture:
    1. Initializes SCAN and EXP contexts with random parameters
    2. Creates test files for import tests
    """
    SCAN.restore_all_defaults(confirm=True)
    SCAN.set_param_value("scan_dim", 3)
    for d in range(4):
        SCAN.set_param_value(f"scan_dim{d}_n_points", random.choice([3, 5, 7, 8]))
        SCAN.set_param_value(f"scan_dim{d}_delta", random.choice([0.1, 0.5, 1, 1.5]))
        SCAN.set_param_value(f"scan_dim{d}_offset", random.choice([-0.1, 0.5, 1]))
        SCAN.set_param_value(f"scan_dim{d}_label", get_random_string(12))
        SCAN.set_param_value(f"scan_dim{d}_unit", get_random_string(3))

    for _key in EXP.params:
        if EXP.params[_key].dtype == Integral:
            EXP.set_param_value(_key, int(100 * np.random.random()))
        elif EXP.params[_key].dtype == Real:
            EXP.set_param_value(_key, np.random.random())
        elif EXP.params[_key].dtype == str:
            EXP.set_param_value(_key, get_random_string(12))

    # Create basic import test file
    import_test_filename = temp_path / "import_test.h5"
    data = Dataset(
        np.random.random((9, 9, 27)),
        data_label=get_random_string(12),
        data_unit=get_random_string(3),
        axis_labels={0: "None", 1: None, 2: "Label"},
        axis_units={0: "u1", 1: "u2", 2: None},
        axis_ranges={
            0: np.arange(9),
            1: np.arange(9) - 3,
            2: np.linspace(12, -5, num=27),
        },
    )
    io_node_label = get_random_string(9)
    import_plugin_name = get_random_string(8)
    create_hdf5_results_file(
        import_test_filename,
        data,
        SCAN.get_param_values_as_dict(filter_types_for_export=True),
        EXP.get_param_values_as_dict(filter_types_for_export=True),
        TREE,
        node_label=io_node_label,
        plugin_name=import_plugin_name,
    )

    # Create squeezed test files
    data_shape = (5, 7)
    mismatched_data_shape = (2, 3, 4, 5)
    scan = _make_scan_with_size1_dims(3, 1)
    squeezed_data = create_dataset(5, shape=scan.shape + data_shape).squeeze()
    mismatched_data = create_dataset(4, shape=mismatched_data_shape)

    scan_dict = scan.get_param_values_as_dict(filter_types_for_export=True)
    exp_dict = EXP.get_param_values_as_dict(filter_types_for_export=True)

    import_squeezed_filename = temp_path / "import_test_squeezed.h5"
    import_squeezed_empty_filename = temp_path / "import_test_squeezed_empty.h5"
    import_legacy_squeezed_filename = temp_path / "import_test_legacy_squeezed.h5"
    import_legacy_no_match_filename = temp_path / "import_test_legacy_no_match.h5"

    for _name, _dset, _extra_kwargs in [
        (import_squeezed_filename, squeezed_data, {"squeezed_scan_dims": "1"}),
        (import_squeezed_empty_filename, squeezed_data, {}),
        (import_legacy_squeezed_filename, squeezed_data, {}),
        (import_legacy_no_match_filename, mismatched_data, {}),
    ]:
        create_hdf5_results_file(
            _name,
            _dset,
            scan_dict,
            exp_dict,
            TREE,
            node_label="Label",
            plugin_name="SomePlugin",
            **_extra_kwargs,
        )

    with h5py.File(import_legacy_squeezed_filename, "r+") as _file:
        del _file["entry/pydidas_config/squeezed_scan_dims"]
    with h5py.File(import_legacy_no_match_filename, "r+") as _file:
        del _file["entry/pydidas_config/squeezed_scan_dims"]

    yield {
        "import_test_filename": import_test_filename,
        "io_node_label": io_node_label,
        "import_plugin_name": import_plugin_name,
        "data": data,
        "data_shape": data_shape,
        "mismatched_data_shape": mismatched_data_shape,
        "squeezed_import_data": squeezed_data,
        "import_squeezed_filename": import_squeezed_filename,
        "import_squeezed_empty_filename": import_squeezed_empty_filename,
        "import_legacy_squeezed_filename": import_legacy_squeezed_filename,
        "import_legacy_no_match_filename": import_legacy_no_match_filename,
    }


@pytest.fixture
def default_shapes(setup_module_data):
    """Fixture providing default shapes and related test data."""
    shapes = {
        1: SCAN.shape + (12, 7),
        2: SCAN.shape + (23,),
        3: SCAN.shape + (1, 3, 7),
    }
    labels = {1: "Test", 2: "not again", 3: "another"}
    _data_labels = {1: "Intensity", 2: "Peak height", 3: "Area"}
    _data_units = {1: "a.u.", 2: "km", 3: "square inch"}
    plugin_names = {1: "A plugin", 2: "Plugin no 2.", 3: "Ye olde plugin"}
    filenames = {
        1: "node_01_Test.nxs",
        2: "node_02_not_again.nxs",
        3: "node_03_another.nxs",
    }

    return {
        "shapes": shapes,
        "labels": labels,
        "data_labels": _data_labels,
        "data_units": _data_units,
        "plugin_names": plugin_names,
        "filenames": filenames,
    }


@pytest.fixture
def setup_test_files(empty_temp_path, default_shapes):
    """Fixture to set up test files and directories for each test."""
    _node_infos = {
        _node: {
            "node_label": default_shapes["labels"][_node],
            "data_label": default_shapes["data_labels"][_node],
            "data_unit": default_shapes["data_units"][_node],
            "shape": default_shapes["shapes"][_node],
            "plugin_name": default_shapes["plugin_names"][_node],
        }
        for _node in default_shapes["shapes"].keys()
    }
    H5SAVER.prepare_files_and_directories(empty_temp_path, _node_infos)

    yield {
        "result_dir": empty_temp_path,
        "shapes": default_shapes["shapes"],
        "labels": default_shapes["labels"],
        "data_labels": default_shapes["data_labels"],
        "data_units": default_shapes["data_units"],
        "filenames": default_shapes["filenames"],
    }


def get_datasets(shapes, start_dim=3):
    """Helper function to create datasets with specified shapes."""
    return {
        _key: create_dataset(len(_shape[start_dim:]), shape=_shape[start_dim:])
        for _key, _shape in shapes.items()
    }


def assert_written_files_are_okay(_result_dir, data, metadata, filenames, shapes):
    """Helper function to assert that written HDF5 files are correct."""
    for _node_id in shapes:
        _fname = _result_dir / filenames[_node_id]
        with h5py.File(_fname, "r") as _file:
            assert (
                _file["entry/data"].attrs["title"] == metadata[_node_id]["data_label"]
            )
            assert (
                _file["entry/data/data"].attrs["units"]
                == metadata[_node_id]["data_unit"]
            )
            for _ax in range(3, data[_node_id].ndim):
                _ax_entry = _file[f"entry/data/axis_{_ax}"]
                assert (
                    read_and_decode_hdf5_dataset(_ax_entry["label"])
                    == metadata[_node_id]["axis_labels"][_ax - 3]
                )
                assert (
                    read_and_decode_hdf5_dataset(_ax_entry["unit"])
                    == metadata[_node_id]["axis_units"][_ax - 3]
                )
                assert np.array_equal(
                    read_and_decode_hdf5_dataset(_ax_entry["range"]),
                    metadata[_node_id]["axis_ranges"][_ax - 3],
                )


def test_class():
    assert H5SAVER.__class__ == META


def test_prepare_files_and_directories(setup_test_files):
    _result_dir: Path = setup_test_files["result_dir"]  # type: ignore[type] # type: ignore[type]
    shapes = setup_test_files["shapes"]
    labels = setup_test_files["labels"]
    filenames = setup_test_files["filenames"]
    assert _result_dir.exists()
    # prepare_files_and_directories was called in the ``setup_test_files`` fixture
    assert H5SAVER.get_attribute_dict("shape") == shapes
    assert H5SAVER.get_attribute_dict("node_label") == labels
    for _key in shapes:
        _fname = H5SAVER._filenames[_key]
        assert _fname == filenames[_key]
        assert (_result_dir / _fname).exists()


def test_create_file_and_populate_metadata(setup_test_files):
    _result_dir: Path = setup_test_files["result_dir"]  # type: ignore[type]
    shapes = setup_test_files["shapes"]
    filenames = setup_test_files["filenames"]
    _node_id = 1
    H5SAVER._create_file_and_populate_metadata(_node_id, SCAN, EXP, TREE)
    with h5py.File(_result_dir / filenames[1], "r") as _file:
        _data = _file["entry/data/data"]
        assert _data.shape == shapes[1]
        assert isinstance(_data, h5py.Dataset)


def test_update_with_scan_metadata(setup_test_files):
    shapes = setup_test_files["shapes"]

    _datasets = get_datasets(shapes)
    _metadata = H5SAVER.update_with_scan_metadata(_datasets, SCAN)
    for _key, _metadata_item in _metadata.items():
        assert _metadata_item["data_label"] == _datasets[_key].data_label
        assert _metadata_item["data_unit"] == _datasets[_key].data_unit
        for _dim in range(SCAN.ndim):
            assert _metadata_item["axis_labels"][_dim] == SCAN.axis_labels[_dim]
            assert _metadata_item["axis_units"][_dim] == SCAN.axis_units[_dim]
            assert np.allclose(
                _metadata_item["axis_ranges"][_dim], SCAN.axis_ranges[_dim]
            )
        for _dim in range(_datasets[_key].ndim - SCAN.ndim):
            assert (
                _metadata_item["axis_labels"][_dim + SCAN.ndim]
                == _datasets[_key].axis_labels[_dim]
            )
            assert (
                _metadata_item["axis_units"][_dim + SCAN.ndim]
                == _datasets[_key].axis_units[_dim]
            )
            assert np.allclose(
                _metadata_item["axis_ranges"][_dim + SCAN.ndim],
                _datasets[_key].axis_ranges[_dim],
            )


def test_update_metadata__standard(setup_test_files):
    _result_dir: Path = setup_test_files["result_dir"]  # type: ignore[type]
    shapes = setup_test_files["shapes"]
    filenames = setup_test_files["filenames"]

    _data = {
        _key: create_dataset(len(_shape[3:]), shape=_shape[3:])
        for _key, _shape in shapes.items()
    }
    _metadata = {
        _key: dict(
            axis_units=_item.axis_units,
            axis_labels=_item.axis_labels,
            axis_ranges=_item.axis_ranges,
            data_label=_data[_key].data_label,
            data_unit=_data[_key].data_unit,
        )
        for _key, _item in _data.items()
    }
    H5SAVER.update_metadata(_metadata)
    assert_written_files_are_okay(_result_dir, _data, _metadata, filenames, shapes)


def test_export_full_data_to_file(setup_test_files):
    _result_dir: Path = setup_test_files["result_dir"]  # type: ignore[type]
    shapes = setup_test_files["shapes"]
    filenames = setup_test_files["filenames"]

    _data = get_datasets(shapes, start_dim=0)
    H5SAVER.export_full_data_to_file(_data, SCAN)
    for _node_id in shapes:
        _fname = _result_dir / filenames[_node_id]
        with h5py.File(_fname, "r") as _file:
            _written_data = _file["entry/data/data"][()]
        assert np.allclose(_data[_node_id], _written_data)


def test_export_full_data_to_file__same_dataset(setup_test_files):
    _result_dir: Path = setup_test_files["result_dir"]  # type: ignore[type]
    shapes = setup_test_files["shapes"]
    filenames = setup_test_files["filenames"]

    _data = get_datasets(shapes, start_dim=1)
    H5SAVER.export_full_data_to_file(_data, SCAN)
    _data = get_datasets(shapes, start_dim=0)
    H5SAVER.export_full_data_to_file(_data)
    for _node_id in shapes:
        _fname = _result_dir / filenames[_node_id]
        with h5py.File(_fname, "r") as _file:
            _written_data = _file["entry/data/data"][()]
        assert np.allclose(_data[_node_id], _written_data)


def test_export_frame_to_file(setup_test_files):
    _result_dir: Path = setup_test_files["result_dir"]  # type: ignore[type]
    shapes = setup_test_files["shapes"]
    filenames = setup_test_files["filenames"]

    _data = get_datasets(shapes)
    _index = 5
    _scan_indices = SCAN.get_indices_from_ordinal(_index)
    H5SAVER.export_frame_to_file(_index, _data, SCAN)
    for _node_id in shapes:
        _fname = _result_dir / filenames[_node_id]
        with h5py.File(_fname, "r") as _file:
            _written_data = _file["entry/data/data"][_scan_indices]
        assert np.allclose(_written_data, _data[_node_id].array)


def test_import_results_from_file(setup_module_data):
    _fname: Path = setup_module_data["import_test_filename"]  # type: ignore[type]
    _data, _node_info, _scan, _exp, _tree = H5SAVER.import_results_from_file(_fname)
    _input_data: Dataset = setup_module_data["data"]  # type: ignore[type]
    assert _node_info["node_label"] == setup_module_data["io_node_label"]
    assert _data.data_label == _input_data.data_label
    for _ax in range(_data.ndim):
        assert _input_data.axis_labels[_ax] == _data.axis_labels[_ax]
        assert _input_data.axis_units[_ax] == _data.axis_units[_ax]
        if isinstance(_input_data.axis_ranges[_ax], np.ndarray):
            assert np.allclose(
                _input_data.axis_ranges[_ax],
                _data.axis_ranges[_ax],
            )
        else:
            assert _input_data.axis_ranges[_ax] == _data.axis_ranges[_ax]
    for _key, _param in EXP.params.items():
        if _param.dtype == Real:
            assert abs(_param.value - _exp.get_param_value(_key)) < 1e-7
        else:
            assert _param.value == _exp.get_param_value(_key)
    for _key, _param in SCAN.params.items():
        if _param.dtype == Real:
            assert abs(_param.value - _scan.get_param_value(_key)) < 1e-7
        else:
            assert _param.value == _scan.get_param_value(_key)


def test_import_results_from_file__with_missing_data(
    setup_module_data, empty_temp_path
):
    _fname: Path = setup_module_data["import_test_filename"]  # type: ignore[type]
    _new_name = empty_temp_path / "import_test_with_None.h5"
    shutil.copy(_fname, _new_name)
    with h5py.File(_new_name, "r+") as _file:
        del _file["entry/pydidas_config/scan/scan_dim0_n_points"]
        del _file["entry/pydidas_config/scan/scan_dim0_unit"]
        del _file["entry/pydidas_config/scan/scan_dim0_label"]
    with pytest.raises(UserConfigError):
        _data, _node_info, _scan, _exp, _tree = H5SAVER.import_results_from_file(
            _new_name
        )


def test_insert_squeezed_scan_dims__single_dim(setup_module_data):
    data_shape = setup_module_data["data_shape"]
    _scan = _make_scan_with_size1_dims(3, 1)
    _data = Dataset(
        np.random.random(_scan.squeezed_shape + data_shape),
        axis_labels={
            0: _scan.axis_labels[0],
            1: _scan.axis_labels[2],
            2: "data_label0",
            3: "data_label1",
        },
        axis_units={
            0: _scan.axis_units[0],
            1: _scan.axis_units[2],
            2: "data_unit",
            3: "data_unit B",
        },
        axis_ranges={
            0: _scan.axis_ranges[0],
            1: _scan.axis_ranges[2],
            2: np.linspace(11, 12, data_shape[0]),  # type: ignore[type]
            3: np.linspace(0, 2, data_shape[1]),  # type: ignore[type]
        },
    )
    _result = H5SAVER._insert_squeezed_scan_dims(_data, _scan, [1])
    assert _result.shape == _scan.shape + data_shape
    for _dim in [0, 1, 2]:
        assert _result.axis_labels[_dim] == _scan.get_param_value(
            f"scan_dim{_dim}_label"
        )
        assert _result.axis_units[_dim] == _scan.get_param_value(f"scan_dim{_dim}_unit")
    assert np.allclose(_result.squeeze(), _data)


def test_insert_squeezed_scan_dims__multiple_dims():
    _scan = _make_scan_with_size1_dims(3, 0, 2)
    _data_shape = (12,)
    _data = Dataset(
        np.random.random(_scan.squeezed_shape + _data_shape),
        axis_labels={0: "motor1_ax", 1: "intensity"},
        axis_units={0: "deg", 1: "a.u."},
        axis_ranges={
            0: np.linspace(0, 0.4, _scan.shape[1]),
            1: np.arange(_data_shape[0], dtype=float),
        },
    )
    _result = H5SAVER._insert_squeezed_scan_dims(_data, _scan, [0, 2])
    assert _result.shape == _scan.shape + _data_shape
    assert _result.axis_labels[0] == _scan.axis_labels[0]
    assert _result.axis_labels[1] == _data.axis_labels[0]
    assert _result.axis_labels[2] == _scan.axis_labels[2]
    assert _result.axis_labels[3] == _data.axis_labels[1]
    assert np.allclose(_result.squeeze(), _data)


def test_update_metadata__with_squeeze(empty_temp_path):
    _scan = _make_scan_with_size1_dims(3, 1)
    _plugin_shape = (12, 7)
    _full_shape = _scan.shape + _plugin_shape
    _node_infos = {
        1: {
            "node_label": "SqueezedNode",
            "data_label": "Intensity",
            "data_unit": "a.u.",
            "shape": _plugin_shape,
            "plugin_name": "SomeProcPlugin",
        }
    }
    H5SAVER.prepare_files_and_directories(
        empty_temp_path, _node_infos, scan_context=_scan
    )
    _data = Dataset(
        np.random.random(_full_shape),
        axis_labels={i: f"ax{i}" for i in range(len(_full_shape))},
        axis_units={i: f"u{i}" for i in range(len(_full_shape))},
        axis_ranges={
            i: np.arange(_full_shape[i], dtype=float) for i in range(len(_full_shape))
        },
    )
    H5SAVER.update_metadata({1: _data}, scan=_scan, squeeze=True)
    _fname = empty_temp_path / H5SAVER._filenames[1]
    with h5py.File(_fname, "r") as _file:
        _squeeze_str = read_and_decode_hdf5_dataset(
            _file["entry/pydidas_config/squeezed_scan_dims"]
        )
        _squeezed_dims = [int(_i) for _i in _squeeze_str.split(";")]
    assert _squeezed_dims == [1]


def test_export_full_data_to_file__with_squeeze(empty_temp_path):
    _scan = _make_scan_with_size1_dims(3, 1)
    _plugin_shape = (12, 7)
    _full_shape = _scan.shape + _plugin_shape
    _squeezed_shape = _scan.squeezed_shape + _plugin_shape
    _node_infos = {
        1: {
            "node_label": "SqueezedNode",
            "data_label": "Intensity",
            "data_unit": "a.u.",
            "shape": _squeezed_shape,
            "plugin_name": "SomeProcPlugin",
        }
    }
    H5SAVER.prepare_files_and_directories(
        empty_temp_path, _node_infos, scan_context=_scan
    )
    _full_data = {1: Dataset(np.random.random(_full_shape))}
    H5SAVER.export_full_data_to_file(_full_data, scan_context=_scan, squeeze=True)
    with h5py.File(empty_temp_path / H5SAVER._filenames[1], "r") as _file:
        _written = _file["entry/data/data"][()]
        _squeeze_str = read_and_decode_hdf5_dataset(
            _file["entry/pydidas_config/squeezed_scan_dims"]
        )
    assert _written.shape == _squeezed_shape
    assert np.allclose(_written, _full_data[1].squeeze().array)
    assert _squeeze_str == "1"


def test_import_results_from_file__with_squeezed_dims_flag(setup_module_data):
    """Test to check that data was re-inserted for squeezed dim"""
    _fname: Path = setup_module_data["import_squeezed_filename"]  # type: ignore[type]
    _import_data: Dataset = setup_module_data["squeezed_import_data"]  # type: ignore[type]
    _data, _info, _scan, _exp, _tree = H5SAVER.import_results_from_file(_fname)
    data_shape = setup_module_data["data_shape"]
    assert _data.shape == _scan.shape + data_shape
    assert _data.axis_labels[1] == _scan.axis_labels[1]
    assert _data.axis_units[1] == _scan.axis_units[1]
    assert _data.axis_labels[0] == _import_data.axis_labels[0]


def test_import_results_from_file__with_empty_squeezed_dims_flag(setup_module_data):
    """Test to check that no data was re-inserted for squeezed dim"""
    _fname: Path = setup_module_data["import_squeezed_empty_filename"]  # type: ignore[type]
    _data, _info, _scan, _exp, _tree = H5SAVER.import_results_from_file(_fname)
    data_shape = setup_module_data["data_shape"]
    _expected_shape = _scan.squeezed_shape + data_shape
    assert _data.shape == _expected_shape


def test_import_results_from_file__legacy_squeezed_dims(setup_module_data):
    """Test to check that data was re-inserted if key is missing"""
    _fname: Path = setup_module_data["import_legacy_squeezed_filename"]  # type: ignore[type]
    _data, _info, _scan, _exp, _tree = H5SAVER.import_results_from_file(_fname)
    data_shape = setup_module_data["data_shape"]
    assert _data.shape == _scan.shape + data_shape
    assert _data.axis_labels[1] == _scan.axis_labels[1]
    assert _data.axis_units[1] == _scan.axis_units[1]


def test_import_results_from_file__legacy_size1_dims_shape_no_match(setup_module_data):
    """Without key and shape mismatch, data should stay the same"""
    _fname: Path = setup_module_data["import_legacy_no_match_filename"]  # type: ignore[type]
    _data, _info, _scan, _exp, _tree = H5SAVER.import_results_from_file(_fname)
    assert _data.shape == setup_module_data["mismatched_data_shape"]


if __name__ == "__main__":
    pytest.main()

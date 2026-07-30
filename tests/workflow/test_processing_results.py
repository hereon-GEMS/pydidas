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

"""Unit tests for the ProcessingResults workflow class."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import os
import re
from numbers import Real
from pathlib import Path
from typing import Any

import h5py
import numpy as np
import pytest

from pydidas import unittest_objects  # noqa: F401
from pydidas.contexts import DiffractionExperiment
from pydidas.contexts.scan import Scan, ScanContext
from pydidas.core import Dataset, UserConfigError
from pydidas.core.utils import get_random_string
from pydidas.plugins import PluginCollection
from pydidas.unittest_objects import (
    DummyLoader,
    DummyProc,
    DummyProcNewDataset,
    create_dataset,
    create_hdf5_results_file,
)
from pydidas.workflow import (
    ProcessingResults,
    ProcessingTree,
)


_INPUT_SHAPE = (127, 324)
_NEW_SHAPE = (12, 3, 1, 5)
_DEFAULT_PLUGIN_METADATA = {
    1: {
        "axis_units": {0: "m", 1: "mm"},
        "axis_labels": {0: "dim1", 1: "dim 2"},
        "axis_ranges": {
            0: np.arange(_INPUT_SHAPE[0]),
            1: np.arange(_INPUT_SHAPE[1])[::-1],
        },
        "data_label": "Test",
        "data_unit": "u1",
    },
    2: {
        "axis_units": {0: "m", 1: "Test", 2: "", 3: "spam!"},
        "axis_labels": {0: "dim1", 1: "2nd dim", 2: "dim #3", 3: "42"},
        "axis_ranges": {
            0: 12 + np.arange(_NEW_SHAPE[0]),
            1: np.arange(_NEW_SHAPE[1]),
            2: np.array([42]),
            3: 4 + 0.5 * np.arange(_NEW_SHAPE[3]),
        },
        "data_label": "New dataset",
        "data_unit": "u2",
    },
}


@pytest.fixture(scope="module", autouse=True)
def verify_plugin_collection_valid() -> None:
    """Verify that the plugin collection is loaded."""
    _unittest_obj_dir = (
        Path(__file__).parents[2] / "src" / "pydidas" / "unittest_objects"
    )
    _collection = PluginCollection()
    _collection.verify_is_initialized()
    _collection.find_and_register_plugins(_unittest_obj_dir)


@pytest.fixture
def tree() -> ProcessingTree:
    tree = ProcessingTree()
    tree.create_and_add_node(DummyLoader())
    tree.nodes[0].plugin.set_param_value("image_height", _INPUT_SHAPE[0])
    tree.nodes[0].plugin.set_param_value("image_width", _INPUT_SHAPE[1])
    _proc1 = DummyProc()
    _proc1.set_param_value("label", "Test plugin 1")
    _proc2 = DummyProcNewDataset(output_shape=_NEW_SHAPE)
    _proc2.set_param_value("label", "Test plugin 2")
    tree.create_and_add_node(_proc1)
    tree.create_and_add_node(_proc2, parent=tree.root)
    tree.prepare_execution()
    return tree


@pytest.fixture
def clean_results(random_scan, random_diff_exp, tree) -> ProcessingResults:
    _res = ProcessingResults(
        scan=random_scan, processing_tree=tree, diffraction_exp=random_diff_exp
    )
    return _res


@pytest.fixture
def results(clean_results) -> ProcessingResults:
    clean_results.prepare_new_results()
    clean_results.update_result_metadata(_DEFAULT_PLUGIN_METADATA)
    return clean_results


@pytest.fixture
def result_data() -> dict[int, Dataset]:
    _res1 = Dataset(np.random.random(_INPUT_SHAPE), **_DEFAULT_PLUGIN_METADATA[1])
    _res2 = Dataset(np.random.random(_NEW_SHAPE), **_DEFAULT_PLUGIN_METADATA[2])
    _results = {1: _res1, 2: _res2}
    return _results


def _create_metadata_with_scan(plugin_metadata, scan) -> dict[int, dict[str, Any]]:
    _scan_meta = {
        "axis_ranges": scan.axis_ranges,
        "axis_labels": scan.axis_labels,
        "axis_units": scan.axis_units,
    }
    _new_metadata = {}
    for _node_id, _meta in plugin_metadata.items():
        _node_metadata = _new_metadata[_node_id] = {}
        for _key in ["axis_labels", "axis_units", "axis_ranges"]:
            _items = _scan_meta[_key] + list(_meta[_key].values())
            _node_metadata[_key] = {_i: _k for _i, _k in enumerate(_items)}
        _node_metadata["data_unit"] = _meta["data_unit"]
        _node_metadata["data_label"] = _meta["data_label"]
    return _new_metadata


def _get_node_output_filename(node_id: int, tree: ProcessingTree) -> str:
    _label = tree.nodes[node_id].plugin.get_param_value("label")
    if _label:
        _label = re.sub("[^a-zA-Z0-9_-]", "_", _label)
        _label = re.sub("_+", "_", _label.strip("_"))
        return f"node_{node_id:02d}_{_label}.nxs"
    return f"node_{node_id:02d}.nxs"


def _get_node_output_path(node_id: int, tree: ProcessingTree, tmpdir: Path) -> Path:
    return tmpdir / _get_node_output_filename(node_id, tree)


def _create_h5_test_file(
    node_id: int,
    res: ProcessingResults,
    tmpdir: Path,
    tree: ProcessingTree,
    scan: Scan,
    diff_exp: DiffractionExperiment,
) -> None:
    _path = _get_node_output_path(node_id, tree, tmpdir)
    create_hdf5_results_file(
        _path,
        res._composites[node_id],
        scan,
        diff_exp,
        tree,
        node_id=node_id,
        node_label=tree.nodes[node_id].plugin.get_param_value("label"),
        plugin_name=tree.nodes[node_id].plugin.plugin_name,
    )


def _get_node_labels(res: ProcessingResults) -> dict[int, str]:
    return {_key: _info.label for _key, _info in res._plugin_result_infos.items()}


def _get_data_labels(res: ProcessingResults) -> dict[int, str]:
    return {_key: _data.data_label for _key, _data in res._composites.items()}


def _get_data_units(res: ProcessingResults) -> dict[int, str]:
    return {_key: _data.data_unit for _key, _data in res._composites.items()}


def test_init__plain() -> None:
    res = ProcessingResults()
    assert isinstance(res, ProcessingResults)
    assert isinstance(res.scan_instance, Scan)
    assert isinstance(res.diff_exp_instance, DiffractionExperiment)
    assert isinstance(res.proc_tree_instance, ProcessingTree)


def test_init__w_contexts() -> None:
    _local_scan = Scan()
    _local_exp = DiffractionExperiment()
    _local_tree = ProcessingTree()
    res = ProcessingResults(
        scan=_local_scan,
        diffraction_exp=_local_exp,
        processing_tree=_local_tree,
    )
    assert id(_local_scan) == id(res.scan_instance)
    assert id(_local_exp) == id(res.diff_exp_instance)
    assert id(_local_tree) == id(res.proc_tree_instance)


# --------------------
# Tests of properties
# --------------------


def test_scan_instance(random_scan, clean_results) -> None:
    assert isinstance(clean_results.scan_instance, Scan)
    assert id(random_scan) == id(clean_results.scan_instance)


def test_diff_exp_instance(random_diff_exp, clean_results) -> None:
    assert isinstance(clean_results.diff_exp_instance, DiffractionExperiment)
    assert id(random_diff_exp) == id(clean_results.diff_exp_instance)


def test_proc_tree_instance(tree, clean_results) -> None:
    assert isinstance(clean_results.proc_tree_instance, ProcessingTree)
    assert id(tree) == id(clean_results.proc_tree_instance)


def test_shapes__empty(clean_results) -> None:
    assert clean_results.shapes == {}


def test_shapes__w_results(results) -> None:
    _shapes = results.shapes
    assert isinstance(_shapes, dict)
    assert all(isinstance(_key, int) for _key in _shapes.keys())
    assert all(isinstance(_value, tuple) for _value in _shapes.values())


def test_ndims__empty(clean_results) -> None:
    assert clean_results.ndims == {}


def test_ndims__w_results(results) -> None:
    _ndims = results.ndims
    assert isinstance(_ndims, dict)
    assert all(isinstance(_key, int) for _key in _ndims.keys())
    assert all(isinstance(_value, int) for _value in _ndims.values())


def test_frozen_tree(clean_results) -> None:
    clean_results.prepare_new_results()
    assert isinstance(clean_results.frozen_tree, ProcessingTree)
    assert id(clean_results.frozen_tree) != id(clean_results.proc_tree_instance)


def test_frozen_exp(clean_results) -> None:
    clean_results.prepare_new_results()
    assert isinstance(clean_results.frozen_exp, DiffractionExperiment)
    assert id(clean_results.frozen_exp) != id(clean_results.diff_exp_instance)


def test_frozen_scan(clean_results) -> None:
    clean_results.prepare_new_results()
    assert isinstance(clean_results.frozen_scan, Scan)
    assert id(clean_results.frozen_scan) != id(clean_results.scan_instance)


def test_source_hash(results) -> None:
    _scan_hash = hash(results.scan_instance)
    _diff_exp_hash = hash(results.diff_exp_instance)
    _tree_hash = hash(results.proc_tree_instance)
    _hash = hash((_scan_hash, _tree_hash, _diff_exp_hash))
    assert _hash == results.source_hash


def test_result_titles__empty(clean_results) -> None:
    assert clean_results.result_titles == {}


def test_result_titles__w_results(results) -> None:
    _titles = results.result_titles
    assert isinstance(_titles, dict)
    assert all(isinstance(_key, int) for _key in _titles.keys())
    assert all(isinstance(_value, str) for _value in _titles.values())


# --------------------
# Tests of public methods
# --------------------


def test_clear_all_results(results) -> None:
    results._saver.set_active_savers(".HDF5")
    results.clear_all_results()
    assert results._composites == {}
    assert results._plugin_result_infos == {}
    assert results._source_hash == -1
    assert results._saver.current_formats == []
    for _key in ["metadata_complete", "composites_created", "saver_metadata_set"]:
        assert not results._config[_key]


def test_prepare_new_results(random_scan, results) -> None:
    for _key in [1, 2]:
        _info = results._plugin_result_infos[_key]
        assert _info.plugin_name != ""
        assert _info.label != ""
        assert _info.result_title != ""
        assert _info.shape == (
            random_scan.shape + (_INPUT_SHAPE if _key == 1 else _NEW_SHAPE)
        )
    assert hash(results._config["frozen_scan"]) == hash(results.scan_instance)
    assert id(results._config["frozen_scan"]) != id(results.scan_instance)
    assert hash(results._config["frozen_exp"]) == hash(results.diff_exp_instance)
    assert id(results._config["frozen_exp"]) != id(results.diff_exp_instance)
    for _id, _node in results.proc_tree_instance.nodes.items():
        assert hash(results._config["frozen_tree"].nodes[_id]) == hash(_node)
    assert id(results._config["frozen_tree"]) != id(results.proc_tree_instance)


def test_update_result_metadata(results, random_scan) -> None:
    _meta = _DEFAULT_PLUGIN_METADATA.copy()
    _full_meta = _create_metadata_with_scan(_meta, random_scan)
    results.update_result_metadata(_meta)
    assert results._config["metadata_complete"]
    for _node, _node_metadata in _full_meta.items():
        _stored_meta = results._plugin_result_infos[_node].dataset_metadata
        for _key, _val in _node_metadata.items():
            _ref = _stored_meta[_key]
            if _key == "axis_ranges":
                for _dim, _range in _val.items():
                    assert np.allclose(_range, _ref[_dim])
            else:
                assert _val == _ref
    assert results.shapes[1] == random_scan.shape + _INPUT_SHAPE
    assert results.shapes[2] == random_scan.shape + _NEW_SHAPE


def test_store_scan_point_results__w_frame_metadata(
    clean_results, result_data, random_scan
) -> None:
    results = clean_results
    results.prepare_new_results()
    results.update_result_metadata(_DEFAULT_PLUGIN_METADATA)
    _index = random_scan.n_points - 1
    results.store_scan_point_results(_index, result_data)
    _scan_indices = random_scan.get_indices_from_ordinal(_index)
    assert np.allclose(result_data[1], results._composites[1][_scan_indices])
    assert np.allclose(result_data[2], results._composites[2][_scan_indices])


def test_store_scan_point_results__no_previous_metadata(
    clean_results, random_scan, result_data
) -> None:
    results = clean_results
    results.prepare_new_results()
    _index = random_scan.n_points - 1
    results.store_scan_point_results(_index, result_data)
    _scan_indices = random_scan.get_indices_from_ordinal(_index)
    assert np.allclose(result_data[1], results._composites[1][_scan_indices])
    assert np.allclose(result_data[2], results._composites[2][_scan_indices])
    assert results._config["metadata_complete"]


def test_store_scan_point_results__w_composites(
    clean_results, random_scan, result_data
) -> None:
    results = clean_results
    results.prepare_new_results()
    results.update_result_metadata(_DEFAULT_PLUGIN_METADATA)
    results._create_composites()
    _index = random_scan.n_points - 2
    results.store_scan_point_results(_index, result_data)
    # repeat storing to verify saver_metadata flag works correctly
    results.store_scan_point_results(_index + 1, result_data)
    _scan_indices = random_scan.get_indices_from_ordinal(_index)
    _scan_indices_b = random_scan.get_indices_from_ordinal(_index + 1)
    assert np.allclose(result_data[1], results._composites[1][_scan_indices])
    assert np.allclose(result_data[2], results._composites[2][_scan_indices])
    assert np.allclose(result_data[1], results._composites[1][_scan_indices_b])
    assert np.allclose(result_data[2], results._composites[2][_scan_indices_b])


def test_store_scan_point_results__w_autosave(
    results, empty_temp_path, result_data, tree, random_scan
) -> None:
    results.prepare_result_export(empty_temp_path, ".nxs")
    results.store_scan_point_results(0, result_data, autosave=True)
    _indices = random_scan.get_indices_from_ordinal(0)
    with h5py.File(_get_node_output_path(1, tree, empty_temp_path), "r") as f:
        _data1 = f["entry/data/data"][_indices]
    with h5py.File(_get_node_output_path(2, tree, empty_temp_path), "r") as f:
        _data2 = f["entry/data/data"][_indices]
    assert np.allclose(_data1, result_data[1])
    assert np.allclose(_data2, result_data[2])


def test_get_result_ranges(results, random_scan) -> None:
    _ranges = results.get_result_ranges(1)
    for _dim, _range in _ranges.items():
        _ref = (
            random_scan.get_range_for_dim(_dim)
            if _dim < random_scan.ndim
            else _DEFAULT_PLUGIN_METADATA[1]["axis_ranges"][_dim - random_scan.ndim]
        )
        assert np.allclose(_range, _ref)


def test_get_result_ranges__no_such_node(results) -> None:
    with pytest.raises(UserConfigError):
        results.get_result_ranges(42)


@pytest.mark.parametrize("squeeze", [True, False])
@pytest.mark.parametrize("flatten", [True, False])
@pytest.mark.parametrize("copy_data", [True, False])
def test_get_results(results, random_scan, squeeze, flatten, copy_data) -> None:
    res = results
    _res = res.get_results(
        1, squeeze=squeeze, flatten_scan_dims=flatten, copy=copy_data
    )
    if flatten:
        assert _res.shape == (random_scan.n_points,) + _INPUT_SHAPE
    else:
        assert _res.shape == random_scan.shape + _INPUT_SHAPE
    assert (id(_res) != id(results._composites[1])) == copy_data


def test_get_results__wrong_node_id() -> None:
    res = ProcessingResults()
    with pytest.raises(UserConfigError):
        res.get_results(3)


def test_store_frame_shapes(results, random_scan) -> None:
    res = results
    res.update_result_metadata(_DEFAULT_PLUGIN_METADATA)
    assert res.shapes == {
        1: random_scan.shape + _INPUT_SHAPE,
        2: random_scan.shape + _NEW_SHAPE,
    }
    assert res._config["metadata_complete"]


def test_store_frame_shapes__wrong_nodes(clean_results) -> None:
    res = clean_results
    res.prepare_new_results()
    _metadata = {1: _DEFAULT_PLUGIN_METADATA[1], 3: _DEFAULT_PLUGIN_METADATA[2]}
    with pytest.raises(KeyError):
        res.update_result_metadata(_metadata)


def test_create_composites(clean_results, random_scan) -> None:
    res = clean_results
    res.prepare_new_results()
    res.update_result_metadata(_DEFAULT_PLUGIN_METADATA)
    res._create_composites()
    assert res._composites[1].shape == random_scan.shape + _INPUT_SHAPE
    assert res._composites[2].shape == random_scan.shape + _NEW_SHAPE


def test_create_composites__shapes_unset(clean_results) -> None:
    res = clean_results
    res.prepare_new_results()
    with pytest.raises(UserConfigError):
        res._create_composites()


def test_get_result_subset__wrong_node_id(results) -> None:
    res = results
    _slice = (0, 0, 0, 0, 0)
    with pytest.raises(UserConfigError):
        res.get_result_subset(42, *_slice)


@pytest.mark.parametrize(
    "flatten_scan_dims,slices",
    [
        (False, (0, 0, 0, 0, 0)),
        (True, (0, 0, 0)),
    ],
    ids=["no_flatten", "flatten"],
)
def test_get_result_subset__single_point(results, flatten_scan_dims, slices) -> None:
    _res = results.get_result_subset(1, *slices, flatten_scan_dims=flatten_scan_dims)
    assert isinstance(_res, Real)


@pytest.mark.parametrize(
    "flatten_scan_dims,build_slices,build_shape",
    [
        (
            False,
            lambda n0, n2: (slice(0, n0), 0, slice(0, n2), 0, 0),
            lambda n0, n2: (n0, n2),
        ),
        (
            True,
            lambda n0, n2: (slice(0, n0 - 3), 0, slice(0, n2)),
            lambda n0, n2: (n0 - 3, n2),
        ),
    ],
    ids=["no_flatten", "flatten"],
)
def test_get_result_subset__slice_array(
    results, random_scan, flatten_scan_dims, build_slices, build_shape
) -> None:
    n0 = random_scan.get_param_value("scan_dim0_n_points")
    n2 = random_scan.get_param_value("scan_dim2_n_points")
    _res = results.get_result_subset(
        1, *build_slices(n0, n2), flatten_scan_dims=flatten_scan_dims
    )
    assert isinstance(_res, np.ndarray)
    assert _res.shape == build_shape(n0, n2)


@pytest.mark.parametrize(
    "squeeze,build_slices,build_shape",
    [
        (
            False,
            lambda n0, n2: (np.arange(n0), [0], np.arange(1, n2 - 1)),
            lambda n0, n2: (n0, 1, n2 - 2) + _INPUT_SHAPE,
        ),
        (
            True,
            lambda n0, n2: (np.arange(n0), [0], np.arange(n2), 0, 0),
            lambda n0, n2: (n0, n2),
        ),
    ],
    ids=["no_squeeze", "squeezed"],
)
def test_get_result_subset__array_indices(
    results, random_scan, squeeze, build_slices, build_shape
) -> None:
    n0 = random_scan.get_param_value("scan_dim0_n_points")
    n2 = random_scan.get_param_value("scan_dim2_n_points")
    _res = results.get_result_subset(1, *build_slices(n0, n2), squeeze=squeeze)
    assert isinstance(_res, np.ndarray)
    assert _res.shape == build_shape(n0, n2)


def test_get_result_subset__ndarray_and_slice(results, random_scan) -> None:
    n0 = random_scan.get_param_value("scan_dim0_n_points")
    n2 = random_scan.get_param_value("scan_dim2_n_points")
    _slices = (np.arange(n0), 0, np.arange(n2 - 2), (0, 2, 3), 0)
    _res = results.get_result_subset(1, *_slices)
    assert isinstance(_res, np.ndarray)
    assert _res.shape == (n0, n2 - 2, 3)


@pytest.mark.parametrize(
    "build_slices,build_shape",
    [
        (
            lambda n0: (
                slice(0, n0 - 3),
                slice(0, _NEW_SHAPE[0] - 1),
                1,
                0,
                slice(1, _NEW_SHAPE[3] - 1),
            ),
            lambda n0: (n0 - 3, _NEW_SHAPE[0] - 1, _NEW_SHAPE[3] - 2),
        ),
        (
            lambda n0: (np.arange(n0 - 3), 0, 0, 0, np.arange(_NEW_SHAPE[3] - 1)),
            lambda n0: (n0 - 3, _NEW_SHAPE[3] - 1),
        ),
    ],
    ids=["slices", "arrays"],
)
def test_get_result_subset__flatten_multidim(
    results, random_scan, build_slices, build_shape
) -> None:
    n0 = random_scan.get_param_value("scan_dim0_n_points")
    _res = results.get_result_subset(2, *build_slices(n0), flatten_scan_dims=True)
    assert isinstance(_res, np.ndarray)
    assert _res.shape == build_shape(n0)


def test_prepare_result_export__setup_incomplete(results, empty_temp_path) -> None:
    results._config["metadata_complete"] = False
    with pytest.raises(UserConfigError):
        results.prepare_result_export(empty_temp_path, ".HDF5")


def test_prepare_result_export__simple(results, empty_temp_path, tree) -> None:
    results.prepare_result_export(empty_temp_path, ".HDF5")
    _files = os.listdir(empty_temp_path)
    for _id in results._composites:
        assert _get_node_output_filename(_id, tree) in _files


def test_prepare_result_export__single_node(results, empty_temp_path, tree) -> None:
    results.prepare_result_export(empty_temp_path, ".HDF5", single_node=1)
    _files = os.listdir(empty_temp_path)
    assert _get_node_output_filename(1, tree) in _files
    assert _get_node_output_filename(2, tree) not in _files


def test_prepare_result_export__w_existing_file_no_overwrite(
    results, empty_temp_path, tree
) -> None:
    results.prepare_result_export(empty_temp_path, ".HDF5", single_node=1)
    with open(empty_temp_path / _get_node_output_filename(1, tree), "w") as _file:
        _file.write("test")
    with pytest.raises(UserConfigError):
        results.prepare_result_export(empty_temp_path, ".HDF5")


def test_prepare_result_export__w_existing_file_w_overwrite(
    results, empty_temp_path, tree
) -> None:
    with h5py.File(empty_temp_path / _get_node_output_filename(1, tree), "w"):
        pass
    results.prepare_result_export(empty_temp_path, ".HDF5", overwrite=True)
    _files = os.listdir(empty_temp_path)
    for _id in results._composites:
        assert _get_node_output_filename(_id, tree) in _files


def test_prepare_result_export__w_non_existing_dir(
    results, empty_temp_path, tree
) -> None:
    empty_temp_path.rmdir()
    results.prepare_result_export(empty_temp_path, ".HDF5")
    _files = os.listdir(empty_temp_path)
    for _id in results._composites:
        assert _get_node_output_filename(_id, tree) in _files


def test_save_results_to_disk__simple(results, empty_temp_path, tree) -> None:
    results.save_results_to_disk(empty_temp_path, ".HDF5")
    with h5py.File(_get_node_output_path(1, tree, empty_temp_path), "r") as f:
        _shape1 = f["entry/data/data"].shape
    with h5py.File(_get_node_output_path(2, tree, empty_temp_path), "r") as f:
        _shape2 = f["entry/data/data"].shape
    assert _shape1 == results.shapes[1]
    assert _shape2 == results.shapes[2]


def test_save_results_to_disk__w_NeXus_name(results, empty_temp_path, tree) -> None:
    results.save_results_to_disk(empty_temp_path, "NeXus (HDF5)")
    with h5py.File(_get_node_output_path(1, tree, empty_temp_path), "r") as f:
        _shape1 = f["entry/data/data"].shape
    with h5py.File(_get_node_output_path(2, tree, empty_temp_path), "r") as f:
        _shape2 = f["entry/data/data"].shape
    assert _shape1 == results.shapes[1]
    assert _shape2 == results.shapes[2]


def test_save_results_to_disk__w_squeeze(results, empty_temp_path, tree) -> None:
    results.save_results_to_disk(empty_temp_path, ".HDF5", squeeze=True)
    with h5py.File(_get_node_output_path(1, tree, empty_temp_path), "r") as f:
        _shape1 = f["entry/data/data"].shape
    with h5py.File(_get_node_output_path(2, tree, empty_temp_path), "r") as f:
        _shape2 = f["entry/data/data"].shape
    assert _shape1 == tuple(n for n in results.shapes[1] if n > 1)
    assert _shape2 == tuple(n for n in results.shapes[2] if n > 1)


def test_save_results_to_disk__single_node(results, empty_temp_path, tree) -> None:
    results.save_results_to_disk(empty_temp_path, ".HDF5", node_id=1)
    with h5py.File(_get_node_output_path(1, tree, empty_temp_path), "r") as f:
        _shape1 = f["entry/data/data"].shape
    assert _shape1 == results.shapes[1]
    assert not _get_node_output_path(2, tree, empty_temp_path).is_file()


def test_get_node_result_metadata_string(results, random_scan) -> None:
    _node_info = results.get_node_result_metadata_string(2, use_scan_timeline=False)
    _ndim_scan = len(
        [_dim for _dim in range(random_scan.ndim) if random_scan.shape[_dim] > 1]
    )
    _ndim_data = len([_dim for _dim in range(len(_NEW_SHAPE)) if _NEW_SHAPE[_dim] > 1])
    for _dim in range(_ndim_scan):
        assert f"Axis #{_dim:02d} (scan):" in _node_info
    for _dim in range(_ndim_scan, _ndim_scan + _ndim_data):
        assert f"Axis #{_dim:02d} (data):" in _node_info
    assert f"Axis #{(_ndim_scan + _ndim_data):02d} (data):" not in _node_info


def test_get_node_result_metadata_string__w_data_size_1(
    random_scan, tree, random_diff_exp
) -> None:
    random_scan.set_param_value("scan_dim", 1)
    random_scan.set_param_value("scan_dim0_n_points", 1)
    tree.delete_node_by_id(1)
    tree.delete_node_by_id(2)
    _proc3 = DummyProcNewDataset(output_shape=(1,))
    _proc3.set_param_value("label", "Test plugin 3")
    tree.create_and_add_node(_proc3)
    _plugin_metadata = {
        1: {
            "axis_units": {0: "m"},
            "axis_labels": {0: "dim1"},
            "axis_ranges": {0: np.array((7))},
            "data_label": "Test",
            "data_unit": "u1",
        }
    }
    _res = ProcessingResults(
        scan=random_scan, processing_tree=tree, diffraction_exp=random_diff_exp
    )
    _res.prepare_new_results()
    _res.update_result_metadata(_plugin_metadata)
    _str = _res.get_node_result_metadata_string(1)
    assert "Data zero-dimensional" in _str


def test_get_node_result_metadata_string__w_scan_timeline(results) -> None:
    _node_info = results.get_node_result_metadata_string(1, use_scan_timeline=True)
    assert "Axis #00 (scan):" in _node_info
    for _dim in range(1, 1 + len(_INPUT_SHAPE)):
        assert f"Axis #{_dim:02d} (data):" in _node_info


def test_get_node_result_metadata_string__no_squeeze(results, random_scan) -> None:
    _node_info = results.get_node_result_metadata_string(
        2, use_scan_timeline=False, squeeze=False
    )
    for _dim in range(random_scan.ndim):
        assert f"Axis #{_dim:02d} (scan):" in _node_info
    for _dim in range(random_scan.ndim, random_scan.ndim + len(_NEW_SHAPE)):
        assert f"Axis #{_dim:02d} (data):" in _node_info
    assert f"Axis #{(random_scan.ndim + len(_NEW_SHAPE)):02d} (data):" not in _node_info


def test_import_data_from_directory__empty_dir(empty_temp_path) -> None:
    _scan_title = get_random_string(8)
    ScanContext().set_param_value("scan_title", _scan_title)
    res = ProcessingResults()
    res.import_data_from_directory(empty_temp_path)
    assert res.shapes == {}
    assert res.scan_instance.get_param_value("scan_title") == _scan_title


def test_import_data_from_directory__with_files(
    results, result_data, empty_temp_path, tree, random_scan, random_diff_exp
) -> None:
    _data = {}
    for _id, _shape in results.shapes.items():
        _data[_id] = create_dataset(len(_shape), shape=_shape)
        create_hdf5_results_file(
            _get_node_output_path(_id, tree, empty_temp_path),
            _data[_id],
            random_scan,
            random_diff_exp,
            tree,
            node_id=_id,
            node_label=tree.nodes[_id].plugin.get_param_value("label"),
            plugin_name=tree.nodes[_id].plugin.plugin_name,
        )
    results.clear_all_results()
    results.import_data_from_directory(empty_temp_path)
    for _id in [1, 2]:
        _res_info = results._plugin_result_infos[_id]
        assert _res_info.shape == (
            random_scan.shape + (_INPUT_SHAPE if _id == 1 else _NEW_SHAPE)
        )
        assert _res_info.label == tree.nodes[_id].plugin.get_param_value("label")
        assert _res_info.plugin_name == tree.nodes[_id].plugin.plugin_name
        assert _res_info.result_title == tree.nodes[_id].plugin.result_title
        for _dim in range(_res_info.ndim):
            _ref = _data[_id].axis_ranges[_dim]
            assert np.allclose(_res_info.axis_ranges[_dim], _ref)


def test_update_from_processing_results__wrong_type() -> None:
    res = ProcessingResults()
    with pytest.raises(TypeError):
        res.update_from_processing_results(  # type: ignore[arg-type]
            "not a ProcessingResults instance"
        )


def test_update_from_processing_results(results) -> None:
    _new_res = ProcessingResults()
    _new_res.update_from_processing_results(results)
    assert _new_res.shapes == results.shapes
    assert _get_node_labels(_new_res) == _get_node_labels(results)
    assert _get_data_labels(_new_res) == _get_data_labels(results)
    assert _get_data_units(_new_res) == _get_data_units(results)
    assert _new_res.ndims == results.ndims
    assert (
        _new_res.frozen_tree.export_to_string()
        == results.frozen_tree.export_to_string()
    )
    assert _new_res.frozen_exp.param_values == results.frozen_exp.param_values
    assert _new_res.frozen_scan.param_values == results.frozen_scan.param_values


#
#
#
# def test_get_result_metadata__wrong_id(results) -> None:
#     res = results
#     with pytest.raises(UserConfigError):
#         res._node_result_metadata(3)
#
#
# def test_get_result_metadata(results) -> None:
#     res = results
#     _tmp_array = np.random.random((50, 50))
#     res._composites[0] = Dataset(
#         _tmp_array,
#         axis_labels=[chr(_i + 97) for _i in range(_tmp_array.ndim)],
#         axis_units=["unit_" + chr(_i + 97) for _i in range(_tmp_array.ndim)],
#         metadata={"spam": "eggs"},
#         axis_ranges={0: 2 + 0.4 * np.arange(50), 1: -3 * np.arange(50)},
#     )
#     _metadata = res._node_result_metadata(0)
#     assert isinstance(_metadata, dict)
#     for _key in ["axis_labels", "axis_units", "metadata"]:
#         assert _metadata[_key] == getattr(res._composites[0], _key)
#     for _dim in range(2):
#         assert np.allclose(
#             _metadata["axis_ranges"][_dim], res._composites[0].axis_ranges[_dim]
#         )
#
#
# def test_get_result_metadata__use_scan_timeline(results, random_scan) -> None:
#     res = results
#     _curr_meta_info = {"spam": "eggs"}
#     _tmp_array = np.random.random(random_scan.shape + (50, 50))
#     res._composites[0] = Dataset(
#         _tmp_array,
#         axis_labels=[chr(_i + 97) for _i in range(_tmp_array.ndim)],
#         axis_units=["unit_" + chr(_i + 97) for _i in range(_tmp_array.ndim)],
#         metadata=_curr_meta_info,
#     )
#     _metadata = res._node_result_metadata(0, use_scan_timeline=True)
#     assert isinstance(_metadata, dict)
#     assert _metadata["metadata"] == _curr_meta_info
#     for _key in ["axis_labels", "axis_units"]:
#         _entries = list(_metadata[_key].values())[1:]
#         _ref = list(getattr(res._composites[0], _key).values())[random_scan.ndim :]
#         assert _entries == _ref
#
#
# def test_processing_result_saver__expected_export_filenames(results, tree) -> None:
#     res = results
#     saver = ProcessingResultSaver()
#     saver.set_active_savers(".HDF5")
#     _filenames = saver.expected_export_filenames(res._plugin_result_infos)
#     assert sorted(_filenames) == sorted(
#         [_get_node_output_filename(1, tree), _get_node_output_filename(2, tree)]
#     )


if __name__ == "__main__":
    pytest.main([__file__])

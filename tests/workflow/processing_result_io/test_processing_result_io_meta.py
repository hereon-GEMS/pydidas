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


from unittest.mock import patch

import numpy as np
import pytest

from pydidas.contexts import DiffractionExperimentContext, Scan, ScanContext
from pydidas.contexts.diff_exp.diff_exp import DiffractionExperiment
from pydidas.core import Dataset, UserConfigError
from pydidas.core.utils import get_random_string
from pydidas.unittest_objects.create_dataset_ import create_dataset
from pydidas.workflow import ProcessingResults, WorkflowTree
from pydidas.workflow.processing_tree import ProcessingTree
from pydidas.workflow.result_io import ProcessingResultIoBase, ProcessingResultIoMeta


TREE = WorkflowTree()
EXP = DiffractionExperimentContext()
SCAN = ScanContext()
RESULTS = ProcessingResults()
META = ProcessingResultIoMeta


@pytest.fixture
def io_meta():
    _backup = META.registry
    META.registry = {}
    yield META
    META.registry = _backup


@pytest.fixture
def temp_dir(tmp_path):
    yield tmp_path


def create_saver_class(title, ext: str | list[str]):
    if isinstance(ext, str):
        ext = [ext.lower()]
    _cls = META(
        title.upper(),
        (ProcessingResultIoBase,),
        {
            "extensions": ext,
            "format_name": get_random_string(10),
            "default_suffix": ext[0],
        },
    )
    return _cls


@pytest.fixture
def get_save_dir_and_node_info():
    def _factory():
        _save_dir = "dummy/directory/to/nowhere"
        _shapes = {1: (10, 10), 2: (11, 27)}
        _node_labels = {1: "unknown", 2: "result no 2"}
        _data_labels = {1: "Intensity", 2: "Area"}
        _plugin_names = {1: "ye olde plugin", 2: "SPAM SPAM SPAM"}
        _node_info = {
            _id: {
                "shape": _shapes[_id],
                "node_label": _node_labels[_id],
                "data_label": _data_labels[_id],
                "plugin_name": _plugin_names[_id],
            }
            for _id in _shapes
        }
        return _save_dir, _node_info

    return _factory


@pytest.fixture
def generate_test_metadata(get_save_dir_and_node_info):
    def _factory():
        _, _node_info = get_save_dir_and_node_info()
        _shapes = {_id: _node_info[_id]["shape"] for _id in _node_info}
        _res1 = Dataset(
            np.random.random(_shapes[1]),
            axis_units=["m", "mm"],
            axis_labels=["dim1", "dim 2"],
            axis_ranges=[
                np.arange(_shapes[1][0]),
                _shapes[1][1] - np.arange(_shapes[1][1]),
            ],
        )
        _res2 = Dataset(
            np.random.random(_shapes[2]),
            axis_units=["m", "Test"],
            axis_labels=["dim1", "2nd dim"],
            axis_ranges=[12 + np.arange(_shapes[2][0]), 4 + np.arange(_shapes[2][1])],
        )
        _meta1 = {
            "axis_units": _res1.axis_units,
            "axis_labels": _res1.axis_labels,
            "axis_ranges": _res1.axis_ranges,
        }
        _meta2 = {
            "axis_units": _res2.axis_units,
            "axis_labels": _res2.axis_labels,
            "axis_ranges": _res2.axis_ranges,
        }
        return {1: _meta1, 2: _meta2}

    return _factory


def test__class_type(io_meta):
    assert type(io_meta) is type


def test__class_attributes(io_meta):
    assert hasattr(io_meta, "registry")


def test_register_class(io_meta):
    _saver = create_saver_class("SAVER_TEST", ".test")
    assert ".test" in io_meta.registry
    assert io_meta.registry[".test"] is _saver
    assert _saver.format_name in io_meta.format_registry
    assert io_meta.format_registry[_saver.format_name] == _saver.default_suffix


@pytest.mark.parametrize("savers", [None, ""])
def test_get_savers__with_none(io_meta, savers):
    result = io_meta.get_savers(savers)
    assert result == {}
    assert isinstance(result, dict)


@pytest.mark.parametrize("savers", [".test", "test"])
def test_get_savers__with_single_extension(io_meta, savers):
    saver_test = create_saver_class("SAVER_TEST", ".test")
    _res = io_meta.get_savers(savers)
    assert ".test" in _res
    assert isinstance(_res[".test"], saver_test)


@pytest.mark.parametrize("savers", [[".test", "hdf5"], ".test; .hdf5"])
def test_get_savers__with_multiple_extensions_list(io_meta, savers):
    saver_test = create_saver_class("SAVER_TEST", ".test")
    saver_hdf5 = create_saver_class("SAVER_HDF5", ".hdf5")
    _res = io_meta.get_savers(savers)
    assert len(_res) == 2
    assert ".test" in _res
    assert ".hdf5" in _res
    assert isinstance(_res[".test"], saver_test)
    assert isinstance(_res[".hdf5"], saver_hdf5)


@pytest.mark.parametrize("ext", [".test", ".TeST", ".TEST", ".teST"])
def test_get_savers__case_insensitivity(io_meta, ext):
    saver_test = create_saver_class("SAVER_TEST", ".test")
    result = io_meta.get_savers(ext)
    assert ".test" in result
    assert isinstance(result[".test"], saver_test)


@pytest.mark.parametrize(
    "ext", [[".test", ".test", ".dummy"], [".test", ".dummy"], [".dummy", ".test"]]
)
def test_get_savers__duplicate_formats(io_meta, ext):
    create_saver_class("SAVER_TEST", [".test", ".dummy"])
    result = io_meta.get_savers(ext)
    assert len(result) == 1
    assert ext[0] in result
    assert ext[-1] not in result


def test_get_savers__w_format_name(io_meta):
    _cls = create_saver_class("SAVER_TEST", [".test", ".dummy"])
    _ext = _cls.extensions
    _format_name = _cls.format_name
    _savers = io_meta.get_savers(_format_name)
    assert len(_savers) == 1
    assert _ext[0] in _savers
    assert _ext[-1] not in _savers


def test_get_savers__unregistered_format_raises(io_meta):
    with pytest.raises(UserConfigError):
        io_meta.get_savers(".unregistered")


def test_get_savers__multiple_calls_different_instances(io_meta):
    create_saver_class("SAVER_TEST", ".test")
    result1 = io_meta.get_savers([".test"])
    result2 = io_meta.get_savers([".test"])
    assert result1[".test"] is not result2[".test"]
    assert type(result1[".test"]) is type(result2[".test"])


@pytest.mark.parametrize(
    "node_id, filename", [(1, "node_01.test"), (3, "node_03.hdf5")]
)
def test_import_data_from_directory(io_meta, temp_dir, node_id, filename):
    saver_test = create_saver_class("SAVER_TEST", ".test")
    saver_hdf5 = create_saver_class("SAVER_HDF5", ".hdf5")

    (temp_dir / filename).write_text("dummy")
    _input_data = create_dataset(2, shape=(10, 10 * node_id))

    def mock_import(_fname):
        return _input_data, {}, SCAN, EXP, TREE

    with (
        patch.object(
            saver_test, "import_results_from_file", side_effect=mock_import
        ) as mock_test,
        patch.object(
            saver_hdf5, "import_results_from_file", side_effect=mock_import
        ) as mock_hdf5,
    ):
        _data, _node_info, _scan, _exp, _tree = io_meta.import_data_from_directory(
            temp_dir
        )

        if ".test" in filename:
            assert mock_test.called
            assert not mock_hdf5.called
            mock_test.assert_called_once()
            _test_call_arg = mock_test.call_args[0][0]
            assert "node_01.test" in str(_test_call_arg)
        if ".hdf5" in filename:
            assert mock_hdf5.called
            assert not mock_test.called
            mock_hdf5.assert_called_once()
            _hdf5_call_arg = mock_hdf5.call_args[0][0]
            assert "node_03.hdf5" in str(_hdf5_call_arg)

    assert node_id in _data
    assert np.allclose(_data[node_id], _input_data)
    assert isinstance(_scan, Scan)
    assert isinstance(_exp, DiffractionExperiment)
    assert isinstance(_tree, ProcessingTree)


if __name__ == "__main__":
    pytest.main([__file__])

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

"""Unit tests for pydidas.workflow.processing_result_saver module."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from pathlib import Path
from unittest.mock import patch

import pytest

from pydidas.contexts import (
    DiffractionExperiment,
    Scan,
)
from pydidas.plugins.plugin_result_info import PluginResultInfo
from pydidas.unittest_objects import create_dataset
from pydidas.workflow.processing_result_saver import ProcessingResultSaver
from pydidas.workflow.processing_tree import ProcessingTree
from pydidas.workflow.result_io import ProcessingResultIoBase, ProcessingResultIoMeta


@pytest.fixture
def saver():
    return ProcessingResultSaver()


@pytest.fixture
def io_meta():
    _backup = ProcessingResultIoMeta.registry
    ProcessingResultIoMeta.registry = {}
    yield ProcessingResultIoMeta
    ProcessingResultIoMeta.registry = _backup


def create_mock_saver_class(title: str, ext: str) -> type[ProcessingResultIoBase]:
    _cls = ProcessingResultIoMeta(
        title.upper(),
        (ProcessingResultIoBase,),
        dict(extensions=[ext.lower()], format_name=ext),
    )
    return _cls  # type: ignore[arg-type]


@pytest.fixture
def node_info():
    return {
        1: PluginResultInfo(label="node_1", node_id=1),
        2: PluginResultInfo(label="node_2", node_id=2),
    }


def test_init(saver):
    assert isinstance(saver, ProcessingResultSaver)
    assert saver._active_savers == {}
    assert saver._config["savers_ready"] is False


def test_current_formats__empty(saver):
    formats = saver.current_formats
    assert formats == []
    assert isinstance(formats, list)


def test_set_active_savers__with_none(saver, io_meta):
    saver.set_active_savers(None)
    assert saver._active_savers == {}
    assert saver._config["savers_ready"] is False


def test_set_active_savers__with_single_format(saver, io_meta):
    create_mock_saver_class("SAVER_TEST", ".test")
    saver.set_active_savers(".test")
    assert ".test" in saver._active_savers
    assert saver._config["savers_ready"] is False


@pytest.mark.parametrize("save_formats", [[".test", ".hdf5"], ".test;hdf5"])
def test_set_active_savers__with_list(saver, io_meta, save_formats):
    create_mock_saver_class("SAVER_TEST", ".test")
    create_mock_saver_class("SAVER_HDF5", ".hdf5")
    saver.set_active_savers(save_formats)
    assert len(saver._active_savers) == 2
    assert ".test" in saver._active_savers
    assert ".hdf5" in saver._active_savers


def test_set_active_savers__clears_ready_flag(saver, io_meta):
    create_mock_saver_class("SAVER_TEST", ".test")
    saver._config["savers_ready"] = True
    saver.set_active_savers(".test")
    assert saver._config["savers_ready"] is False


def test_expected_export_filenames(saver, io_meta, node_info):
    create_mock_saver_class("SAVER_TEST", ".test")
    saver.set_active_savers(".test")
    filenames = saver.expected_export_filenames(node_info)
    assert isinstance(filenames, list)
    assert len(filenames) == len(node_info)


def test_expected_export_filenames__multiple_savers(saver, io_meta, node_info):
    create_mock_saver_class("SAVER_TEST", ".test")
    create_mock_saver_class("SAVER_HDF5", ".hdf5")
    saver.set_active_savers([".test", ".hdf5"])
    filenames = saver.expected_export_filenames(node_info)
    assert len(filenames) == len(node_info) * 2


def test_expected_export_filenames__no_savers(saver, node_info):
    filenames = saver.expected_export_filenames(node_info)
    assert filenames == []


@pytest.mark.parametrize("str_path", [True, False])
def test_prepare_active_savers(saver, io_meta, node_info, tmp_path, str_path):
    create_mock_saver_class("SAVER_TEST", ".test")
    saver.set_active_savers(".test")
    _path = str(tmp_path) if str_path else tmp_path
    saver.prepare_active_savers(_path, node_info)
    assert saver._config["save_dir"] == Path(tmp_path)
    assert saver._config["savers_ready"] is True


def test_prepare_active_savers__with_contexts(saver, io_meta, node_info, tmp_path):
    create_mock_saver_class("SAVER_TEST", ".test")
    saver.set_active_savers(".test")
    scan = Scan()
    exp = DiffractionExperiment()
    tree = ProcessingTree()

    with patch.object(
        saver._active_savers[".test"], "prepare_files_and_directories"
    ) as mock_prepare:
        saver.prepare_active_savers(
            tmp_path,
            node_info,
            scan=scan,
            diffraction_exp=exp,
            processing_tree=tree,
        )
        mock_prepare.assert_called_once()
        call_kwargs = mock_prepare.call_args[1]
        assert call_kwargs["scan"] is scan
        assert call_kwargs["diffraction_exp"] is exp
        assert call_kwargs["processing_tree"] is tree


def test_prepare_active_savers__multiple_savers(saver, io_meta, node_info, tmp_path):
    create_mock_saver_class("SAVER_TEST", ".test")
    create_mock_saver_class("SAVER_HDF5", ".hdf5")
    saver.set_active_savers([".test", ".hdf5"])
    with patch.object(
        ProcessingResultIoBase, "prepare_files_and_directories"
    ) as mock_prepare:
        saver.prepare_active_savers(tmp_path, node_info)
        # Should be called for each saver
        assert mock_prepare.call_count == 2


def test_update_saver_metadata(saver, io_meta):
    create_mock_saver_class("SAVER_TEST", ".test")
    saver.set_active_savers(".test")
    metadata = {
        1: {"axis_labels": ["x", "y"], "data_label": "test"},
        2: {"axis_labels": ["a", "b"], "data_label": "data"},
    }
    with patch.object(
        saver._active_savers[".test"], "update_result_metadata"
    ) as mock_update:
        saver.update_saver_metadata(metadata)
        mock_update.assert_called_once_with(metadata)


def test_update_saver_metadata__multiple_savers(saver, io_meta):
    create_mock_saver_class("SAVER_TEST", ".test")
    create_mock_saver_class("SAVER_HDF5", ".hdf5")
    saver.set_active_savers([".test", ".hdf5"])
    metadata = {1: {"data_label": "test"}}
    with patch.object(ProcessingResultIoBase, "update_result_metadata") as mock_update:
        saver.update_saver_metadata(metadata)
        # Should be called for each saver
        assert mock_update.call_count == 2


def test_export_frame_to_active_savers(saver, io_meta):
    create_mock_saver_class("SAVER_TEST", ".test")
    saver.set_active_savers(".test")
    _frame_data = {1: create_dataset(2), 2: create_dataset(2)}
    with patch.object(
        saver._active_savers[".test"],
        "export_frame_to_file",
    ) as mock_export:
        saver.export_frame_to_active_savers(42, _frame_data)
        mock_export.assert_called_once_with(42, _frame_data)


def test_export_frame_to_active_savers__with_kwargs(saver, io_meta):
    create_mock_saver_class("SAVER_TEST", ".test")
    saver.set_active_savers(".test")
    _frame_data = {1: create_dataset(2)}
    with patch.object(
        saver._active_savers[".test"],
        "export_frame_to_file",
    ) as mock_export:
        saver.export_frame_to_active_savers(42, _frame_data, custom_param="value")
        mock_export.assert_called_once()
        call_args = mock_export.call_args
        assert call_args[0] == (42, _frame_data)
        assert call_args[1]["custom_param"] == "value"


def test_export_frame_to_active_savers__multiple_savers(saver, io_meta):
    create_mock_saver_class("SAVER_TEST", ".test")
    create_mock_saver_class("SAVER_HDF5", ".hdf5")
    saver.set_active_savers([".test", ".hdf5"])
    _frame_data = {1: create_dataset(2)}
    with patch.object(ProcessingResultIoBase, "export_frame_to_file") as mock_export:
        saver.export_frame_to_active_savers(0, _frame_data)
        # Should be called for each saver
        assert mock_export.call_count == 2


def test_export_full_data_to_active_savers(saver, io_meta):
    create_mock_saver_class("SAVER_TEST", ".test")
    saver.set_active_savers(".test")
    _full_data = {1: create_dataset(3), 2: create_dataset(3)}
    with patch.object(
        saver._active_savers[".test"],
        "export_full_data_to_file",
    ) as mock_export:
        saver.export_full_data_to_active_savers(_full_data)
        mock_export.assert_called_once_with(_full_data, squeeze=False)


def test_export_full_data_to_active_savers__with_squeeze(saver, io_meta):
    create_mock_saver_class("SAVER_TEST", ".test")
    saver.set_active_savers(".test")
    _full_data = {1: create_dataset(3)[:, 0]}  # type: ignore[arg-type]
    with patch.object(
        saver._active_savers[".test"],
        "export_full_data_to_file",
    ) as mock_export:
        saver.export_full_data_to_active_savers(_full_data, squeeze=True)
        mock_export.assert_called_once_with(_full_data, squeeze=True)


def test_export_full_data_to_active_savers__multiple_savers(saver, io_meta):
    create_mock_saver_class("SAVER_TEST", ".test")
    create_mock_saver_class("SAVER_HDF5", ".hdf5")
    saver.set_active_savers([".test", ".hdf5"])
    _full_data = {1: create_dataset(3)}
    with patch.object(
        ProcessingResultIoBase, "export_full_data_to_file"
    ) as mock_export:
        saver.export_full_data_to_active_savers(_full_data)
        assert mock_export.call_count == 2


if __name__ == "__main__":
    pytest.main([__file__])

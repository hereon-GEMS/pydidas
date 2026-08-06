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
from typing import ClassVar
from unittest.mock import MagicMock, patch

import pytest

from pydidas.plugins.plugin_result_info import PluginResultInfo
from pydidas.workflow.result_io import ProcessingResultIoBase, ProcessingResultIoMeta


@pytest.fixture(scope="module")
def saver_class():
    _registry = ProcessingResultIoMeta.registry.copy()
    ProcessingResultIoMeta.clear_registry()

    class TestSaver(ProcessingResultIoBase):
        extensions: ClassVar[list[str]] = ["TEST"]
        default_suffix = ".Test"
        format_name = "Test"

    yield TestSaver
    ProcessingResultIoMeta.clear_registry()
    ProcessingResultIoMeta.registry = _registry


@pytest.fixture
def saver(saver_class):
    return saver_class()


def test_class_base(saver_class):
    assert ProcessingResultIoBase in saver_class.__bases__


class SharedTestProcessingResultIo:
    """Shared tests for ProcessingResultIoBase implementations."""

    @staticmethod
    def node_info():
        return {
            5: PluginResultInfo(label="__\n _ \t pretty@!%ugly_name", node_id=5),
            7: PluginResultInfo(label="a_name", node_id=7),
        }

    @pytest.mark.parametrize(
        "node_id, label, expected",
        [
            (5, "__\n _ \t pretty@!%ugly_name", "node_05_pretty_ugly_name"),
            (7, "a_name", "node_07_a_name"),
            (3, "", "node_03"),
            (9, None, "node_09"),
            (1, "a__b____c", "node_01_a_b_c"),
            (2, "my-label-name", "node_02_my-label-name"),
        ],
    )
    def test_get_filenames(self, saver, node_id, label, expected):
        _node_info = {node_id: PluginResultInfo(label=label, node_id=node_id)}
        _names = saver.get_filenames(_node_info)
        assert _names[node_id] == (expected + saver.default_suffix)

    def test_get_filenames__returns_all_node_ids(self, saver):
        _names = saver.get_filenames(self.node_info())
        assert set(_names.keys()) == {5, 7}

    def test_get_filenames__w_empty_dict(self, saver):
        _names = saver.get_filenames({})
        assert _names == {}

    def test_prepare_files_and_directories__creates_dir(self, saver, tmp_path):
        _new_dir = tmp_path / "output"
        assert not _new_dir.exists()
        saver.prepare_files_and_directories(_new_dir, {})
        assert _new_dir.exists()

    def test_prepare_files_and_directories__sets_save_dir(self, saver, tmp_path):
        saver.prepare_files_and_directories(tmp_path, {})
        assert saver._config["save_dir"] == Path(tmp_path)

    def test_prepare_files_and_directories__sets_filenames(self, saver, tmp_path):
        saver.prepare_files_and_directories(tmp_path, self.node_info())
        _fnames = saver._config["filenames"]
        assert _fnames[5] == tmp_path / (
            "node_05_pretty_ugly_name" + saver.default_suffix
        )
        assert _fnames[7] == tmp_path / ("node_07_a_name" + saver.default_suffix)

    def test_prepare_files_and_directories__check_uses_kwargs(self, saver, tmp_path):
        _scan = MagicMock()
        _exp = MagicMock()
        _tree = MagicMock()
        saver.prepare_files_and_directories(
            tmp_path, {}, scan=_scan, diffraction_exp=_exp, processing_tree=_tree
        )
        assert saver._config["scan"] is _scan
        assert saver._config["diffraction_exp"] is _exp
        assert saver._config["processing_tree"] is _tree

    def test_prepare_files_and_directories__uses_defaults(self, saver, tmp_path):
        _scan_mock = MagicMock()
        _exp_mock = MagicMock()
        _tree_mock = MagicMock()
        with (
            patch(
                "pydidas.workflow.result_io.processing_result_io_base.ScanContext",
                return_value=_scan_mock,
            ),
            patch(
                "pydidas.workflow.result_io.processing_result_io_base.DiffractionExperimentContext",
                return_value=_exp_mock,
            ),
            patch(
                "pydidas.workflow.result_io.processing_result_io_base.WorkflowTree",
                return_value=_tree_mock,
            ),
        ):
            saver.prepare_files_and_directories(tmp_path, {})
        assert saver._config["scan"] is _scan_mock
        assert saver._config["diffraction_exp"] is _exp_mock
        assert saver._config["processing_tree"] is _tree_mock


def test_export_frame_to_file__raises(saver):
    with pytest.raises(NotImplementedError):
        saver.export_frame_to_file(0, {})


def test_export_full_data_to_file__raises(saver):
    with pytest.raises(NotImplementedError):
        saver.export_full_data_to_file({})


def test_update_result_metadata__raises(saver):
    with pytest.raises(NotImplementedError):
        saver.update_result_metadata({})


def test_import_results_from_file__is_staticmethod():
    assert isinstance(
        ProcessingResultIoBase.__dict__["import_results_from_file"], staticmethod
    )


def test_import_results_from_file__raises(saver_class):
    with pytest.raises(NotImplementedError):
        saver_class.import_results_from_file("dummy")


class TestProcessingResultIoBase(SharedTestProcessingResultIo): ...


if __name__ == "__main__":
    pytest.main([__file__])

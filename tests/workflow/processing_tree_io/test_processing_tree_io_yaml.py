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

import pytest
import yaml

import pydidas
from pydidas.core import UserConfigError
from pydidas.workflow import ProcessingTree
from pydidas.workflow.processing_tree_io import ProcessingTreeIoMeta
from pydidas.workflow.processing_tree_io.processing_tree_io_yaml import (
    ProcessingTreeIoYaml,
)


PLUGIN_COLL = pydidas.plugins.PluginCollection()


@pytest.fixture
def yaml_filename(temp_path: Path) -> Path:
    return temp_path / "test.yaml"


def create_correct_export(filename: Path, tree: ProcessingTree) -> None:
    with open(filename, "w") as _f:
        _dump = {
            "nodes": tree.export_to_list_of_nodes(),
            "version": pydidas.VERSION,
        }
        yaml.safe_dump(_dump, _f)


def test_export_to_file(yaml_filename: Path, test_tree: ProcessingTree) -> None:
    ProcessingTreeIoYaml.export_to_file(yaml_filename, test_tree, overwrite=True)
    with open(yaml_filename, "r") as f:
        _save = yaml.safe_load(f)
    assert "version" in _save
    assert "nodes" in _save
    assert _save["version"] == pydidas.VERSION
    # assert does not raise an error
    _new = ProcessingTree()
    _new.restore_from_list_of_nodes(_save["nodes"])


def test_import_from_file__w_version(
    yaml_filename: Path, test_tree: ProcessingTree
) -> None:
    create_correct_export(yaml_filename, test_tree)
    _new = ProcessingTreeIoYaml.import_from_file(yaml_filename)
    assert set(_new.nodes) == set(test_tree.nodes)
    for _id, _node in _new.nodes.items():
        assert set(_node.plugin.params) == set(test_tree.nodes[_id].plugin.params)


def test_import_from_file__wrong_format(
    yaml_filename: Path, test_tree: ProcessingTree
) -> None:
    _list = [1, 2, 3, 5]
    with open(yaml_filename, "w") as _f:
        yaml.safe_dump(_list, _f)
    with pytest.raises(UserConfigError):
        ProcessingTreeIoYaml.import_from_file(yaml_filename)


def test_import_from_file__w_version_and_error(
    yaml_filename: Path, test_tree: ProcessingTree
) -> None:
    with open(yaml_filename, "w") as _f:
        _dump = {"nodes": "np.ndarrray((12))", "version": pydidas.VERSION}
        yaml.safe_dump(_dump, _f)
    with pytest.raises(UserConfigError):
        ProcessingTreeIoYaml.import_from_file(yaml_filename)


def test_import_from_file__old_version_no_error(
    yaml_filename: Path, test_tree: ProcessingTree
) -> None:
    with open(yaml_filename, "w") as _f:
        _dump = {
            "nodes": test_tree.export_to_list_of_nodes(),
            "version": "0.0.0",
        }
        yaml.safe_dump(_dump, _f)
    _new = ProcessingTreeIoYaml.import_from_file(yaml_filename)
    assert set(_new.nodes) == set(test_tree.nodes)
    for _id, _node in _new.nodes.items():
        assert set(_node.plugin.params) == set(test_tree.nodes[_id].plugin.params)


def test_import_from_file__old_version_w_error(yaml_filename: Path) -> None:
    with open(yaml_filename, "w") as _f:
        _dump = {"nodes": "dummy incorrect string", "version": "0.0.0"}
        yaml.safe_dump(_dump, _f)
    with pytest.raises(UserConfigError):
        ProcessingTreeIoYaml.import_from_file(yaml_filename)


def test_export_to_file__existing_file_no_overwrite(
    yaml_filename: Path, test_tree: ProcessingTree
) -> None:
    with open(yaml_filename, "w") as f:
        f.write("test")
    with pytest.raises(FileExistsError):
        ProcessingTreeIoYaml.export_to_file(yaml_filename, test_tree)


def test_export_to_file__existing_file__replace(
    yaml_filename: Path, test_tree: ProcessingTree
) -> None:
    with open(yaml_filename, "w") as f:
        f.write("test")
    ProcessingTreeIoYaml.export_to_file(yaml_filename, test_tree, replace=True)
    # assert does not raise an error


def test__meta_import_from_file(yaml_filename: Path, test_tree: ProcessingTree) -> None:
    """Test importing via ProcessingTreeIoMeta."""
    ProcessingTreeIoMeta.register_class(ProcessingTreeIoYaml, update_registry=True)
    create_correct_export(yaml_filename, test_tree)
    _new = ProcessingTreeIoMeta.import_from_file(yaml_filename)
    assert set(_new.nodes) == set(test_tree.nodes)
    for _id, _node in _new.nodes.items():
        assert set(_node.plugin.params) == set(test_tree.nodes[_id].plugin.params)


if __name__ == "__main__":
    pytest.main([__file__])

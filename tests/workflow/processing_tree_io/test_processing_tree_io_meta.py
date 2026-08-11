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


from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock

from pydidas.workflow.processing_tree import ProcessingTree


import pytest  # isort:skip

from pydidas.workflow.processing_tree_io import ProcessingTreeIoMeta


@pytest.fixture(autouse=True)
def cleanup_registry() -> Generator[None, Any, None]:
    """Clear registry before and after test."""
    ProcessingTreeIoMeta.clear_registry()
    yield
    ProcessingTreeIoMeta.clear_registry()


@pytest.fixture
def test_class_registered() -> Generator[MagicMock, Any, None]:
    """Create and register a mock class with ProcessingTreeIoMeta."""
    # Create a mock class with local trees storage
    mock_io_ops: dict[str, Any] = {}

    def mock_export_to_file(filename: str, tree: Any) -> None:
        """Mock export_to_file method."""
        mock_io_ops[filename] = tree

    def mock_import_from_file(filename: str) -> Any:
        """Mock import_from_file method."""
        if filename in mock_io_ops:
            return mock_io_ops[filename]
        raise KeyError("filename not registered")

    # Create a mock class with the required attributes
    mock_class = MagicMock()
    mock_class.extensions = [".test", ".another_test"]
    mock_class.format_name = "Test"
    mock_class.mock_io_ops = mock_io_ops
    mock_class.export_to_file = MagicMock(side_effect=mock_export_to_file)
    mock_class.import_from_file = MagicMock(side_effect=mock_import_from_file)
    mock_class.__name__ = "MockTestClass"

    # Manually register the mock class extensions in the registry
    for ext in mock_class.extensions:
        ProcessingTreeIoMeta.registry[ext] = mock_class  # type: ignore[assignment]

    yield mock_class


def test__empty() -> None:
    assert ProcessingTreeIoMeta.registry == {}


def test__w_class(test_class_registered: MagicMock) -> None:
    assert len(ProcessingTreeIoMeta.registry) > 0
    for _key in test_class_registered.extensions:
        assert _key in ProcessingTreeIoMeta.registry


def test_import_from_file(test_class_registered: MagicMock) -> None:
    _test_tree = ProcessingTree()
    test_class_registered.mock_io_ops["dummy.test"] = _test_tree
    _reply = ProcessingTreeIoMeta.import_from_file("dummy.test")
    assert _test_tree == _reply


def test_export_to_file(test_class_registered: MagicMock) -> None:
    _test_tree = ProcessingTree()
    ProcessingTreeIoMeta.export_to_file("dummy.test", _test_tree)
    assert _test_tree == test_class_registered.mock_io_ops["dummy.test"]


def test_get_string_of_formats__empty(cleanup_registry: None) -> None:
    assert ProcessingTreeIoMeta.get_string_of_formats() == "All supported files ()"


def test_get_string_of_formats__w_entry(test_class_registered: MagicMock) -> None:
    _res = ProcessingTreeIoMeta.get_string_of_formats()
    _ref = "All supported files (*.test *.another_test);;Test (*.test *.another_test)"
    assert _res == _ref


def test_get_registered_formats_empty(cleanup_registry: None) -> None:
    assert ProcessingTreeIoMeta.get_registered_formats() == {}


def test_get_registered_formats__w_entry(test_class_registered: MagicMock) -> None:
    res = ProcessingTreeIoMeta.get_registered_formats()
    assert res == {test_class_registered.format_name: test_class_registered.extensions}


if __name__ == "__main__":
    pytest.main([__file__])

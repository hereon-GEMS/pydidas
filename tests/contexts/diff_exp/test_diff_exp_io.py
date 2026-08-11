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

"""Unit tests for DiffractionExperimentIo."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from unittest.mock import MagicMock

import pytest

from pydidas.contexts.diff_exp import (
    DiffractionExperiment,
    DiffractionExperimentContext,
    DiffractionExperimentIo,
    DiffractionExperimentIoBase,
)


EXP = DiffractionExperimentContext()


@pytest.fixture()
def mock_io_class():
    """
    Create a mock IO class for testing DiffractionExperimentIo registry.

    Yields a MagicMock with export_to_file and import_from_file methods.
    """
    _mock_cls = MagicMock(spec=DiffractionExperimentIoBase)
    _mock_cls.extensions = [".test"]
    _mock_cls.format_name = "Test"
    _mock_cls.export_to_file = MagicMock()
    _mock_cls.import_from_file = MagicMock()
    return _mock_cls


@pytest.fixture(autouse=True)
def registry_with_mock(mock_io_class):
    """
    Set up and tear down the registry with mock IO class.

    Saves the original registry, clears it, registers the mock class,
    then restores the original registry after tests complete.
    """
    _original_registry = DiffractionExperimentIo.registry.copy()
    DiffractionExperimentIo.clear_registry()
    DiffractionExperimentIo.register_class(mock_io_class)
    yield
    DiffractionExperimentIo.registry = _original_registry


@pytest.fixture(autouse=True)
def reset_mocks_and_context(mock_io_class):
    """
    Reset mock calls and global context before each test.

    Depends on registry_with_mock to ensure registry is initialized.
    """
    mock_io_class.export_to_file.reset_mock()
    mock_io_class.import_from_file.reset_mock()
    yield
    EXP.restore_all_defaults(True)


def test_export_to_file(mock_io_class):
    _fname = "test.test"
    DiffractionExperimentIo.export_to_file(_fname)
    mock_io_class.export_to_file.assert_called_once()
    _call_args, _call_kwargs = mock_io_class.export_to_file.call_args
    assert _call_args[0] == _fname


def test_import_from_file__generic(mock_io_class):
    _fname = "test.test"
    DiffractionExperimentIo.import_from_file(_fname)
    mock_io_class.import_from_file.assert_called_once()
    _call_args, _call_kwargs = mock_io_class.import_from_file.call_args
    assert _call_args[0] == _fname
    assert _call_kwargs.get("diffraction_exp") is None


def test_import_from_file__given_exp(mock_io_class):
    _exp = DiffractionExperiment()
    _fname = "test.test"
    DiffractionExperimentIo.import_from_file(_fname, diffraction_exp=_exp)
    mock_io_class.import_from_file.assert_called_once()
    _call_args, _call_kwargs = mock_io_class.import_from_file.call_args
    assert _call_args[0] == _fname
    assert _call_kwargs.get("diffraction_exp") is _exp


if __name__ == "__main__":
    pytest.main([__file__])

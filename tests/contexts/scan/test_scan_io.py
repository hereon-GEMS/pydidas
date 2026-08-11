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
from unittest.mock import MagicMock, Mock

import pytest

from pydidas.contexts.scan import Scan, ScanContext, ScanIo
from pydidas.core import UserConfigError


SCAN = ScanContext()


@pytest.fixture(autouse=True)
def clean_scan_io_registry():
    """Fixture to clean the ScanIo registry before running tests."""
    original_registry = ScanIo.registry.copy()
    original_bl_format_registry = ScanIo.beamline_format_registry.copy()
    ScanIo.clear_registry()
    yield
    ScanIo.registry = original_registry
    ScanIo.beamline_format_registry = original_bl_format_registry


@pytest.fixture
def mock_io():
    """Fixture to create a mock IO class."""
    mock_class = MagicMock()
    mock_class.extensions = [".test"]
    mock_class.format_name = "Test"
    mock_class.beamline_format = False
    mock_class.import_only = False
    mock_class.export_to_file = MagicMock()
    mock_class.import_from_file = MagicMock()
    mock_class.import_from_file_sequence = MagicMock()
    mock_class.check_file_list = MagicMock(return_value=["::no_error::"])
    return mock_class


@pytest.fixture
def mock_bl_io():
    """Fixture to create a mock beamline IO class."""
    mock_class = MagicMock()
    mock_class.extensions = [".bl_test"]
    mock_class.format_name = "Beamline Test"
    mock_class.beamline_format = True
    mock_class.import_only = True
    mock_class.export_to_file = MagicMock()
    mock_class.import_from_file = MagicMock()
    mock_class.import_from_file_sequence = MagicMock()
    mock_class.check_file_list = MagicMock(return_value=["::no_error::"])
    return mock_class


def test_clear_registry():
    ScanIo.registry[".test"] = Mock()
    ScanIo.beamline_format_registry[".bl_test"] = Mock()
    ScanIo.clear_registry()
    assert ScanIo.registry == {}
    assert ScanIo.beamline_format_registry == {}


def test_is_extension_registered(mock_io, mock_bl_io, clean_scan_io_registry):
    ScanIo.beamline_format_registry[".test"] = mock_io
    ScanIo.beamline_format_registry[".bl_test"] = mock_bl_io
    assert ScanIo.is_extension_registered(".test")
    assert ScanIo.is_extension_registered(".bl_test")


def test_is_extension_registered__wrong_class():
    assert not ScanIo.is_extension_registered("dummy")


def test_export_to_file(mock_io):
    ScanIo.registry[".test"] = mock_io
    _fname = Path("test.test")
    ScanIo.export_to_file(_fname, some_kwarg="value")
    mock_io.export_to_file.assert_called_once_with(_fname, some_kwarg="value")


def test_export_to_file__w_bl_format(mock_bl_io):
    mock_bl_io.import_only = False
    ScanIo.beamline_format_registry[".bl_test"] = mock_bl_io
    _fname = Path("test.bl_test")
    ScanIo.export_to_file(_fname)
    mock_bl_io.export_to_file.assert_called_once_with(_fname)


def test_export_to_file__import_only_class(mock_io):
    mock_io.import_only = True
    ScanIo.registry[".test"] = mock_io
    _fname = Path("test.test")
    with pytest.raises(UserConfigError):
        ScanIo.export_to_file(_fname)


def test_import_from_file__generic_scan_context(mock_io):
    ScanIo.registry[".test"] = mock_io
    _fname = Path("test.test")
    ScanIo.import_from_file(_fname)
    mock_io.import_from_file.assert_called_once_with(_fname, scan=None)


def test_import_from_file__given_scan(mock_io):
    ScanIo.registry[".test"] = mock_io
    _fname = Path("test.test")
    _scan = Scan()
    ScanIo.import_from_file(_fname, scan=_scan)
    mock_io.import_from_file.assert_called_once_with(_fname, scan=_scan)


def test_import_from_file_sequence(mock_io):
    ScanIo.registry[".test"] = mock_io
    _fnames = [Path(f"test_{i}.test") for i in range(5)]
    ScanIo.import_from_file_sequence(_fnames, some_kwarg="value")
    mock_io.import_from_file_sequence.assert_called_once_with(
        _fnames, some_kwarg="value"
    )


def test_import_from_file_sequence__w_different_extensions(mock_io):
    ScanIo.registry[".test"] = mock_io
    _fnames = [Path("test1.test"), Path("test2.bl_test")]
    with pytest.raises(UserConfigError):
        ScanIo.import_from_file_sequence(_fnames)


def test_get_string_of_beamline_formats(mock_io, mock_bl_io):
    ScanIo.registry[".test"] = mock_io
    ScanIo.beamline_format_registry[".bl_test"] = mock_bl_io
    _str = ScanIo.get_string_of_beamline_formats()
    assert "*.bl_test" in _str
    assert "Beamline Test" in _str
    assert "*.test" not in _str


def test_register_class__w_existing_entry(mock_io):
    ScanIo.registry[".test"] = Mock()
    with pytest.raises(KeyError):
        ScanIo.register_class(mock_io)


def test_register_class__w_update_and_existing_entry(mock_io):
    ScanIo.registry[".test"] = Mock()
    ScanIo.register_class(mock_io, update_registry=True)
    assert ScanIo.registry[".test"] == mock_io


def test_get_io_class__w_bl_format(mock_io, mock_bl_io):
    ScanIo.registry[".test"] = mock_io
    ScanIo.beamline_format_registry[".bl_test"] = mock_bl_io
    _io_class = ScanIo.get_io_class("test.bl_test")
    assert _io_class == mock_bl_io


def test_get_io_class__w_standard_format(mock_io):
    ScanIo.registry[".test"] = mock_io
    _io_class = ScanIo.get_io_class("test.test")
    assert _io_class == mock_io


def test_check_multiple_files(mock_io):
    ScanIo.registry[".test"] = mock_io
    _fnames = [Path("test1.test"), Path("test2.test")]
    _check = ScanIo.check_multiple_files(_fnames, some_kwarg="value")
    assert _check == ["::no_error::"]
    mock_io.check_file_list.assert_called_once_with(_fnames, some_kwarg="value")


def test_check_multiple_files__w_different_extensions(mock_io):
    ScanIo.registry[".test"] = mock_io
    _fnames = [Path("test1.test"), Path("test2.bl_test")]
    with pytest.raises(UserConfigError):
        ScanIo.check_multiple_files(_fnames)  # type: ignore[arg-type]


def test_get_string_of_formats__inherited_from_meta(mock_io):
    ScanIo.registry[".test"] = mock_io
    _str = ScanIo.get_string_of_formats()
    assert "*.test" in _str
    assert "Test" in _str
    assert "All supported files" in _str


if __name__ == "__main__":
    pytest.main([__file__])

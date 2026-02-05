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


import shutil
import tempfile
from pathlib import Path
from typing import Any

import pytest

from pydidas.contexts.scan import Scan, ScanContext, ScanIo, ScanIoBase
from pydidas.core import UserConfigError


SCAN = ScanContext()


def export_to_file(cls, filename, **kwargs):
    cls.exported = True
    cls.export_filename = filename


def import_from_file(cls, filename, scan=None, **kwargs):
    cls.imported = True
    cls.scan = SCAN if scan is None else scan
    cls.import_filename = filename


def create_test_class(
    class_name: str = None,
    extensions: list[str] = None,
    format_name=None,
    **kwargs: Any,
) -> type:
    _class = type(
        "TestIo" if class_name is None else class_name,
        (ScanIoBase,),
        {
            "imported": False,
            "exported": False,
            "export_filename": None,
            "import_filename": None,
            "export_to_file": classmethod(export_to_file),
            "import_from_file": classmethod(import_from_file),
            "extensions": extensions if extensions is not None else [".test"],
            "format_name": format_name if format_name is not None else "Test",
        }
        | kwargs,
    )
    return _class


def create_bl_test_class(
    class_name: str = None, extensions: list[str] = None, format_name=None
) -> type:
    _class = create_test_class(
        "TestIoBeamline" if class_name is None else class_name,
        extensions=extensions if extensions is not None else [".bl_test"],
        format_name=format_name if format_name is not None else "Beamline Test",
        beamline_format=True,
        import_only=True,
    )
    return _class


@pytest.fixture
def clean_scan_io_registry():
    """Fixture to clean the ScanIo registry before running tests."""
    original_registry = ScanIo.registry.copy()
    original_bl_format_registry = ScanIo.beamline_format_registry.copy()
    ScanIo.clear_registry()
    yield
    ScanIo.registry = original_registry
    ScanIo.beamline_format_registry = original_bl_format_registry


@pytest.fixture(scope="module")
def temp_path():
    """Fixture to create a temporary directory."""
    _temp_dir = Path(tempfile.mkdtemp())
    yield _temp_dir
    shutil.rmtree(_temp_dir)


def test_clear_registry(clean_scan_io_registry):
    ScanIo.clear_registry()
    assert ScanIo.registry == {}
    assert ScanIo.beamline_format_registry == {}


@pytest.mark.parametrize(
    "format_key, _callable, input_ext",
    [
        ["test", create_test_class, None],
        ["bl_test", create_bl_test_class, None],
        ["test", create_test_class, "TEST"],
    ],
)
def test_is_extension_registered(
    format_key, _callable, input_ext, temp_path, clean_scan_io_registry
):
    if input_ext:
        _class = _callable(extensions=[input_ext])
    else:
        _class = _callable()
    if format_key == "bl_test":
        assert ".bl_test" in ScanIo.beamline_format_registry
    else:
        assert "." + format_key in ScanIo.registry
    assert ScanIo.is_extension_registered("." + format_key)


def test_is_extension_registered__false(clean_scan_io_registry):
    assert not ScanIo.is_extension_registered("dummy")


def test_export_to_file(temp_path, clean_scan_io_registry):
    _test_class = create_test_class()
    _fname = temp_path / "test.test"
    ScanIo.export_to_file(_fname)
    assert _test_class.exported
    assert _test_class.export_filename == _fname


def test_export_to_file__import_only_format(temp_path, clean_scan_io_registry):
    _test_class = create_test_class()

    _fname = temp_path / "test.test"
    ScanIo.export_to_file(_fname)
    assert _test_class.exported
    assert _test_class.export_filename == _fname


def test_export_to_file__bl_format(temp_path, clean_scan_io_registry):
    _test_class_bl_format = create_bl_test_class()
    _fname = temp_path / "test.bl_test"
    ScanIo.beamline_format_registry[".bl_test"].import_only = False
    ScanIo.export_to_file(_fname)
    assert _test_class_bl_format.exported
    assert _test_class_bl_format.export_filename == _fname


def test_export_to_file__import_only(temp_path, clean_scan_io_registry):
    _fname = temp_path / "test.test"
    _class = create_test_class()
    ScanIo.registry[".test"].import_only = True
    with pytest.raises(UserConfigError):
        ScanIo.export_to_file(_fname)


def test_import_from_file__generic_ScanContext(temp_path, clean_scan_io_registry):
    _test_class = create_test_class()
    _fname = temp_path / "test.test"
    ScanIo.import_from_file(_fname)
    assert _test_class.imported
    assert _test_class.import_filename == _fname
    assert _test_class.scan == SCAN


def test_import_from_file__given_Scan(temp_path, clean_scan_io_registry):
    _test_class = create_test_class()
    _fname = temp_path / "test.test"
    _scan = Scan()
    ScanIo.import_from_file(_fname, scan=_scan)
    assert _test_class.imported
    assert _test_class.import_filename == _fname
    assert _test_class.scan == _scan


def test_import_from_multiple_files(temp_path, clean_scan_io_registry):
    _test_class = create_test_class()
    _fnames = [temp_path / f"test_{i}.test" for i in range(5)]
    ScanIo.import_from_multiple_files(_fnames)
    assert _test_class.imported
    assert _test_class.import_filename == _fnames


def test_get_string_of_beamline_formats(clean_scan_io_registry):
    _test_class = create_test_class()
    _bl_test_class = create_bl_test_class()
    _str = ScanIo.get_string_of_beamline_formats()
    assert "*.bl_test" in _str
    assert "*.test" not in _str


def test_register_class__w_existing_entry(clean_scan_io_registry):
    ScanIo.registry[".test"] = 42
    with pytest.raises(KeyError):
        _class = create_test_class()


def test_register_class__w_update_and_existing_entry(clean_scan_io_registry):
    _class = create_test_class()
    ScanIo.registry[".test"] = "dummy"
    ScanIo.register_class(_class, update_registry=True)
    assert ScanIo.registry[".test"] == _class


def test_get_io_class__w_bl_format(clean_scan_io_registry):
    _class = create_test_class()
    _bl_class = create_bl_test_class()
    _io_class = ScanIo.get_io_class("test.bl_test")
    assert _io_class == _bl_class


def test_import_from_multiple_files__w_different_extensions(clean_scan_io_registry):
    _test_class = create_test_class()
    _fnames = ["test1.test", "test2.bl_test"]
    with pytest.raises(UserConfigError):
        ScanIo.import_from_multiple_files(_fnames)


def test_check_multiple_files__corrent(clean_scan_io_registry):
    _test_class = create_test_class()
    _fnames = ["test1.test", "test2.test"]
    _check = ScanIo.check_multiple_files(_fnames)
    assert _check == ["::no_error::"]


def test_check_multiple_files__w_different_extensions(clean_scan_io_registry):
    _test_class = create_test_class()
    _fnames = ["test1.test", "test2.bl_test"]
    with pytest.raises(UserConfigError):
        ScanIo.check_multiple_files(_fnames)


if __name__ == "__main__":
    pytest.main()

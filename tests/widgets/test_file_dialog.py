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

"""Unit tests for the FileDialog class."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import pytest

from pydidas.core import UserConfigError
from pydidas.widgets import PydidasFileDialog


@pytest.fixture
def file_dialog(qtbot):
    """
    Provide a PydidasFileDialog instance for testing.

    Parameters
    ----------
    qtbot
        The pytest-qt bot for testing Qt applications.

    Yields
    ------
    PydidasFileDialog
        A PydidasFileDialog instance with reset state.
    """
    dialog = PydidasFileDialog()
    dialog._calling_kwargs = {}
    yield dialog
    dialog.q_settings_remove("Test__import")
    dialog.q_settings_remove("Test__export")


def test_is_same_instance(qtbot) -> None:
    """Test that PydidasFileDialog is a singleton."""
    dialog1 = PydidasFileDialog()
    dialog2 = PydidasFileDialog()
    assert dialog1 is dialog2, "PydidasFileDialog should be a singleton."


@pytest.mark.parametrize("reference", [None, "test_ref"])
@pytest.mark.parametrize("qsettings_ref", [None, "Test__import"])
def test_store_calling_kwargs(file_dialog, reference, qsettings_ref) -> None:
    """Test storing calling kwargs with reference or qsettings_ref."""
    kwarg_dict = {"key1": "value1", "key2": "value2"}
    if reference is not None:
        kwarg_dict["reference"] = reference
    if qsettings_ref is not None:
        kwarg_dict["qsettings_ref"] = qsettings_ref
    if reference and qsettings_ref:
        with pytest.raises(UserConfigError):
            file_dialog._store_calling_kwargs(kwarg_dict)
    else:
        file_dialog._store_calling_kwargs(kwarg_dict)
        assert file_dialog._calling_kwargs == kwarg_dict


@pytest.mark.parametrize("qref", [None, "Test__import", "Test__export"])
@pytest.mark.parametrize("stored_entry", [None, "file"])
@pytest.mark.parametrize("reference", [None, "ref"])
@pytest.mark.parametrize("stored_dir", [None, "stored_dir"])
def test_get_stored_entries__with_qref(
    file_dialog, qref, stored_entry, reference, stored_dir
) -> None:
    """Test getting stored entries with various qref and reference settings."""
    file_dialog.q_settings_set("dialogues/Test__import", "entry_import")
    file_dialog.q_settings_set("dialogues/Test__export", "entry_export")
    file_dialog._stored_selections = {}
    file_dialog._calling_kwargs = {}
    file_dialog._stored_dirs = {}
    if qref is not None:
        file_dialog._calling_kwargs["qsettings_ref"] = qref
    if stored_entry is not None:
        file_dialog._stored_selections["dialogues/Test__import"] = stored_entry
        file_dialog._stored_selections["dialogues/Test__export"] = stored_entry
        file_dialog._stored_selections["ref"] = stored_entry
    if reference is not None:
        file_dialog._calling_kwargs["reference"] = reference
    if stored_dir is not None and reference is not None:
        file_dialog._stored_dirs[reference] = stored_dir
    _fname, _dir = file_dialog._get_stored_entries()
    if qref is not None:
        expected_dir = "entry_import" if qref == "Test__import" else "entry_export"
        assert _dir == expected_dir
        assert _fname == (stored_entry or "")
    elif reference is not None:
        assert _dir == stored_dir
        assert _fname == (stored_entry or "")
    else:
        assert _dir is None
        assert _fname == ""


@pytest.mark.parametrize("format1", ["Test1 (*.test1 *.t1)", None])
@pytest.mark.parametrize("format2", ["Test2 (*.test2 *.t2)", None])
def test_set_name_filter(file_dialog, format1, format2) -> None:
    """Test setting name filter with different format combinations."""
    _all_formats = [".test0", ".t0"]
    file_dialog._calling_kwargs = {}
    _format_str = "Test0 (*.test0 *.t0)"
    if format1 is not None:
        _format_str += f";;{format1}"
        _all_formats.extend([".test1", ".t1"])
    if format2 is not None:
        _format_str += f";;{format2}"
        _all_formats.extend([".test2", ".t2"])
    _format_str = (
        f"All supported files (*{' *'.join(_all_formats)})" + f";;{_format_str}"
    )
    file_dialog._calling_kwargs["formats"] = _format_str
    file_dialog._set_name_filter()
    assert set(_all_formats) == set(file_dialog._config["supported_extensions"])


def test_set_name_filter__no_formats(file_dialog) -> None:
    """Test setting name filter when no formats are provided."""
    file_dialog._calling_kwargs = {}
    file_dialog._set_name_filter()
    assert file_dialog._config["supported_extensions"] is None


@pytest.mark.parametrize("use_dir", [True, False])
@pytest.mark.parametrize("qref", [None, "Test__import"])
@pytest.mark.parametrize("ref", [None, "test__42"])
def test_store_current_directory(file_dialog, temp_path, use_dir, qref, ref) -> None:
    """Test storing the current directory with various settings."""
    if qref is not None and ref is not None:
        # the test is not valid if both qref and ref are set, because
        # this will raise a UserConfigError in _store_calling_kwargs
        return
    _test_dir = temp_path / "file_dialog_test"
    _fname = _test_dir / "test_file.txt"
    _test_dir.mkdir(parents=True, exist_ok=True)
    with open(_fname, "w") as f:
        f.write("test")
    file_dialog._calling_kwargs["qsettings_ref"] = qref
    if ref is not None:
        file_dialog._calling_kwargs["reference"] = ref
    file_dialog.selectFile(str(_test_dir if use_dir else _fname))
    file_dialog._store_current_directory()
    assert file_dialog.q_settings_get("dialogues/current") == str(_test_dir)
    if qref is not None:
        assert file_dialog.q_settings_get(f"dialogues/{qref}") == str(_test_dir)
        assert file_dialog._stored_selections[f"dialogues/{qref}"] == (
            "file_dialog_test" if use_dir else "test_file.txt"
        )
    if ref is not None:
        assert file_dialog._stored_dirs[ref] == str(_test_dir)
        assert file_dialog._stored_selections[ref] == (
            "file_dialog_test" if use_dir else "test_file.txt"
        )


@pytest.mark.parametrize("use_default_suffix", [True, False])
@pytest.mark.parametrize("select_filter", [0, 1, 2, 3, 4, 5])
def test_get_extension(file_dialog, use_default_suffix, select_filter) -> None:
    """Test getting file extension based on selected filter."""
    _filters = [
        "All supported files (*.test0 *.t0 *.test *.t1 *.npy *.tif)",
        "Test0 (*.test0 *.t0)",
        "Test1 (*.test1 *.t1)",
        "Npy (*.npy)",
        "Tif (*.tif)",
        "None",
    ]
    _formats = ";;".join(_filters)
    file_dialog._calling_kwargs["formats"] = _formats
    if use_default_suffix:
        file_dialog._calling_kwargs["default_suffix"] = ".t0"
    file_dialog._set_name_filter()
    _selected_filter = _filters[select_filter]
    file_dialog.selectNameFilter(_selected_filter)
    _ext = file_dialog._get_extension()
    if _selected_filter == "None":
        assert _ext == ""
    elif use_default_suffix and ".t0" in _selected_filter:
        assert _ext == ".t0"
    elif ".npy" in _selected_filter:
        assert _ext == ".npy"
    elif ".tif" in _selected_filter:
        assert _ext == ".tif"
    else:
        assert _ext == _selected_filter.removesuffix(")").split("*")[1].strip()


if __name__ == "__main__":
    pytest.main([])

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

"""Unit tests for the Hdf5DatasetSelector widget."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"

import shutil
from pathlib import Path

import h5py
import numpy as np
import pytest
from qtpy import QtCore

from pydidas.core import Parameter
from pydidas.unittest_objects import SignalSpy
from pydidas.widgets.selection import Hdf5DatasetSelector


@pytest.fixture
def hdf5_test_file(temp_path: Path) -> Path:
    """Create a test HDF5 file with various datasets."""
    _filepath = temp_path / "hdf5_dataset_selector" / "test_data.h5"
    _filepath.parent.mkdir(parents=True, exist_ok=True)

    with h5py.File(_filepath, "w") as f:
        # Create flat datasets
        f.create_dataset("flat_1d", data=np.random.rand(10))
        f.create_dataset("flat_2d", data=np.random.rand(10, 10))
        f.create_dataset("flat_3d", data=np.random.rand(5, 10, 10))
        f.create_dataset("flat_4d", data=np.random.rand(5, 6, 7, 8))

        # Create entry/data structure (NeXus format)
        entry = f.create_group("entry")
        data_group = entry.create_group("data")
        data_group.create_dataset("data", data=np.random.rand(5, 10, 10))
        data_group.create_dataset("data_000001", data=np.random.rand(5, 10, 5, 5))

        # Create instrument/detector structure
        instrument = entry.create_group("instrument")
        detector = instrument.create_group("detector")
        detector.create_dataset("data", data=np.random.rand(5, 10, 10))
        detector.create_dataset("detector_mask", data=np.random.rand(10, 10))

        # Create NXdata group with signal attribute
        nxdata = entry.create_group("nx/data")
        nxdata.attrs["NX_class"] = "NXdata"
        nxdata.attrs["signal"] = "signal_data"
        nxdata.create_dataset("signal_data", data=np.random.rand(5, 10, 10))
        nxdata.create_dataset("auxiliary_data", data=np.random.rand(5, 10, 10))

        # Create deeply nested structure
        nested = f.create_group("nested")
        level1 = nested.create_group("level1")
        level2 = level1.create_group("level2")
        level2.create_dataset("deep_data", data=np.random.rand(5, 10))

    # Create a copy to test switching files
    shutil.copy(_filepath, _filepath.parent / "test_data_copy.h5")

    yield _filepath
    _filepath.unlink()


@pytest.fixture
def widget(qtbot, hdf5_test_file: Path) -> Hdf5DatasetSelector:
    """Create a Hdf5DatasetSelector widget instance."""
    widget = Hdf5DatasetSelector()
    widget.spy_sig_new_dataset_selected = SignalSpy(widget.sig_new_dataset_selected)
    widget.spy_sig_request_hdf5_browser = SignalSpy(widget.sig_request_hdf5_browser)
    widget.new_filename(hdf5_test_file)
    widget.show()
    qtbot.wait_until(lambda: widget.isVisible(), timeout=500)
    return widget


@pytest.mark.gui
def test_widget_creation() -> None:
    """Test that widget can be created."""
    widget = Hdf5DatasetSelector()
    assert isinstance(widget, Hdf5DatasetSelector)
    assert isinstance(widget.get_param("dataset"), Parameter)
    assert isinstance(widget.get_param("min_datadim"), Parameter)
    assert not widget.isVisible()
    assert widget._config["current_dataset"] == ""
    assert widget._config["current_filename"] == ""
    assert widget._config["min_datadim"] == 1
    assert widget._config["display_details"] is False
    assert hasattr(widget, "sig_new_dataset_selected")
    assert hasattr(widget, "sig_request_hdf5_browser")


@pytest.mark.gui
def test_new_filename(hdf5_test_file: Path) -> None:
    """Test setting a new filename."""
    widget = Hdf5DatasetSelector()
    widget.new_filename(str(hdf5_test_file))
    _choices = widget.get_param("dataset").choices
    assert widget.isVisible()
    assert widget._config["current_filename"] == str(hdf5_test_file)
    assert len(_choices) > 0
    assert _choices[0] == "/entry/data/data"  # Should be prioritized


@pytest.mark.gui
def test_new_filename___non_hdf5(widget: Hdf5DatasetSelector, temp_path: Path) -> None:
    """Test setting a non-HDF5 filename."""
    non_hdf5_file = temp_path / "test.txt"
    non_hdf5_file.write_text("test")
    widget.new_filename(str(non_hdf5_file))
    assert not widget.isVisible()


@pytest.mark.gui
def test_dataset_property(widget: Hdf5DatasetSelector, hdf5_test_file: Path) -> None:
    """Test the dataset property."""
    dataset = widget.dataset
    assert isinstance(dataset, str)


@pytest.mark.gui
def test_signal_on_dataset_selected(
    widget: Hdf5DatasetSelector, hdf5_test_file: Path
) -> None:
    """Test signal is emitted when dataset is selected."""
    widget.set_param_value("dataset", "/flat_3d")
    assert widget.spy_sig_new_dataset_selected.n == 1


@pytest.mark.gui
@pytest.mark.parametrize("ndim_filter", ["any", ">= 1", ">= 2", ">= 3", ">= 4"])
def test_min_dimension_filtering_any(
    widget: Hdf5DatasetSelector, hdf5_test_file: Path, ndim_filter: str
) -> None:
    widget.set_param_and_widget_value("min_datadim", ndim_filter)
    _choices = widget.get_param("dataset").choices
    assert len(_choices) > 0
    if ndim_filter in ["any", ">= 1"]:
        assert "/flat_1d" in _choices
    if ndim_filter in ["any", ">= 1", ">= 2"]:
        assert "/flat_2d" in _choices
    if ndim_filter in ["any", ">= 1", ">= 2", ">= 3"]:
        assert "/flat_3d" in _choices
    if ndim_filter in ["any", ">= 1", ">= 2", ">= 3", ">= 4"]:
        assert "/flat_4d" in _choices


@pytest.mark.gui
@pytest.mark.parametrize("nx_filter", [False, True])
def test_nxsignal_filtering(
    qtbot, widget: Hdf5DatasetSelector, hdf5_test_file: Path, nx_filter: bool
) -> None:
    """Test NXdata signal-only filtering."""
    # Get datasets with NXsignal filtering on
    widget._widgets["check_nxsignal"].setChecked(nx_filter)
    _choices = widget.get_param("dataset").choices
    assert "/entry/nx/data/signal_data" in _choices
    assert nx_filter == ("/entry/nx/data/auxiliary_data" not in _choices)


@pytest.mark.gui
def test_active_filters_property(widget: Hdf5DatasetSelector) -> None:
    """Test active_filters property."""
    filters = widget.active_filters
    assert isinstance(filters, list)


@pytest.mark.gui
def test_dset_filter_exceptions_property(widget: Hdf5DatasetSelector) -> None:
    """Test dset_filter_exceptions property."""
    exceptions = widget.dset_filter_exceptions
    assert isinstance(exceptions, list)


@pytest.mark.gui
def test_toggle_details_initially_hidden(widget: Hdf5DatasetSelector) -> None:
    """Test that filter container is initially hidden."""
    assert not widget._widgets["filter_container"].isVisible()


@pytest.mark.gui
def test__click_button_toggle_details(widget: Hdf5DatasetSelector, qtbot) -> None:
    """Test toggling details shows the filter container."""
    with qtbot.waitSignal(widget._widgets["button_toggle_details"].clicked):
        qtbot.mouseClick(
            widget._widgets["button_toggle_details"], QtCore.Qt.MouseButton.LeftButton
        )
    assert widget._widgets["filter_container"].isVisible()
    assert widget._config["display_details"] is True
    with qtbot.waitSignal(widget._widgets["button_toggle_details"].clicked):
        qtbot.mouseClick(
            widget._widgets["button_toggle_details"], QtCore.Qt.MouseButton.LeftButton
        )
    assert widget._config["display_details"] is False
    assert not widget._widgets["filter_container"].isVisible()


@pytest.mark.gui
def test_display_dataset_signal_not_emitted_on_same_dataset(
    widget: Hdf5DatasetSelector, hdf5_test_file: Path
) -> None:
    """Test that signal is not emitted when same dataset is selected."""
    _n0 = widget.spy_sig_new_dataset_selected.n
    current = widget.dataset
    widget.set_param_and_widget_value("dataset", current)
    # Count should not increase significantly
    assert widget.spy_sig_new_dataset_selected.n == _n0


@pytest.mark.gui
def test_clear(widget: Hdf5DatasetSelector, hdf5_test_file: Path) -> None:
    """Test that clear() resets the widget state."""
    assert widget.isVisible()
    assert widget._config["current_filename"] != ""
    widget.clear()
    assert not widget.isVisible()
    assert widget._config["current_dataset"] == ""
    assert widget._config["current_filename"] == ""


@pytest.mark.gui
def test_clear_on_empty_widget(widget: Hdf5DatasetSelector) -> None:
    """Test that clear() works on uninitialized widget."""
    widget.clear()
    assert not widget.isVisible()
    assert widget._config["current_dataset"] == ""


@pytest.mark.gui
def test_inspect_button_signal(qtbot, widget: Hdf5DatasetSelector) -> None:
    """Test that inspect button emits signal."""
    qtbot.mouseClick(
        widget._widgets["button_inspect"], QtCore.Qt.MouseButton.LeftButton
    )
    assert widget.spy_sig_request_hdf5_browser.n == 1


@pytest.mark.gui
def test_dataset_changed_signal(qtbot, widget: Hdf5DatasetSelector) -> None:
    """Test signal when dataset is changed."""
    _n0 = widget.spy_sig_new_dataset_selected.n
    with qtbot.waitSignal(widget.sig_new_dataset_selected, timeout=1000):
        widget.set_param_and_widget_value("dataset", "/flat_1d")
    assert widget.spy_sig_new_dataset_selected.n == _n0 + 1


@pytest.mark.gui
def test_empty_hdf5_file(temp_path: Path) -> None:
    """Test with empty HDF5 file."""
    empty_file = temp_path / "empty.h5"
    with h5py.File(empty_file, "w") as _:
        pass  # Create empty file

    widget = Hdf5DatasetSelector()
    widget.new_filename(str(empty_file))
    choices = widget.get_param("dataset").choices
    # Should have at least empty string
    assert len(choices) >= 1


@pytest.mark.gui
def test_hdf5_file_with_only_groups(temp_path: Path) -> None:
    """Test with HDF5 file containing only groups."""
    groups_file = temp_path / "groups.h5"
    with h5py.File(groups_file, "w") as f:
        f.create_group("group1")
        f.create_group("group1/subgroup")

    widget = Hdf5DatasetSelector()
    widget.new_filename(str(groups_file))
    choices = widget.get_param("dataset").choices
    # Should handle gracefully
    assert len(choices) >= 1


@pytest.mark.gui
def test_hdf5_file_with_scalars(widget: Hdf5DatasetSelector, temp_path: Path) -> None:
    """Test with HDF5 file containing scalar datasets."""
    scalar_file = temp_path / "scalars.h5"
    with h5py.File(scalar_file, "w") as f:
        f.create_dataset("scalar", data=42)

    widget.new_filename(scalar_file)
    widget.set_param_and_widget_value("min_datadim", "any")
    choices = widget.get_param("dataset").choices
    assert "/scalar" in choices


@pytest.mark.gui
def test_switching_between_files(widget: Hdf5DatasetSelector, temp_path: Path) -> None:
    """Test switching between different HDF5 files."""
    _file1 = temp_path / "file1.h5"
    with h5py.File(_file1, "w") as f:
        f.create_dataset("data_a", data=np.random.rand(10, 10))

    # Create second file
    _file2 = temp_path / "file2.h5"
    with h5py.File(_file2, "w") as f:
        f.create_dataset("data_b", data=np.random.rand(10, 10))

    # Load first file
    widget.new_filename(_file1)
    assert "/data_a" in widget.get_param("dataset").choices

    # Switch to second file
    widget.new_filename(_file2)
    _new_choices = widget.get_param("dataset").choices
    assert "/data_b" in _new_choices
    assert "/data_a" not in _new_choices


@pytest.mark.gui
def test_non_existent_file(widget: Hdf5DatasetSelector, temp_path: Path) -> None:
    """Test with non-existent file."""
    non_existent = temp_path / "does_not_exist.h5"
    # Should not raise, just handle gracefully
    widget.new_filename(non_existent)


@pytest.mark.gui
def test_nxsignal_with_other_filters(
    qtbot, widget: Hdf5DatasetSelector, hdf5_test_file: Path
) -> None:
    """Test NXsignal filtering combined with dimension filtering."""
    widget._widgets["check_nxsignal"].setChecked(True)
    with qtbot.waitSignal(
        widget.param_composite_widgets["min_datadim"].sig_value_changed, timeout=1000
    ):
        widget.set_param_and_widget_value("min_datadim", ">= 4")
    _choices = widget.get_param("dataset").choices
    assert "/entry/nx/data/signal_data" not in _choices


if __name__ == "__main__":
    pytest.main([__file__])

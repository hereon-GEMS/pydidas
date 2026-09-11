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

"""Unit tests for the SelectDataFrameDialog."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from collections.abc import Generator
from pathlib import Path
from unittest.mock import patch

import h5py
import numpy as np
import pytest
from qtpy import QtWidgets

from pydidas.core import Dataset, FileReadError
from pydidas.widgets.dialogues.select_data_frame_dialog import SelectDataFrameDialog
from pydidas.widgets.selection import SelectDataFrameWidget
from pydidas.widgets.silx_plot import PydidasPlot2D
from pydidas_qtcore import PydidasQApplication


_DATA_2D = np.arange(30, dtype=np.float32).reshape(5, 6)
_DATA_3D = np.ones((4, 5, 6), dtype=np.float32)


@pytest.fixture(scope="module")
def path_w_data_files(temp_path: Path) -> Path:
    """Create a directory with test data files for the dialog tests."""
    _path = temp_path / "select_data_frame_dialog"
    _path.mkdir(exist_ok=True)
    np.save(_path / "data_2d.npy", _DATA_2D)
    with h5py.File(_path / "data.h5", "w") as f:
        f["/entry/data/2d"] = _DATA_2D
        f["/entry/data/3d"] = _DATA_3D
    return _path


@pytest.fixture(autouse=True)
def _cleanup() -> Generator[None, None, None]:
    """Close any SelectDataFrameDialog instances after each test."""
    app = PydidasQApplication.instance()
    yield
    for widget in [
        w for w in app.topLevelWidgets() if isinstance(w, SelectDataFrameDialog)
    ]:
        widget.close()
        widget.deleteLater()
    app.processEvents()


@pytest.fixture
def dialog(qtbot) -> SelectDataFrameDialog:
    """Create and show a default SelectDataFrameDialog."""
    _dialog = SelectDataFrameDialog()
    qtbot.add_widget(_dialog)
    _dialog.show()
    qtbot.wait_until(lambda: _dialog.isVisible(), timeout=500)
    return _dialog


@pytest.mark.gui
def test__creation(dialog) -> None:
    assert isinstance(dialog, SelectDataFrameDialog)
    assert isinstance(dialog._widgets["selector"], SelectDataFrameWidget)
    assert isinstance(dialog._widgets["plot"], PydidasPlot2D)
    assert isinstance(dialog._widgets["but_confirm"], QtWidgets.QPushButton)
    assert isinstance(dialog._widgets["but_abort"], QtWidgets.QPushButton)


@pytest.mark.gui
def test__creation__confirm_button_initially_disabled(dialog) -> None:
    assert not dialog._widgets["but_confirm"].isEnabled()


@pytest.mark.gui
def test__selected_frame__initially_none(dialog) -> None:
    assert dialog.selected_frame is None


@pytest.mark.gui
def test__creation__with_filename(qtbot, path_w_data_files) -> None:
    _fname = path_w_data_files / "data_2d.npy"
    with patch(
        "pydidas.widgets.dialogues.select_data_frame_dialog.import_data",
        return_value=Dataset(_DATA_2D),
    ):
        _dialog = SelectDataFrameDialog(filename=_fname)
    qtbot.add_widget(_dialog)
    assert (
        not _dialog._widgets["selector"].param_composite_widgets["filename"].isVisible()
    )


@pytest.mark.gui
def test__process_file_validity__enables_confirm(dialog) -> None:
    assert not dialog._widgets["but_confirm"].isEnabled()
    dialog._process_file_validity(True)
    assert dialog._widgets["but_confirm"].isEnabled()


@pytest.mark.gui
def test__process_file_validity__disables_confirm(dialog) -> None:
    dialog._process_file_validity(True)
    assert dialog._widgets["but_confirm"].isEnabled()
    dialog._process_file_validity(False)
    assert not dialog._widgets["but_confirm"].isEnabled()


@pytest.mark.gui
def test__process_file_validity__false_clears_selected_frame(dialog) -> None:
    dialog._selected_frame = Dataset(_DATA_2D)
    dialog._process_file_validity(False)
    assert dialog.selected_frame is None


@pytest.mark.gui
def test__load_and_display__stores_dataset(dialog) -> None:
    _data = Dataset(_DATA_2D)
    with patch(
        "pydidas.widgets.dialogues.select_data_frame_dialog.import_data",
        return_value=_data,
    ):
        dialog._load_and_display("some_file.npy", {})
    assert dialog.selected_frame is _data


@pytest.mark.gui
def test__load_and_display__calls_plot(dialog) -> None:
    _data = Dataset(_DATA_2D)
    with (
        patch(
            "pydidas.widgets.dialogues.select_data_frame_dialog.import_data",
            return_value=_data,
        ),
        patch.object(dialog._widgets["plot"], "plot_pydidas_dataset") as mock_plot,
    ):
        dialog._load_and_display("some_file.npy", {})
    mock_plot.assert_called_once_with(_data)


@pytest.mark.gui
def test__load_and_display__passes_config_to_import(dialog) -> None:
    _data = Dataset(_DATA_2D)
    _config = {"dataset": "/entry/data/2d", "indices": (0,)}
    with patch(
        "pydidas.widgets.dialogues.select_data_frame_dialog.import_data",
        return_value=_data,
    ) as mock_import:
        dialog._load_and_display("file.h5", _config)
    mock_import.assert_called_once_with("file.h5", **_config)


@pytest.mark.gui
def test__load_and_display__on_file_read_error__clears_frame(dialog) -> None:
    dialog._selected_frame = Dataset(_DATA_2D)
    with (
        patch(
            "pydidas.widgets.dialogues.select_data_frame_dialog.import_data",
            side_effect=FileReadError("read error"),
        ),
        pytest.raises(FileReadError),
    ):
        dialog._load_and_display("bad_file.npy", {})
    assert dialog.selected_frame is None


@pytest.mark.gui
def test__load_and_display__on_file_read_error__clears_plot(dialog) -> None:
    with (
        patch(
            "pydidas.widgets.dialogues.select_data_frame_dialog.import_data",
            side_effect=FileReadError("read error"),
        ),
        patch.object(dialog._widgets["plot"], "clear") as mock_clear,
        pytest.raises(FileReadError),
    ):
        dialog._load_and_display("bad_file.npy", {})
    mock_clear.assert_called_once()


@pytest.mark.gui
def test__confirm__accepts_dialog(qtbot, dialog) -> None:
    with qtbot.waitSignal(dialog.accepted, timeout=1000):
        dialog._confirm()


@pytest.mark.gui
def test__confirm__button_click_accepts_dialog(qtbot, dialog) -> None:
    dialog._widgets["but_confirm"].setEnabled(True)
    with qtbot.waitSignal(dialog.accepted, timeout=1000):
        dialog._widgets["but_confirm"].click()


@pytest.mark.gui
def test__abort__rejects_dialog(qtbot, dialog) -> None:
    with qtbot.waitSignal(dialog.rejected, timeout=1000):
        dialog._widgets["but_abort"].click()


@pytest.mark.gui
def test__abort__selected_frame_remains_none(qtbot, dialog) -> None:
    with qtbot.waitSignal(dialog.rejected, timeout=1000):
        dialog._widgets["but_abort"].click()
    assert dialog.selected_frame is None


@pytest.mark.gui
def test__selected_frame__returns_last_loaded_after_confirm(qtbot, dialog) -> None:
    _data = Dataset(_DATA_2D)
    with patch(
        "pydidas.widgets.dialogues.select_data_frame_dialog.import_data",
        return_value=_data,
    ):
        dialog._load_and_display("file.npy", {})
    with qtbot.waitSignal(dialog.accepted, timeout=1000):
        dialog._confirm()
    assert dialog.selected_frame is _data


@pytest.mark.gui
def test__sig_new_selection__triggers_load_and_display(dialog) -> None:
    _data = Dataset(_DATA_2D)
    with patch(
        "pydidas.widgets.dialogues.select_data_frame_dialog.import_data",
        return_value=_data,
    ):
        dialog._widgets["selector"].sig_new_selection.emit("file.npy", {})
    assert dialog.selected_frame is _data


@pytest.mark.gui
def test__sig_file_valid__true__enables_confirm(dialog) -> None:
    dialog._widgets["selector"].sig_file_valid.emit(True)
    assert dialog._widgets["but_confirm"].isEnabled()


@pytest.mark.gui
def test__sig_file_valid__false__disables_confirm(dialog) -> None:
    dialog._widgets["selector"].sig_file_valid.emit(True)
    dialog._widgets["selector"].sig_file_valid.emit(False)
    assert not dialog._widgets["but_confirm"].isEnabled()


@pytest.mark.gui
def test__get_frame__returns_dataset_on_accept(qtbot) -> None:
    _data = Dataset(_DATA_2D)
    with (
        patch.object(
            SelectDataFrameDialog,
            "exec_",
            return_value=QtWidgets.QDialog.Accepted,
        ),
        patch.object(
            SelectDataFrameDialog,
            "selected_frame",
            new_callable=lambda: property(lambda self: _data),
        ),
    ):
        result = SelectDataFrameDialog.get_frame()
    assert result is _data


@pytest.mark.gui
def test__get_frame__returns_none_on_reject(qtbot) -> None:
    with patch.object(
        SelectDataFrameDialog,
        "exec_",
        return_value=QtWidgets.QDialog.Rejected,
    ):
        result = SelectDataFrameDialog.get_frame()
    assert result is None


@pytest.mark.gui
def test__load_and_display__real_npy_file(dialog, path_w_data_files) -> None:
    _fname = str(path_w_data_files / "data_2d.npy")
    dialog._load_and_display(_fname, {})
    assert dialog.selected_frame is not None
    assert isinstance(dialog.selected_frame, Dataset)
    assert dialog.selected_frame.shape == _DATA_2D.shape


@pytest.mark.gui
def test__load_and_display__real_hdf5_file(dialog, path_w_data_files) -> None:
    _fname = str(path_w_data_files / "data.h5")
    _config = {"dataset": "/entry/data/2d", "indices": None}
    dialog._load_and_display(_fname, _config)
    assert dialog.selected_frame is not None
    assert dialog.selected_frame.shape == _DATA_2D.shape


if __name__ == "__main__":
    pytest.main([__file__])

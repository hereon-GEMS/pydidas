# This file is part of pydidas.
#
# Copyright 2025, Helmholtz-Zentrum Hereon
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

"""Module with pydidas unittests"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"

import warnings
from pathlib import Path
from unittest.mock import patch

import h5py
import numpy as np
import pytest
from qtpy import QtCore
from skimage.io import imsave

from pydidas.core import UserConfigError
from pydidas.unittest_objects import SignalSpy
from pydidas.widgets.misc.select_data_frame_widget import SelectDataFrameWidget
from pydidas_qtcore import PydidasQApplication


_VALID_FILENAMES = ["hdf5_file.h5", "tif_file.tiff", "npy_file.npy"]
_FILENAMES = _VALID_FILENAMES + ["invalid.tif"]
_USER_CONFIG_ERROR_METHOD = (
    "pydidas.widgets.misc.select_data_frame_widget."
    "SelectDataFrameWidget.raise_UserConfigError"
)
_VALID_KEYS = sorted(
    [
        "/entry/data/2d/data1",
        "/entry2/dataset/2d/data2",
        "/entry/data/3d_dataset_1",
        "/entry2/dataset/3d_dataset_2",
    ]
)


@pytest.fixture(scope="module")
def test_data():
    _3d_data_1 = np.arange(4).reshape(4, 1, 1) * np.ones((1, 5, 6), dtype=int)
    _3d_data_2 = np.arange(6).reshape(1, 6, 1) * np.ones((5, 1, 7), dtype=int)
    return {
        "/entry/data/2d/data1": np.arange(30).reshape(5, 6),
        "/entry2/dataset/2d/data2": np.arange(42).reshape(6, 7),
        "/entry/data/3d_dataset_1": _3d_data_1,
        "/entry2/dataset/3d_dataset_2": _3d_data_2,
        "/entry2/data/4d_dataset": np.arange(120).reshape(2, 3, 4, 5),
        "/entry/data/5d_data": np.arange(240).reshape(2, 3, 4, 5, 2),
    }


@pytest.fixture(scope="module", autouse=True)
def _cleanup():
    yield
    app = PydidasQApplication.instance()
    for widget in [
        _w for _w in app.topLevelWidgets() if isinstance(_w, SelectDataFrameWidget)
    ]:
        widget.deleteLater()
    app.processEvents()


@pytest.fixture(scope="module")
def path_w_data_files(temp_path, test_data):
    _path = temp_path / "select_data_frame_widget_files"
    _path.mkdir()
    with h5py.File(_path / "hdf5_file.h5", "w") as f:
        for _dataset_path, _data in test_data.items():
            f[_dataset_path] = _data
    with h5py.File(_path / "empty_hdf5_file.h5", "w") as f:
        pass
    np.save(_path / "npy_file.npy", test_data["/entry/data/2d/data1"])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        imsave(
            _path / "tif_file.tiff", test_data["/entry/data/2d/data1"].astype(np.uint16)
        )
    yield _path


@pytest.fixture
def widget(qtbot):
    widget = SelectDataFrameWidget()
    widget.spy_sig_file_valid = SignalSpy(widget.sig_file_valid)
    widget.spy_sig_new_selection = SignalSpy(widget.sig_new_selection)
    qtbot.add_widget(widget)
    widget.show()
    qtbot.wait_until(lambda: widget.isVisible(), timeout=500)
    return widget


def assert_correct_widget_visibility(widget):
    assert widget.isVisible()
    assert widget.param_composite_widgets["filename"].isVisible()
    assert (
        widget.param_composite_widgets["hdf5_key_str"].isVisible() == widget.hdf5_file
    )
    _slicing_vis = widget.hdf5_file and widget._selection.axis is not None
    assert widget.param_composite_widgets["slicing_axis"].isVisible() == _slicing_vis
    assert widget._widgets["index_selector"].isVisible() == _slicing_vis
    for _key in ["raw_datatype", "raw_n_x", "raw_n_y", "raw_header"]:
        assert widget.param_composite_widgets[_key].isVisible() == widget.binary_file


@pytest.mark.gui
def test__creation(widget):
    assert isinstance(widget, SelectDataFrameWidget)
    assert widget.get_param_value("filename", dtype=str) == "."
    assert_correct_widget_visibility(widget)


@pytest.mark.gui
@pytest.mark.parametrize("filename", _FILENAMES)
@pytest.mark.parametrize("dtype", [str, Path])
def test_process_new_filename(qtbot, widget, path_w_data_files, filename, dtype):
    widget.set_param_and_widget_value(
        "filename", dtype(path_w_data_files / filename), emit_signal=False
    )
    if filename == "invalid.tif":
        with pytest.raises(UserConfigError):
            widget.process_new_filename()
    else:
        with qtbot.waitSignal(widget.sig_file_valid, timeout=1000):
            widget.process_new_filename()
    qtbot.wait(5)  # ensure signal processing
    assert_correct_widget_visibility(widget)
    assert widget.spy_sig_file_valid.n == 1
    assert widget.spy_sig_file_valid.results[0] == [filename != "invalid.tif"]
    assert widget.spy_sig_new_selection.n == (filename != "invalid.tif")


@pytest.mark.gui
@pytest.mark.parametrize("filename", _VALID_FILENAMES)
def test__select_file(qtbot, widget, path_w_data_files, test_data, filename):
    _fname_widget = widget.param_composite_widgets["filename"]
    with (
        qtbot.waitSignal(_fname_widget.sig_new_value, timeout=1000),
        qtbot.waitSignal(_fname_widget.sig_value_changed, timeout=1000),
    ):
        widget.set_param_and_widget_value("filename", path_w_data_files / filename)
    qtbot.wait(5)  # ensure signal processing
    assert_correct_widget_visibility(widget)
    assert widget.spy_sig_file_valid.n == 1
    assert widget.spy_sig_file_valid.results[0] == [True]
    assert widget.spy_sig_new_selection.n == 1
    assert widget.spy_sig_new_selection.results[0][0] == str(
        path_w_data_files / filename
    )
    if filename == "hdf5_file.h5":
        for _key, _data in test_data.items():
            _included = _data.ndim <= 3
            assert (_key in widget.params["hdf5_key_str"].choices) == _included
            assert (
                _key
                in widget.param_composite_widgets[
                    "hdf5_key_str"
                ].io_widget.current_choices
            ) == _included


@pytest.mark.gui
def test__select_invalid_file(widget, path_w_data_files):
    widget.set_param_value("filename", path_w_data_files / "invalid.txt")
    with patch(_USER_CONFIG_ERROR_METHOD) as mock_error:
        widget.param_composite_widgets["filename"].set_value(
            widget.get_param_value("filename")
        )
    mock_error.assert_called_once()
    assert_correct_widget_visibility(widget)


@pytest.mark.gui
def test__select_empty_h5file(widget, path_w_data_files):
    widget.set_param_value("filename", path_w_data_files / "empty_hdf5_file.h5")
    with pytest.raises(UserConfigError):
        widget.process_new_filename()
    assert widget.param_composite_widgets["filename"].isVisible()
    assert not widget.param_composite_widgets["hdf5_key_str"].isVisible()
    assert not widget.param_composite_widgets["slicing_axis"].isVisible()
    assert not widget._widgets["index_selector"].isVisible()


@pytest.mark.gui
def test__select_h5file_with_same_dsets(qtbot, widget, path_w_data_files):
    widget.set_param_and_widget_value_and_choices(
        "hdf5_key_str", _VALID_KEYS[0], _VALID_KEYS, emit_signal=False
    )
    with qtbot.waitSignal(widget.sig_new_selection, timeout=1000):
        widget.set_param_and_widget_value(
            "filename", path_w_data_files / "hdf5_file.h5"
        )
    assert_correct_widget_visibility(widget)
    assert (
        widget.param_composite_widgets["hdf5_key_str"].display_value == _VALID_KEYS[0]
    )


@pytest.mark.gui
def test__select_h5_2d_dset_after_3d(widget, path_w_data_files):
    widget.set_param_and_widget_value("filename", path_w_data_files / "hdf5_file.h5")
    widget.set_param_and_widget_value("hdf5_key_str", "/entry/data/3d_dataset_1")
    widget.set_param_and_widget_value("hdf5_key_str", "/entry/data/2d/data1")
    assert_correct_widget_visibility(widget)
    assert (
        widget.param_composite_widgets["hdf5_key_str"].display_value
        == "/entry/data/2d/data1"
    )
    assert widget._selection.axis is None


@pytest.mark.gui
@pytest.mark.parametrize("dataset", _VALID_KEYS)
@pytest.mark.parametrize("emulate_gui", [True, False])
def test__select_hdf5_dset(
    qtbot, widget, test_data, path_w_data_files, dataset, emulate_gui
):
    _data_dim = test_data[dataset].ndim
    widget.set_param_and_widget_value("filename", path_w_data_files / "hdf5_file.h5")
    # ensure that the dataset is not currently selected
    _current_dset = widget.param_composite_widgets["hdf5_key_str"].display_value
    if _current_dset == dataset:
        _new_key = _VALID_KEYS[1] if dataset == _VALID_KEYS[0] else _VALID_KEYS[0]
        widget.set_param_and_widget_value("hdf5_key_str", _new_key, emit_signal=False)
        _current_dset = _new_key
    # A single selection signal should have been emitted for the file selection
    assert widget.spy_sig_file_valid.n == 1
    assert widget.spy_sig_new_selection.n == 1
    if emulate_gui:
        _io_widget = widget.param_composite_widgets["hdf5_key_str"].io_widget
        _new_index = _io_widget.current_choices.index(dataset)
        with qtbot.waitSignal(widget.sig_new_selection, timeout=1000):
            qtbot.mouseClick(_io_widget, QtCore.Qt.LeftButton)
            _io_widget.setCurrentIndex(_new_index)
    else:
        with qtbot.waitSignal(widget.sig_new_selection, timeout=1000):
            widget.set_param_and_widget_value("hdf5_key_str", dataset)
    assert widget.spy_sig_new_selection.n == 2
    assert widget.spy_sig_new_selection.results[1][1]["dataset"] == dataset
    assert widget.param_composite_widgets["slicing_axis"].isVisible() == (_data_dim > 2)
    assert widget._widgets["index_selector"].isVisible() == (_data_dim > 2)


@pytest.mark.gui
@pytest.mark.parametrize("axis", [0, 1, 2])
def test__select_slicing_axis(qtbot, widget, path_w_data_files, axis):
    widget.set_param_and_widget_value("filename", path_w_data_files / "hdf5_file.h5")
    widget.set_param_and_widget_value("hdf5_key_str", "/entry/data/3d_dataset_1")
    _io_widget = widget.param_composite_widgets["slicing_axis"].io_widget
    _expected_result = (None,) * axis + (
        widget._widgets["index_selector"].current_slice.start,
    )
    if _io_widget.current_text == str(axis):
        _new_axis = 1 if axis == 0 else 0
        widget.set_param_and_widget_value("slicing_axis", _new_axis, emit_signal=False)
    assert _io_widget.current_text != str(axis)
    # 2 signals should have been emitted for file and dataset selection
    assert widget.spy_sig_new_selection.n == 2
    with qtbot.waitSignal(widget.sig_new_selection, timeout=1000):
        _io_widget.setCurrentIndex(axis)
    assert widget.spy_sig_new_selection.n == 3
    assert widget.spy_sig_new_selection.results[2][1]["indices"] == _expected_result


@pytest.mark.gui
@pytest.mark.parametrize("index", [2, 3])
def test__select_new_frame__valid_index(qtbot, widget, path_w_data_files, index):
    widget.set_param_and_widget_value("filename", path_w_data_files / "hdf5_file.h5")
    widget.set_param_and_widget_value("hdf5_key_str", "/entry/data/3d_dataset_1")
    widget.set_param_and_widget_value("slicing_axis", 1)
    assert widget.spy_sig_new_selection.n == 3
    _index_selector = widget._widgets["index_selector"]
    with qtbot.waitSignal(widget.sig_new_selection, timeout=1000):
        _index_selector._move_to_index(index)
    assert widget.spy_sig_new_selection.n == 4
    _expected_result = (None, index)
    assert widget.spy_sig_new_selection.results[3][1]["indices"] == _expected_result


@pytest.mark.gui
def test__select_new_frame__same_index(qtbot, widget, path_w_data_files):
    widget.set_param_and_widget_value("filename", path_w_data_files / "hdf5_file.h5")
    widget.set_param_and_widget_value("hdf5_key_str", "/entry/data/3d_dataset_1")
    widget.set_param_and_widget_value("slicing_axis", 1)
    assert widget.spy_sig_new_selection.n == 3
    _index_selector = widget._widgets["index_selector"]
    _index_selector._move_to_index(0)
    qtbot.wait(20)  # ensure signal processing
    assert widget.spy_sig_new_selection.n == 3


@pytest.mark.gui
def test__select_new_frame__change_axis(qtbot, widget, path_w_data_files, test_data):
    _dset = "/entry/data/3d_dataset_1"
    _spy = widget.spy_sig_new_selection
    widget.set_param_and_widget_value("filename", path_w_data_files / "hdf5_file.h5")
    widget.set_param_and_widget_value("hdf5_key_str", _dset)
    widget.set_param_and_widget_value("slicing_axis", 2)
    _data = test_data[_dset]
    assert _spy.n == 3
    _index_selector = widget._widgets["index_selector"]
    with qtbot.waitSignal(widget.sig_new_selection, timeout=1000):
        _index_selector._move_to_index(_data.shape[2] - 1)
    assert _spy.n == 4
    _expected_result = (None, None, _data.shape[2] - 1)
    assert _spy.results[3][1]["indices"] == _expected_result
    # change to an axis with less points and check that the index resets to 0
    with (
        qtbot.waitSignal(widget.sig_new_selection, timeout=1000),
        warnings.catch_warnings(),
    ):
        warnings.simplefilter("ignore", category=UserWarning)
        widget.set_param_and_widget_value("slicing_axis", 1)
    assert _spy.n == 5
    assert _spy.results[4][1]["indices"] == (None, 0)
    # now move to the last index of axis 1
    with qtbot.waitSignal(widget.sig_new_selection, timeout=1000):
        _index_selector._move_to_index(_data.shape[1] - 1)
    assert _spy.n == 6
    assert _spy.results[5][1]["indices"] == (None, _data.shape[1] - 1)
    # and change to axis 2, which should keep the index
    with qtbot.waitSignal(widget.sig_new_selection, timeout=1000):
        widget.set_param_and_widget_value("slicing_axis", 2)
    assert _spy.n == 7
    assert _spy.results[6][1]["indices"] == (None, None, _data.shape[1] - 1)


if __name__ == "__main__":
    pytest.main([])

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

"""
Module with unittests for pydidas.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest
from qtpy import QtCore, QtGui

from pydidas.core import Parameter
from pydidas.unittest_objects import SignalSpy
from pydidas.widgets.parameter_config.param_io_widget_file import ParamIoWidgetFile
from pydidas_qtcore import PydidasQApplication


param_dir = Parameter("input_directory", Path, Path(), name="Input dir")
param_existing_file = Parameter("filename", Path, Path(), name="Input file")
param_output_file = Parameter("output_filename", Path, Path(), name="New file")
param_pattern = Parameter("file_pattern", Path, "test_##.nxs", name="File pattern")


def widget_from_param(qtbot, param, qref=None):
    param.restore_default()
    widget = ParamIoWidgetFile(param, persistent_qsettings_ref=qref)
    widget.spy_new_value = SignalSpy(widget.sig_new_value)
    widget.spy_value_changed = SignalSpy(widget.sig_value_changed)
    widget.show()
    qtbot.add_widget(widget)
    qtbot.wait_until(lambda: widget.isVisible(), timeout=500)
    return widget


def _drag_drop_args(widget, mime_data):
    return (
        widget.rect().center(),
        QtCore.Qt.CopyAction,
        mime_data,
        QtCore.Qt.LeftButton,
        QtCore.Qt.NoModifier,
    )


@pytest.fixture(autouse=True)
def _cleanup():
    yield
    app = PydidasQApplication.instance()
    for widget in [
        _w for _w in app.topLevelWidgets() if isinstance(_w, ParamIoWidgetFile)
    ]:
        widget.deleteLater()
    app.processEvents()


@pytest.fixture(scope="module")
def test_dir(temp_path):
    dir_path = temp_path / "param_io_widget_file_tests"
    dir_path.mkdir()
    np.savetxt(dir_path / "test_file.npy", np.arange(10))
    return dir_path


@pytest.mark.gui
@pytest.mark.parametrize("param", [param_dir, param_existing_file, param_output_file])
@pytest.mark.parametrize("qref", [None, "test_ref_file"])
def test__creation(qtbot, param, test_dir, qref):
    widget = widget_from_param(qtbot, param, qref=qref)
    assert isinstance(widget, ParamIoWidgetFile)
    assert hasattr(widget, "sig_new_value")
    assert hasattr(widget, "sig_value_changed")
    assert widget._io_dialog_config["reference"] == id(widget)
    if qref is None:
        assert widget._io_dialog_config["qsettings_ref"] is None
    else:
        assert widget._io_dialog_config["qsettings_ref"] == qref


@pytest.mark.gui
@pytest.mark.parametrize(
    "param", [param_dir, param_existing_file, param_output_file, param_pattern]
)
@pytest.mark.parametrize("qref", [None, "test_ref_file"])
@pytest.mark.parametrize("cancel", [True, False])
def test_button_function(qtbot, test_dir, param, qref, cancel):
    param.value = Path("/initial/path")
    widget = widget_from_param(qtbot, param)
    match param.refkey:
        case "input_directory":
            _ret_val = str(test_dir)
            _f = "pydidas.widgets.file_dialog.PydidasFileDialog.get_existing_directory"
        case "output_filename":
            _ret_val = str(test_dir / "new_test_file.npy")
            _f = "pydidas.widgets.file_dialog.PydidasFileDialog.get_saving_filename"
        case _:  # filename or pattern
            _ret_val = str(test_dir / "test_file.npy")
            _f = "pydidas.widgets.file_dialog.PydidasFileDialog.get_existing_filename"
    if cancel:
        _ret_val = None
    with patch(_f, return_value=_ret_val):
        widget.button_function()
    _expected_value = (
        str(param.value)
        if cancel
        else ("test_file.npy" if param.refkey == "file_pattern" else _ret_val)
    )
    assert widget.current_text == _expected_value
    assert widget.spy_new_value.n == (0 if cancel else 1)
    assert widget.spy_value_changed.n == (0 if cancel else 1)


@pytest.mark.gui
@pytest.mark.parametrize("param", [param_dir, param_existing_file, param_pattern])
@pytest.mark.parametrize("entry", [Path(), "dir", "subdir"])
def test_set_value(qtbot, test_dir, param, entry):
    widget = widget_from_param(qtbot, param)
    if entry == "dir":
        entry = test_dir
    elif entry == "subdir":
        entry = test_dir / "subdir"
    widget.set_value(entry)
    if entry.is_dir() and entry != Path() and "pattern" not in param.refkey:
        assert widget.io_dialog._stored_dirs[id(widget)] == str(entry)
    assert widget.spy_new_value.n == 1
    assert widget.spy_value_changed.n == 1


@pytest.mark.gui
@pytest.mark.parametrize("mime_method", ["setUrls", "setText"])
def test_drag_enter_event(qtbot, test_dir, mime_method):
    widget = widget_from_param(qtbot, param_output_file)
    # Prepare mime data with a file URL
    mime_data = QtCore.QMimeData()
    if mime_method == "setUrls":
        mime_data.setUrls([QtCore.QUrl.fromLocalFile(str(test_dir / "test_file.npy"))])
    elif mime_method == "setText":
        mime_data.setText("just plain text")
    # Simulate drag enter
    drag_enter_event = QtGui.QDragEnterEvent(*_drag_drop_args(widget, mime_data))
    widget.dragEnterEvent(drag_enter_event)
    assert drag_enter_event.isAccepted() == (mime_method == "setUrls")


@pytest.mark.gui
@pytest.mark.parametrize("n_files", [0, 1, 2])
def test_drop_event(qtbot, qapp, test_dir, n_files):
    widget = widget_from_param(qtbot, param_output_file)
    widget.set_value(test_dir / "default_file.npy")
    assert widget.spy_new_value.n == 1
    # Prepare mime data with a file URL
    mime_data = QtCore.QMimeData()
    if n_files == 0:
        mime_data.setText("text w/o URI")
    else:
        urls = [
            QtCore.QUrl.fromLocalFile(str(test_dir / f"test_file_{i}.npy"))
            for i in range(n_files)
        ]
        mime_data.setUrls(urls)
    drop_event = QtGui.QDropEvent(*_drag_drop_args(widget, mime_data))
    drop_event.acceptProposedAction()
    with patch("qtpy.QtWidgets.QMessageBox.exec_", return_value=None):
        widget.dropEvent(drop_event)
    if n_files == 1:
        assert Path(widget.current_text) == test_dir / "test_file_0.npy"
    else:
        assert Path(widget.current_text) == test_dir / "default_file.npy"
    assert widget.spy_new_value.n == (1 + (n_files == 1))
    assert widget.spy_value_changed.n == (1 + (n_files == 1))


@pytest.mark.gui
@pytest.mark.parametrize("value", [Path("/some/other/path"), Path(), None])
def test_update_widget_value(qtbot, test_dir, value):
    widget = widget_from_param(qtbot, param_existing_file)
    widget.update_widget_value(test_dir / "test_file.npy")
    widget.update_widget_value(value)
    assert Path(widget.current_text) == (value if value is not None else Path(""))
    assert widget.spy_new_value.n == 0
    assert widget.spy_value_changed.n == 0


if __name__ == "__main__":
    pytest.main([])

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

import numpy as np
import pytest
from qtpy import QtCore, QtGui

from pydidas.core import Parameter
from pydidas.unittest_objects import SignalSpy
from pydidas.unittest_objects.dummy_file_dialog import DummyFileDialog
from pydidas.widgets.parameter_config.param_io_widget_file import ParamIoWidgetFile
from pydidas_qtcore import PydidasQApplication


param_dir = Parameter("input_directory", Path, Path(), name="Input dir")
param_existing_file = Parameter("filename", Path, Path(), name="Input file")
param_output_file = Parameter("output_filename", Path, Path(), name="New file")
param_pattern = Parameter("file_pattern", Path, "test_##.nxs", name="File pattern")


def widget_from_param(qtbot, param, qref=None):
    param.restore_default()
    widget = ParamIoWidgetFile(
        param, persistent_qsettings_ref=qref, io_dialog=DummyFileDialog()
    )
    widget.spy_new_value = SignalSpy(widget.sig_new_value)
    widget.spy_value_changed = SignalSpy(widget.sig_value_changed)
    widget.show()
    qtbot.add_widget(widget)
    qtbot.wait_until(lambda: widget.isVisible(), timeout=500)
    return widget


@pytest.fixture(scope="module", autouse=True)
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
    match param.refkey:
        case "input_directory":
            assert widget.io_dialog_call == widget.io_dialog.get_existing_directory
        case "filename":
            assert widget.io_dialog_call == widget.io_dialog.get_existing_filename
        case "output_filename":
            assert widget.io_dialog_call == widget.io_dialog.get_saving_filename
    assert widget._io_dialog_config["reference"] == id(widget)
    if qref is None:
        assert widget._io_dialog_config["qsettings_ref"] is None
    else:
        assert widget._io_dialog_config["qsettings_ref"] == qref


@pytest.mark.parametrize(
    "param", [param_dir, param_existing_file, param_output_file, param_pattern]
)
@pytest.mark.parametrize("qref", [None, "test_ref_file"])
@pytest.mark.parametrize("cancel", [True, False])
def test_button_function(qtbot, test_dir, param, qref, cancel):
    param.value = Path("/initial/path")
    widget = widget_from_param(qtbot, param)
    if cancel:
        widget.io_dialog.returned_selection = None
    else:
        match param.refkey:
            case "input_directory":
                widget.io_dialog.returned_selection = str(test_dir)
            case "output_filename":
                widget.io_dialog.returned_selection = str(
                    test_dir / "new_test_file.npy"
                )
            case _:  # filename or pattern
                widget.io_dialog.returned_selection = str(test_dir / "test_file.npy")
    widget.button_function()
    _expected_value = (
        str(param.value)
        if cancel
        else (
            "test_file.npy"
            if param.refkey == "file_pattern"
            else widget.io_dialog.returned_selection[0]
        )
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
def test_drag_and_drop_file(qtbot, test_dir):
    def _drag_drop_args(mime_data):
        return (
            widget.rect().center(),
            QtCore.Qt.CopyAction,
            mime_data,
            QtCore.Qt.LeftButton,
            QtCore.Qt.NoModifier,
        )

    widget = widget_from_param(qtbot, param_existing_file)
    # Prepare mime data with a file URL
    mime_data = QtCore.QMimeData()
    mime_data.setUrls([QtCore.QUrl.fromLocalFile(str(test_dir / "test_file.npy"))])
    # Simulate drag enter
    drag_enter_event = QtGui.QDragEnterEvent(*_drag_drop_args(mime_data))
    QtCore.QCoreApplication.sendEvent(widget, drag_enter_event)
    # Simulate drop
    drop_event = QtGui.QDropEvent(*_drag_drop_args(mime_data))
    QtCore.QCoreApplication.sendEvent(widget, drop_event)
    assert Path(widget.current_text) == test_dir / "test_file.npy"
    assert widget.spy_new_value.n == 1
    assert widget.spy_value_changed.n == 1


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

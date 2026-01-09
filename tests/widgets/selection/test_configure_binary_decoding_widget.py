# This file is part of pydidas.
#
# Copyright 2025 - 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2025 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import re

import numpy as np
import pytest
from qtpy import QtCore

from pydidas.core import ParameterCollection
from pydidas.core.constants import (
    ASCII_IMPORT_EXTENSIONS,
    BINARY_EXTENSIONS,
    HDF5_EXTENSIONS,
    NUMPY_DTYPES,
    NUMPY_EXTENSIONS,
    TIFF_EXTENSIONS,
)
from pydidas.core.generic_parameters import get_generic_parameter
from pydidas.data_io import import_data
from pydidas.unittest_objects import SignalSpy
from pydidas.widgets.selection import ConfigureBinaryDecodingWidget
from pydidas_qtcore import PydidasQApplication


_EXTENSIONS = (
    HDF5_EXTENSIONS
    + NUMPY_EXTENSIONS
    + BINARY_EXTENSIONS
    + ASCII_IMPORT_EXTENSIONS
    + TIFF_EXTENSIONS
)

_FILENAMES = [
    "arange_int64.bin",
    "arange_float64.bin",
    "arange_float32.bin",
    "ones_int8.bin",
    "ones_uint16.bin",
]


@pytest.fixture(autouse=True)
def _cleanup():
    app = PydidasQApplication.instance()
    yield
    for widget in [
        _w
        for _w in app.topLevelWidgets()
        if isinstance(_w, ConfigureBinaryDecodingWidget)
    ]:
        widget.deleteLater()
    app.processEvents()  # Process deferred deletions


@pytest.fixture(scope="module")
def path_w_data_files(temp_path):
    _path = temp_path / "cbd_widget"
    if not _path.exists():
        _path.mkdir()
    np.arange(625).tofile(_path / "arange_int64.bin")
    np.arange(625).astype(np.double).tofile(_path / "arange_float64.bin")
    np.arange(625).astype(np.single).tofile(_path / "arange_float32.bin")
    np.ones(625).astype(np.int8).tofile(_path / "ones_int8.bin")
    np.ones(625).astype(np.uint16).tofile(_path / "ones_uint16.bin")
    with open(temp_path / "ascii_file.txt", "w") as f:
        f.write("1 2")
    yield _path


@pytest.fixture
def widget(qtbot):
    widget = ConfigureBinaryDecodingWidget()
    widget.spy_sig_new_binary_image = SignalSpy(widget.sig_new_binary_image)  # type: ignore[attr-defined]
    widget.spy_sig_new_binary_config = SignalSpy(widget.sig_new_binary_config)  # type: ignore[attr-defined]
    widget.spy_sig_decoding_invalid = SignalSpy(widget.sig_decoding_invalid)  # type: ignore[attr-defined]
    widget.show()
    qtbot.waitUntil(lambda: widget.isVisible(), timeout=1000)
    yield widget
    widget.deleteLater()


def dtype_size_and_str_repr(filename: str):
    _dtype = filename.removesuffix(".bin").removeprefix("arange_").removeprefix("ones_")
    _dtype_size = np.dtype(NUMPY_DTYPES[_dtype]).itemsize
    _dtype_str = "unsigned " if _dtype.startswith("u") else ""
    _dtype = _dtype.removeprefix("u")
    if _dtype.startswith("int"):
        _dtype_str += "int "
        _dtype = _dtype.removeprefix("int")
    elif _dtype.startswith("float"):
        _dtype_str += "float "
        _dtype = _dtype.removeprefix("float")
    _dtype_str += f"{_dtype} bit"
    return _dtype_size, _dtype_str


@pytest.mark.gui
@pytest.mark.parametrize("use_params", [True, False])
def test__creation(qtbot, temp_path, use_params):
    params = ParameterCollection(get_generic_parameter("filename"))
    kwargs = {"params": params} if use_params else {}
    widget = ConfigureBinaryDecodingWidget(**kwargs)
    widget.show()
    qtbot.waitUntil(lambda: widget.isVisible(), timeout=1000)
    assert isinstance(widget, ConfigureBinaryDecodingWidget)
    for _key in ConfigureBinaryDecodingWidget.default_params:
        assert _key in widget.params
    if use_params:
        assert id(widget.get_param("filename")) == id(params.get_param("filename"))
    assert id(widget._filename_param) == id(widget.get_param("filename"))
    for _key in ConfigureBinaryDecodingWidget.default_params:
        assert id(widget.get_param(_key)) != id(
            ConfigureBinaryDecodingWidget.default_params[_key]
        )
    for _key in ["raw_datatype", "raw_n_y", "raw_n_x", "raw_header_size"]:
        assert _key in widget.param_composite_widgets
        assert widget.param_composite_widgets[_key].isVisible()


@pytest.mark.gui
def test_set_new_filename__qapp_test(qtbot, qapp):
    _original_font_size = qapp.font_size
    with qtbot.waitSignal(qapp.sig_font_size_changed):
        qapp.font_size = _original_font_size + 1
    qapp.font_size = _original_font_size
    assert qapp.font_size == _original_font_size


@pytest.mark.gui
@pytest.mark.parametrize("filename", ["ascii_file.txt", "no_such_file.bin"])
def test_set_new_filename__invalid_files(widget, path_w_data_files, filename):
    _new_path = path_w_data_files / filename
    widget.set_new_filename(_new_path)
    assert not widget.decoding_is_valid
    assert widget.spy_sig_new_binary_image.n == 0
    assert widget.spy_sig_new_binary_config.n == 0
    assert widget.spy_sig_decoding_invalid.n == 0
    assert not widget.isVisible()


@pytest.mark.gui
@pytest.mark.parametrize("filename", _FILENAMES)
def test_set_new_filename__binary(qtbot, widget, path_w_data_files, filename):
    _new_path = path_w_data_files / filename
    with qtbot.waitSignal(widget.sig_decoding_invalid, timeout=1000):
        widget.set_new_filename(_new_path)
    # Allow event loop to process all pending events
    qtbot.waitUntil(lambda: widget.spy_sig_decoding_invalid.n == 1, timeout=1000)
    assert not widget.decoding_is_valid
    assert widget.spy_sig_new_binary_image.n == 0
    assert widget.spy_sig_new_binary_config.n == 0
    _dtype_bytes = int(re.sub(r"[a-z_]", "", filename.removesuffix(".bin"))) // 8
    assert widget._config["filesize"] == (_dtype_bytes * 625)


@pytest.mark.gui
@pytest.mark.parametrize("filename", _FILENAMES)
def test_check_decoding(qtbot, widget, path_w_data_files, filename):
    _new_path = path_w_data_files / filename
    _dtype_size, _dtype_str = dtype_size_and_str_repr(filename)
    widget.set_new_filename(_new_path)
    widget.set_param_and_widget_value("raw_datatype", _dtype_str)
    assert not widget.decoding_is_valid
    assert widget.spy_sig_new_binary_image.n == 0
    assert widget.spy_sig_new_binary_config.n == 0
    assert widget.spy_sig_decoding_invalid.n == 1
    # check with original size
    widget.set_param_and_widget_value("raw_n_y", 25)
    with qtbot.waitSignal(widget.sig_new_binary_image, timeout=1000):
        widget.set_param_and_widget_value("raw_n_x", 25)
    assert widget.decoding_is_valid
    assert widget.spy_sig_new_binary_image.n == 1
    assert widget.spy_sig_new_binary_config.n == 1
    assert widget.spy_sig_decoding_invalid.n == 1
    _fname, _kwargs = widget.spy_sig_new_binary_image.results[0]
    _image = import_data(_fname, **_kwargs)
    assert _image.shape == (25, 25)
    # check with invalid size
    widget.set_param_and_widget_value("raw_n_y", 625)
    qtbot.waitUntil(lambda: widget.spy_sig_decoding_invalid.n == 2, timeout=1000)
    assert not widget.decoding_is_valid
    assert widget.spy_sig_new_binary_image.n == 1
    assert widget.spy_sig_new_binary_config.n == 1
    # check with second correct size 625 * 1
    with qtbot.waitSignal(widget.sig_new_binary_image, timeout=1000):
        widget.set_param_and_widget_value("raw_n_x", 1)
    assert widget.decoding_is_valid
    assert widget.spy_sig_new_binary_image.n == 2
    assert widget.spy_sig_new_binary_config.n == 2
    assert widget.spy_sig_decoding_invalid.n == 2
    _fname, _kwargs = widget.spy_sig_new_binary_image.results[1]
    _image = import_data(_fname, **_kwargs)
    assert _image.shape == (625, 1)
    # check with header offset
    widget.set_param_and_widget_value("raw_header_size", 25 * _dtype_size)
    qtbot.waitUntil(lambda: widget.spy_sig_decoding_invalid.n == 3, timeout=1000)
    assert not widget.decoding_is_valid
    assert widget.spy_sig_new_binary_image.n == 2
    assert widget.spy_sig_new_binary_config.n == 2
    # correct the size for the header offset
    with qtbot.waitSignal(widget.sig_new_binary_image, timeout=1000):
        widget.set_param_and_widget_value("raw_n_y", 600)
    assert widget.decoding_is_valid
    assert widget.spy_sig_new_binary_image.n == 3
    assert widget.spy_sig_new_binary_config.n == 3
    assert widget.spy_sig_decoding_invalid.n == 3
    _fname, _kwargs = widget.spy_sig_new_binary_image.results[2]
    _image = import_data(_fname, **_kwargs)
    assert _image.shape == (600, 1)


@pytest.mark.gui
def test_toggle_details(qtbot, widget):
    for _key in widget.param_composite_widgets:
        assert widget.param_composite_widgets[_key].isVisible()
    assert widget._widgets["show_decoding_details"].isVisible()
    assert widget._widgets["show_decoding_details"].isEnabled()
    for _run in range(2):
        with qtbot.waitSignal(
            widget._widgets["show_decoding_details"].clicked, timeout=1000
        ):
            qtbot.mouseClick(
                widget._widgets["show_decoding_details"],
                QtCore.Qt.MouseButton.LeftButton,
            )
        # Allow event loop to process visibility changes
        qtbot.waitUntil(
            lambda: (
                all(
                    widget.param_composite_widgets[_key].isVisible() == _run
                    for _key in widget.param_composite_widgets
                )
            ),
            timeout=1000,
        )
        # Note: the above waitUntil also serves as assertion of visibility state
        # because if the condition is not met, the test will fail due to timeout


if __name__ == "__main__":
    pytest.main([])

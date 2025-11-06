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
Module with pydidas unittests
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from pathlib import Path
from typing import Any

import numpy as np
import pytest
from numpy import nan

from pydidas.core import Hdf5key, Parameter
from pydidas.core.constants import FLOAT_DISPLAY_ACCURACY
from pydidas.unittest_objects import SignalSpy
from pydidas.widgets import PydidasFileDialog
from pydidas.widgets.parameter_config.base_param_io_widget import BaseParamIoWidget
from pydidas_qtcore import PydidasQApplication


class _TestBaseParamWidget(BaseParamIoWidget):
    def __init__(self, param, **kwargs: Any):
        super().__init__(param, **kwargs)
        self._val = param.value

    @property
    def current_text(self):
        return str(self._val)

    def update_widget_value(self, value: Any) -> None:
        self._val = value


@pytest.fixture(scope="module", autouse=True)
def _cleanup():
    yield
    app = PydidasQApplication.instance()
    for widget in [
        _w for _w in app.topLevelWidgets() if isinstance(_w, BaseParamIoWidget)
    ]:
        widget.deleteLater()
    app.processEvents()


@pytest.fixture(scope="module")
def param():
    return Parameter("test", str, "entry")


@pytest.fixture
def widget(qtbot, param):
    widget = _TestBaseParamWidget(param)
    widget.show()
    qtbot.add_widget(widget)
    qtbot.wait_until(lambda: widget.isVisible(), timeout=500)
    return widget


@pytest.fixture
def spy_value_changed(widget):
    return SignalSpy(widget.sig_value_changed)


@pytest.fixture
def spy_new_value(widget):
    return SignalSpy(widget.sig_new_value)


def widget_with_param(qtbot, param):
    widget = _TestBaseParamWidget(param)
    widget.show()
    qtbot.add_widget(widget)
    qtbot.wait_until(lambda: widget.isVisible(), timeout=500)
    return widget


@pytest.mark.gui
def test__creation(widget):
    assert isinstance(widget, BaseParamIoWidget)
    assert hasattr(widget, "sig_new_value")
    assert hasattr(widget, "sig_value_changed")
    assert isinstance(widget._linked_param, Parameter)


@pytest.mark.gui
def test_current_text(widget):
    assert widget.current_text == "entry"


@pytest.mark.gui
@pytest.mark.parametrize(
    "input_str, expected",
    [(_k, _v) for _k, _v in BaseParamIoWidget._SUPPORTED_TYPE_STRINGS.items()],
)
@pytest.mark.parametrize("case", ["lower", "upper", "mixed"])
def test_is_special_type_string__valid(widget, input_str, expected, case):
    match case:
        case "lower":
            input_str = input_str.lower()
        case "upper":
            input_str = input_str.upper()
        case "mixed":
            input_str = input_str.capitalize()
    assert widget.is_special_type_string(input_str) is True
    if expected in [None, np.nan]:
        assert widget.special_type_from_string(input_str) is expected
    else:
        assert widget.special_type_from_string(input_str) == expected


@pytest.mark.gui
@pytest.mark.parametrize("case", ["lower", "upper", "mixed"])
@pytest.mark.parametrize("input_str", ["invalid_string", "123", "123.4"])
def test_special_type_strings__w_common_entry(widget, case, input_str):
    input_str = "invalid_string"
    match case:
        case "lower":
            input_str = input_str.lower()
        case "upper":
            input_str = input_str.upper()
        case "mixed":
            input_str = input_str.capitalize()
    assert widget.is_special_type_string(input_str) is False
    assert widget.special_type_from_string(input_str) == input_str


# TODO : check if sizeHint required
# @pytest.mark.gui
# @pytest.mark.parametrize("linebreak", [True, False])
# def test_size_hint_height_factor(widget, param, linebreak):
#     widget_lb = _TestBaseParamWidget(param, linebreak=linebreak)
#     expected_factor = 1 + int(linebreak)
#     assert widget_lb.sizeHint().height() == 25 * expected_factor


@pytest.mark.gui
@pytest.mark.parametrize(
    "dtype, value, expected",
    [
        (str, "new_entry", "new_entry"),
        (float, "nan", nan),
        (str, "None", None),
        (float, "12.4", 12.4),
        (Hdf5key, "/entry/data/data", Hdf5key("/entry/data/data")),
        (Path, "/some/path", Path("/some/path")),
        (np.ndarray, (1, 2, 3), np.array([1, 2, 3])),
        (int, "42", 42),
    ],
)
def test_get_value(qtbot, dtype, value, expected):
    param = Parameter("test", dtype, value, allow_None=value == "None")
    widget = widget_with_param(qtbot, param)
    if expected is None or expected is np.nan:
        assert widget.get_value() is expected
    elif dtype == np.ndarray:
        np.testing.assert_array_equal(widget.get_value(), expected)
    else:
        assert widget.get_value() == expected


@pytest.mark.gui
@pytest.mark.parametrize(
    "dtype, value, update, expected",
    [
        (str, "entry", "new_entry", "new_entry"),
        (float, 12, nan, nan),
        (float, 12, None, None),
        (
            float,
            4,
            12.0123456789876,
            np.round(12.0123456789876, decimals=FLOAT_DISPLAY_ACCURACY),
        ),
        (Hdf5key, "/entry/data/data", "/entry/other/data", "/entry/other/data"),
        (Path, Path("/some/path"), "/another/path", "/another/path"),
        (np.ndarray, (1, 2, 3), (2, 3, 4), (2, 3, 4)),
        (int, 12, 42, 42),
    ],
)
def test_set_value(qtbot, dtype, value, update, expected):
    param = Parameter("test", dtype, value, allow_None=None in [value, update])
    widget = widget_with_param(qtbot, param)
    widget.set_value(update)
    if value is None or value is np.nan:
        assert param.value is value
    elif dtype == np.ndarray:
        np.testing.assert_array_equal(param.value, np.array(value))
    else:
        assert param.value == value
    if update is None or update is np.nan:
        assert widget._val is expected
    elif dtype == np.ndarray:
        np.testing.assert_array_equal(widget._val, np.array(expected))
    else:
        assert widget._val == expected


@pytest.mark.gui
@pytest.mark.parametrize("has_io_dialog", [True, False])
def test_set_unique_ref_name(widget, has_io_dialog):
    if has_io_dialog:
        widget._io_dialog_config = {}
    widget.set_unique_ref_name("unique_name")
    assert hasattr(widget, "_io_dialog_config") == has_io_dialog
    if has_io_dialog:
        assert widget._io_dialog_config["qsettings_ref"] == "unique_name"


@pytest.mark.gui
@pytest.mark.parametrize("has_io_dialog", [True, False])
def test_update_io_directory(widget, has_io_dialog, temp_path):
    if has_io_dialog:
        widget.io_dialog = PydidasFileDialog()
    widget.update_io_directory(temp_path)
    assert hasattr(widget, "io_dialog") == has_io_dialog
    if has_io_dialog:
        assert widget.io_dialog._stored_dirs[id(widget)] == str(temp_path)


@pytest.mark.gui
def test_emit_signal(widget, spy_value_changed, spy_new_value):
    widget.update_widget_value("dummy")
    assert spy_value_changed.n == 0
    assert spy_new_value.n == 0
    widget.emit_signal()
    assert spy_value_changed.n == 1
    assert spy_new_value.n == 1
    widget.emit_signal()
    assert spy_value_changed.n == 1
    assert spy_new_value.n == 1
    assert spy_new_value.results[0] == ["dummy"]
    widget.emit_signal(force_update=True)
    assert spy_value_changed.n == 2
    assert spy_new_value.n == 2
    assert spy_new_value.results[1] == ["dummy"]


if __name__ == "__main__":
    pytest.main([])

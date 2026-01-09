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

"""Unit tests for the ParameterWidget."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import os
from pathlib import Path
from typing import Generator

import numpy as np
import pytest
from qtpy import QtCore

from pydidas.core import Hdf5key, Parameter, UserConfigError
from pydidas.core.constants import (
    FONT_METRIC_PARAM_EDIT_WIDTH,
    MINIMUM_WIDGET_DIMENSIONS,
    PARAM_WIDGET_TEXT_WIDTH,
    PARAM_WIDGET_UNIT_WIDTH,
)
from pydidas.core.utils import get_random_string
from pydidas.unittest_objects import SignalSpy
from pydidas.widgets.parameter_config import ParameterWidget
from pydidas.widgets.parameter_config.param_io_widget_checkbox import (
    ParamIoWidgetCheckBox,
)
from pydidas.widgets.parameter_config.param_io_widget_combobox import (
    ParamIoWidgetComboBox,
)
from pydidas.widgets.parameter_config.param_io_widget_file import ParamIoWidgetFile
from pydidas.widgets.parameter_config.param_io_widget_hdf5key import (
    ParamIoWidgetHdf5Key,
)
from pydidas.widgets.parameter_config.param_io_widget_lineedit import (
    ParamIoWidgetLineEdit,
)
from pydidas_qtcore import PydidasQApplication


_TEST_DTYPE_VAL_NEW_VALS = [
    (str, "A", "Spam"),
    (int, 42, -5),
    (float, 1.2, -4.2),
    (Path, Path("/tmp"), Path("/home/user")),
    (Hdf5key, Hdf5key("/entry/A"), Hdf5key("/entry/meta/B")),
]
LAYOUT_VERTICAL_SPACING = ParameterWidget.LAYOUT_VERTICAL_SPACING
LAYOUT_TOP_BOTTOM_MARGIN = ParameterWidget.LAYOUT_TOP_BOTTOM_MARGIN


def widget_instance(qtbot, param, **kwargs) -> ParameterWidget:
    param.restore_default()
    widget = ParameterWidget(param, **kwargs)
    widget.spy_new_value = SignalSpy(widget.sig_new_value)  # type: ignore[attr-defined]
    widget.spy_value_changed = SignalSpy(widget.sig_value_changed)  # type: ignore[attr-defined]
    qtbot.add_widget(widget)
    widget.show()
    qtbot.waitUntil(lambda: widget.isVisible(), timeout=1000)
    return widget


@pytest.fixture(autouse=True)
def _cleanup() -> Generator[None, None, None]:
    app = PydidasQApplication.instance()
    _starting_fontsize = app.font_size
    yield
    with QtCore.QSignalBlocker(app):
        app.font_size = _starting_fontsize
    for widget in [
        _w for _w in app.topLevelWidgets() if isinstance(_w, ParameterWidget)
    ]:
        widget.deleteLater()
    app.processEvents()


@pytest.mark.gui
@pytest.mark.parametrize("choices", [[False], [True], [1, 0]])
@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        {"linebreak": True},
        {"width_unit": 0.2},
        {"linebreak": True, "width_unit": 0.5},
        {"width_unit": 0},
    ],
)
@pytest.mark.parametrize("width", [30, 100, None])
@pytest.mark.parametrize("font_size", [7, 10, 15])
def test__creation__w__bool_choices(qtbot, qapp, choices, kwargs, width, font_size) -> None:
    qapp.font_size = font_size
    _expected_width = qapp.font_char_width * (
        width if width is not None else FONT_METRIC_PARAM_EDIT_WIDTH
    )
    _expected_height = int(
        max(np.ceil(qapp.font_height * 1.05), MINIMUM_WIDGET_DIMENSIONS)
        + 2 * LAYOUT_VERTICAL_SPACING
        + 2 * LAYOUT_TOP_BOTTOM_MARGIN
    )
    _default = True if (choices is None or True in choices) else False
    param = Parameter(
        "test_bool",
        int,
        _default,
        name=get_random_string(100),
        choices=choices,
        unit="C",
    )
    widget = widget_instance(
        qtbot, param, **(kwargs | {"font_metric_width_factor": width})
    )
    assert isinstance(widget.io_widget, ParamIoWidgetCheckBox)
    assert widget.param == param
    assert widget.height() == _expected_height
    assert abs(_expected_width - widget.width()) < 3
    if "unit" in widget._widgets:
        _expected_unit_width = int(
            max(
                widget._MIN_VIS_UNIT_WIDTH * qapp.font_char_width,
                _expected_width * kwargs.get("width_unit", PARAM_WIDGET_UNIT_WIDTH),
            )
        )
        _actual_unit_width = widget._widgets["unit"].width()
        _expected_io_width = _expected_width - _expected_unit_width
        assert abs(_expected_unit_width - _actual_unit_width) < 3
        assert abs(_expected_io_width - widget.io_widget.width()) < 3
    else:
        assert abs(_expected_width - widget.io_widget.width()) < 3


@pytest.mark.gui
@pytest.mark.parametrize(
    "dtype, default, choices",
    [
        (str, "A", ["A", "B", "C"]),
        (int, 42, [42, -1, 5]),
        (float, 1.2, [1.2, -2.4, 0.0]),
        (Path, Path("/tmp"), [Path("/tmp"), Path("/home")]),
        (Hdf5key, Hdf5key("/entry/A"), [Hdf5key("/entry/A"), Hdf5key("/entry/meta/B")]),
    ],
)
@pytest.mark.parametrize("use_choices", [True, False])
def test__creation__check_choices_behaviour(
    qtbot, dtype, default, choices, use_choices
) -> None:
    param = Parameter(
        "test",
        dtype,
        default,
        name="Test",
        choices=(choices if use_choices else None),
    )
    widget = widget_instance(qtbot, param)
    assert widget.param == param
    assert widget.io_widget.current_text == str(default)
    if use_choices:
        assert isinstance(widget.io_widget, ParamIoWidgetComboBox)
        assert widget.io_widget.current_choices == [str(_item) for _item in choices]
    else:
        if dtype is Path:
            assert isinstance(widget.io_widget, ParamIoWidgetFile)
        elif dtype is Hdf5key:
            assert isinstance(widget.io_widget, ParamIoWidgetHdf5Key)
        else:
            assert isinstance(widget.io_widget, ParamIoWidgetLineEdit)


@pytest.mark.gui
@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        {"linebreak": True, "width_unit": 0.0},
        {"width_text": 0.2, "width_unit": 0.2},
        {"linebreak": True, "width_unit": 0.5, "width_text": 0.3},
        {"width_unit": 0, "width_text": 0.3},
    ],
)
@pytest.mark.parametrize("width", [30, 100, None])
@pytest.mark.parametrize("unit", ["m", ""])
def test__creation__check_layout(qtbot, qapp, kwargs, width, unit) -> None:
    # Note: the font size is not checked here because it is covered in the test
    # with the bool choices above.
    _linebreak = int(kwargs.get("linebreak", False))
    _rel_text_width = kwargs.get("width_text", PARAM_WIDGET_TEXT_WIDTH)
    _rel_unit_width = (
        0 if len(unit) == 0 else kwargs.get("width_unit", PARAM_WIDGET_UNIT_WIDTH)
    )
    param = Parameter("test", str, "Test value", name="Test", unit=unit)
    widget = widget_instance(
        qtbot, param, **(kwargs | {"font_metric_width_factor": width})
    )
    # determine the expected widths first in characters
    # then convert to pixels (required for calc of relative I/O width)
    _width_in_chars = width if width is not None else FONT_METRIC_PARAM_EDIT_WIDTH
    _expected_global_width = int(qapp.font_char_width * _width_in_chars)
    _expected_global_height = (
        (2 + _linebreak) * LAYOUT_VERTICAL_SPACING
        + 2 * LAYOUT_TOP_BOTTOM_MARGIN
        + (1 + _linebreak)
        * max(
            int(np.ceil(1.05 * qapp.font_height)),
            MINIMUM_WIDGET_DIMENSIONS,
        )
    )
    _expected_label_width = _width_in_chars * max(_linebreak, _rel_text_width)
    _expected_label_width_px = int(qapp.font_char_width * _expected_label_width)
    _expected_unit_width = (
        0
        if _rel_unit_width == 0
        else max(widget._MIN_VIS_UNIT_WIDTH, (_width_in_chars * _rel_unit_width))
    )
    _expected_unit_width_px = int(qapp.font_char_width * _expected_unit_width)
    _expected_io_width_px = int(
        (
            0.9 * _width_in_chars - _expected_unit_width
            if _linebreak
            else _width_in_chars - _expected_label_width - _expected_unit_width
        )
        * qapp.font_char_width
    )
    _expected_subwidget_height = max(
        int(np.ceil(1.05 * qapp.font_height)),
        MINIMUM_WIDGET_DIMENSIONS,
    )
    _expected_row0_top = LAYOUT_TOP_BOTTOM_MARGIN + LAYOUT_VERTICAL_SPACING
    _expected_row_offset = _expected_subwidget_height + LAYOUT_VERTICAL_SPACING

    assert widget.param == param
    assert isinstance(widget.io_widget, ParamIoWidgetLineEdit)
    assert _expected_global_height == widget.height()
    assert _expected_global_width == widget.width()

    assert widget._widgets["label"].geometry().left() == 0
    assert widget._widgets["label"].geometry().top() == _expected_row0_top
    assert widget._widgets["label"].geometry().width() == _expected_label_width_px
    assert widget._widgets["label"].geometry().height() == _expected_subwidget_height

    assert (
        widget._widgets["io"].geometry().left()
        - (
            int(0.1 * _expected_global_width)
            if _linebreak
            else _expected_label_width_px
        )
        <= 1
    )
    assert widget._widgets["io"].geometry().top() == (
        _expected_row0_top + _linebreak * _expected_row_offset
    )
    assert widget._widgets["io"].geometry().width() == _expected_io_width_px
    assert widget._widgets["io"].geometry().height() == _expected_subwidget_height
    assert _expected_io_width_px == widget.io_widget.width()

    if "unit" in widget._widgets:
        # due to rounding errors, we need to allow for a tolerance of 1 pixel here
        assert (
            widget._widgets["unit"].geometry().left()
            - _expected_global_width
            - _expected_unit_width_px
            <= 1
        )
        assert (
            widget._widgets["unit"].geometry().top()
            == _expected_row0_top + _linebreak * _expected_row_offset
        )
        assert widget._widgets["unit"].geometry().width() == _expected_unit_width_px
        assert widget._widgets["unit"].geometry().height() == _expected_subwidget_height


@pytest.mark.gui
def test__creation__w_visible_kwarg(qtbot, qapp) -> None:
    """
    Visible kwarg must be checked because it uses the sizeHint during __init__
    and the widget overrides the standard sizeHint behavior.
    """
    param = Parameter("test", str, "Test value", name="Test")
    kwargs = {"visible": True, "fixedWidth": 123, "font_metric_width_factor": 50}
    widget = widget_instance(qtbot, param, **kwargs)
    assert widget.isVisible() is True
    assert widget.width() == int(qapp.font_char_width * 50)


@pytest.mark.gui
@pytest.mark.parametrize("dtype, default, new_value", _TEST_DTYPE_VAL_NEW_VALS)
def test_set_param_value(qtbot, dtype, default, new_value) -> None:
    param = Parameter("test", dtype, default, name="Test param")
    widget = widget_instance(qtbot, param)
    widget.set_param_value(str(new_value))
    assert widget.param.value == new_value


@pytest.mark.gui
@pytest.mark.parametrize("dtype, default, new_value", _TEST_DTYPE_VAL_NEW_VALS)
def test_set_param_value__through_widget_signal(qtbot, dtype, default, new_value) -> None:
    param = Parameter("test", dtype, default, name="Test param")
    widget = widget_instance(qtbot, param)
    assert widget.param.value == default
    assert widget.display_value == str(default)
    widget.io_widget.setFocus()
    if os.environ.get("QT_QPA_PLATFORM") == "offscreen":
        widget.io_widget.update_widget_value(str(new_value))
        widget.io_widget.emit_signal()
        qtbot.wait(5)  # wait for signals to be processed
    else:
        qtbot.waitUntil(lambda: widget.io_widget.hasFocus(), timeout=2000)
        widget.io_widget.update_widget_value(str(new_value))
        widget.io_widget.clearFocus()
        qtbot.waitUntil(lambda: widget.io_widget.hasFocus() is False, timeout=1000)
    assert widget.param.value == new_value
    assert widget.display_value == str(new_value)
    assert widget.spy_new_value.n == 1  # type: ignore[attr-defined]
    assert widget.spy_value_changed.n == 1  # type: ignore[attr-defined]


@pytest.mark.gui
@pytest.mark.parametrize(
    "dtype, default, new_value",
    [
        (str, "A", ["a", "b"]),
        (int, 42, "not_an_int"),
        (float, 1.2, "not_a_float"),
        (Path, Path("/tmp"), 42),
        (Hdf5key, Hdf5key("/entry/A"), -1.0),
    ],
)
def test_set_param_value__illegal_new_value(qtbot, dtype, default, new_value) -> None:
    param = Parameter("test", dtype, default, name="Test param")
    widget = widget_instance(qtbot, param)
    assert widget.param.value == default
    assert widget.display_value == str(default)
    with pytest.raises((ValueError, UserConfigError)):  # type: ignore[arg-type]
        widget.set_param_value(new_value)
    assert widget.param.value == default
    assert widget.display_value == str(default)
    assert widget.spy_new_value.n == 0  # type: ignore[attr-defined]
    assert widget.spy_value_changed.n == 0  # type: ignore[attr-defined]


@pytest.mark.gui
@pytest.mark.parametrize("dtype, default, new_value", _TEST_DTYPE_VAL_NEW_VALS)
def test_update_display_value(qtbot, dtype, default, new_value) -> None:
    param = Parameter("test", dtype, default, name="Test param")
    widget = widget_instance(qtbot, param)
    widget.update_display_value(new_value)
    assert param.value == default
    assert widget.display_value == str(new_value)
    assert widget.spy_new_value.n == 0  # type: ignore[attr-defined]
    assert widget.spy_value_changed.n == 0  # type: ignore[attr-defined]


@pytest.mark.gui
@pytest.mark.parametrize("dtype, default, new_value", _TEST_DTYPE_VAL_NEW_VALS)
def test_set_value(qtbot, dtype, default, new_value) -> None:
    param = Parameter("test", dtype, default, name="Test param")
    widget = widget_instance(qtbot, param)
    with qtbot.waitSignal(widget.sig_new_value, timeout=500):
        widget.set_value(new_value)
    qtbot.wait(5)  # wait for signal processing
    assert param.value == new_value
    assert widget.display_value == str(new_value)
    assert widget.spy_new_value.n == 1  # type: ignore[attr-defined]
    assert widget.spy_value_changed.n == 1  # type: ignore[attr-defined]
    widget.set_value(new_value)
    qtbot.wait(5)  # wait for signal processing
    assert widget.spy_new_value.n == 1  # type: ignore[attr-defined]
    assert widget.spy_value_changed.n == 1  # type: ignore[attr-defined]


@pytest.mark.gui
@pytest.mark.parametrize("selection", ["A", "B", "C"])
def test_update_choices_from_param(qtbot, selection) -> None:
    param = Parameter("test", str, "D", choices=["D", "E", "F"])
    widget = widget_instance(qtbot, param)
    param.set_value_and_choices(selection, choices=["A", "B", "C"])
    widget.update_choices_from_param()
    qtbot.wait(5)  # wait for signal processing
    assert widget.io_widget.current_choices == ["A", "B", "C"]
    assert widget.param.choices == ["A", "B", "C"]
    assert widget.display_value == selection
    assert widget.spy_new_value.n == 0  # type: ignore[attr-defined]
    assert widget.spy_value_changed.n == 0  # type: ignore[attr-defined]


@pytest.mark.gui
@pytest.mark.parametrize("selection", ["A", "B", "C"])
def test_update_choices_from_param__no_previous_choices(qtbot, selection) -> None:
    param = Parameter("test", str, "D")
    widget = widget_instance(qtbot, param)
    param.set_value_and_choices(selection, choices=["A", "B", "C"])
    widget.update_choices_from_param()
    qtbot.wait(5)  # wait for signal processing
    assert isinstance(widget.io_widget, ParamIoWidgetComboBox)
    assert widget.io_widget.current_choices == ["A", "B", "C"]
    assert widget.display_value == selection
    assert widget.spy_new_value.n == 0  # type: ignore[attr-defined]
    assert widget.spy_value_changed.n == 0  # type: ignore[attr-defined]


@pytest.mark.gui
@pytest.mark.parametrize("selection", ["A", "B", "C"])
def test_update_choices_from_param__choices_removed(qtbot, selection) -> None:
    param = Parameter("test", str, "D", choices=["D", "E", "F"])
    widget = widget_instance(qtbot, param)
    param.set_value_and_choices(selection, None)
    widget.update_choices_from_param()
    qtbot.wait(5)  # wait for signal processing
    assert isinstance(widget.io_widget, ParamIoWidgetLineEdit)
    assert widget.io_widget.current_choices is None
    assert widget.display_value == selection
    assert widget.spy_new_value.n == 0  # type: ignore[attr-defined]
    assert widget.spy_value_changed.n == 0  # type: ignore[attr-defined]


if __name__ == "__main__":
    pytest.main([])

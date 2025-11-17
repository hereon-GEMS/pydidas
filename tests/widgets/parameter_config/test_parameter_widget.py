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

import pytest

from pydidas.core import Hdf5key, Parameter, UserConfigError
from pydidas.core.constants import (
    FONT_METRIC_PARAM_EDIT_WIDTH,
    MINIMUN_WIDGET_DIMENSIONS,
    PARAM_WIDGET_EDIT_WIDTH,
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


def widget_instance(qtbot, param, **kwargs):
    param.restore_default()
    widget = ParameterWidget(param, **kwargs)
    widget.spy_new_value = SignalSpy(widget.sig_new_value)
    widget.spy_value_changed = SignalSpy(widget.sig_value_changed)
    widget.show()
    qtbot.add_widget(widget)
    qtbot.waitUntil(lambda: widget.isVisible(), timeout=500)
    return widget


@pytest.fixture(scope="module", autouse=True)
def _cleanup():
    yield
    app = PydidasQApplication.instance()
    for widget in [
        _w for _w in app.topLevelWidgets() if isinstance(_w, ParameterWidget)
    ]:
        widget.deleteLater()
    app.processEvents()


@pytest.mark.gui
@pytest.mark.parametrize("choices", [[True, False], [False], [True], [1, 0]])
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
def test__creation__w__bool_choices(qtbot, qapp, choices, kwargs, width):
    _expected_width = qapp.font_char_width * (
        width if width is not None else FONT_METRIC_PARAM_EDIT_WIDTH
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
    assert widget.height() == MINIMUN_WIDGET_DIMENSIONS + 4  # assert no linebreak
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
):
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
def test__creation__check_layout(qtbot, qapp, kwargs, width, unit):
    param = Parameter(
        "test",
        str,
        "Test value",
        name="Test",
        unit=unit,
    )
    _linebreak = int(kwargs.get("linebreak", False))
    _text_width_in_chars = kwargs.get("width_text", PARAM_WIDGET_TEXT_WIDTH)
    _io_width_in_chars = kwargs.get("width_io", PARAM_WIDGET_EDIT_WIDTH)
    _unit_width_in_chars = kwargs.get("width_unit", PARAM_WIDGET_UNIT_WIDTH)
    widget = widget_instance(
        qtbot, param, **(kwargs | {"font_metric_width_factor": width})
    )
    # determine the expected widths (first in characters then convert to pixels)
    _expected_width = qapp.font_char_width * (
        width if width is not None else FONT_METRIC_PARAM_EDIT_WIDTH
    )
    _expected_height = (
        (widget._MARGINS + max(qapp.font_height, MINIMUN_WIDGET_DIMENSIONS))
        * (1 + _linebreak)
    ) + widget._SPACING
    _width_in_chars = width if width is not None else FONT_METRIC_PARAM_EDIT_WIDTH
    _expected_label_width = _width_in_chars * max(_linebreak, _text_width_in_chars)
    _expected_unit_width = (
        0
        if (
            len(unit) == 0
            or _unit_width_in_chars == 0
            or widget._param_widget_class in (ParamIoWidgetFile, ParamIoWidgetHdf5Key)
        )
        else max(
            widget._MIN_VIS_UNIT_WIDTH, int(_width_in_chars * _unit_width_in_chars)
        )
    )
    _expected_io_width = (
        0.9 * _width_in_chars - _expected_unit_width
        if _linebreak
        else _width_in_chars - _expected_label_width - _expected_unit_width
    ) * qapp.font_char_width
    _expected_label_width *= qapp.font_char_width
    _expected_unit_width *= qapp.font_char_width
    # make assertions
    assert widget.param == param
    assert isinstance(widget.io_widget, ParamIoWidgetLineEdit)
    assert abs(_expected_height - widget.height()) < 2
    assert abs(_expected_width - widget.width()) < 5
    assert abs(_expected_label_width - widget._widgets["label"].width()) < 5
    assert (
        widget.io_widget.geometry().left() + _expected_io_width <= _expected_width + 2
    )
    if "unit" in widget._widgets:
        assert "unit" in widget._widgets
        assert abs(_expected_unit_width - widget._widgets["unit"].width()) < 5
    assert abs(_expected_io_width - widget.io_widget.width()) < 5


@pytest.mark.gui
def test__creation__w_visible_kwarg(qtbot, qapp):
    """
    Visible kwarg must be checked because it uses the sizeHint during __init__
    and the widget overrides the standard sizeHint behavior.
    """
    param = Parameter("test", str, "Test value", name="Test")
    kwargs = {"visible": True, "fixedWidth": 123, "font_metric_width_factor": 50}
    widget = widget_instance(qtbot, param, **kwargs)
    assert widget.isVisible() is True
    assert abs(widget.width() - qapp.font_char_width * 50) < 3


@pytest.mark.gui
@pytest.mark.parametrize("dtype, default, new_value", _TEST_DTYPE_VAL_NEW_VALS)
def test_set_param_value(qtbot, dtype, default, new_value):
    param = Parameter("test", dtype, default, name="Test param")
    widget = widget_instance(qtbot, param)
    assert widget.param.value == default
    assert widget.display_value == str(default)
    widget.io_widget.setFocus()
    qtbot.waitUntil(lambda: widget.io_widget.hasFocus(), timeout=500)
    widget.io_widget.update_widget_value(str(new_value))
    widget.io_widget.clearFocus()
    qtbot.waitUntil(lambda: widget.io_widget.hasFocus() is False, timeout=500)
    assert widget.param.value == new_value
    assert widget.display_value == str(new_value)
    assert widget.spy_new_value.n == 1
    assert widget.spy_value_changed.n == 1


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
def test_set_param_value__illegal_new_value(qtbot, dtype, default, new_value):
    param = Parameter("test", dtype, default, name="Test param")
    widget = widget_instance(qtbot, param)
    assert widget.param.value == default
    assert widget.display_value == str(default)
    with pytest.raises((ValueError, UserConfigError)):
        widget.set_param_value(new_value)
    assert widget.param.value == default
    assert widget.display_value == str(default)
    assert widget.spy_new_value.n == 0
    assert widget.spy_value_changed.n == 0


@pytest.mark.gui
@pytest.mark.parametrize("dtype, default, new_value", _TEST_DTYPE_VAL_NEW_VALS)
def test_update_display_value(qtbot, dtype, default, new_value):
    param = Parameter("test", dtype, default, name="Test param")
    widget = widget_instance(qtbot, param)
    widget.update_display_value(new_value)
    assert param.value == default
    assert widget.display_value == str(new_value)
    assert widget.spy_new_value.n == 0
    assert widget.spy_value_changed.n == 0


@pytest.mark.gui
@pytest.mark.parametrize("dtype, default, new_value", _TEST_DTYPE_VAL_NEW_VALS)
def test_set_value(qtbot, dtype, default, new_value):
    param = Parameter("test", dtype, default, name="Test param")
    widget = widget_instance(qtbot, param)
    with qtbot.waitSignal(widget.sig_new_value, timeout=500):
        widget.set_value(new_value)
    qtbot.wait(5)  # wait for signal processing
    assert param.value == new_value
    assert widget.display_value == str(new_value)
    assert widget.spy_new_value.n == 1
    assert widget.spy_value_changed.n == 1
    widget.set_value(new_value)
    qtbot.wait(5)  # wait for signal processing
    assert widget.spy_new_value.n == 1
    assert widget.spy_value_changed.n == 1


@pytest.mark.gui
@pytest.mark.parametrize("selection", ["A", "B", "C"])
def test_update_choices_from_param(qtbot, selection):
    param = Parameter("test", str, "D", choices=["D", "E", "F"])
    widget = widget_instance(qtbot, param)
    param.update_value_and_choices(selection, choices=["A", "B", "C"])
    print(widget.io_widget.current_choices)
    widget.update_choices_from_param()
    qtbot.wait(5)  # wait for signal processing
    assert widget.io_widget.current_choices == ["A", "B", "C"]
    assert widget.param.choices == ["A", "B", "C"]
    assert widget.display_value == selection
    assert widget.spy_new_value.n == 0
    assert widget.spy_value_changed.n == 0


if __name__ == "__main__":
    pytest.main([])

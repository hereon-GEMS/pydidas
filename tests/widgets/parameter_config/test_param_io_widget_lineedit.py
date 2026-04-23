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

"""
Module with unittests for pydidas.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"

import os
from numbers import Integral, Real
from typing import Any

import numpy as np
import pytest
from qtpy import QtCore, QtGui

from pydidas.core import Parameter
from pydidas.core.constants import QT_REG_EXP_FLOAT_VALIDATOR, QT_REG_EXP_INT_VALIDATOR
from pydidas.unittest_objects import SignalSpy
from pydidas.widgets.parameter_config.param_io_widget_lineedit import (
    ParamIoWidgetLineEdit,
)
from pydidas_qtcore import PydidasQApplication


param_int = Parameter("test_int", int, 5, name="Test Int")
param_int_w_None = Parameter(
    "test_int_none", int, 0, name="Test Int  None", allow_None=True
)
param_float = Parameter("test_float", float, 0, name="Test Float")
param_float_w_None = Parameter(
    "test_float_none", float, 0.0, name="Test Float None", allow_None=True
)
param_str = Parameter("test_str", str, "default", name="Test Str")

_PARAM_LIST = [param_int, param_int_w_None, param_float, param_float_w_None, param_str]


def widget_instance(qtbot, param, **kwargs: Any):
    widget = ParamIoWidgetLineEdit(param, **kwargs)
    widget.spy_new_value = SignalSpy(widget.sig_new_value)
    widget.spy_value_changed = SignalSpy(widget.sig_value_changed)
    qtbot.add_widget(widget)
    widget.show()
    widget.setFocus()
    if os.environ.get("QT_QPA_PLATFORM") == "offscreen":
        qtbot.wait(5)  # wait for signals to be processed
    else:
        qtbot.waitUntil(lambda: widget.hasFocus(), timeout=2000)
    return widget


@pytest.fixture(autouse=True)
def _cleanup():
    yield
    for _param in _PARAM_LIST:
        _param.restore_default()
    app = PydidasQApplication.instance()
    for widget in [
        _w for _w in app.topLevelWidgets() if isinstance(_w, ParamIoWidgetLineEdit)
    ]:
        widget.deleteLater()
    app.processEvents()


@pytest.mark.gui
@pytest.mark.parametrize("param", _PARAM_LIST)
@pytest.mark.parametrize("precision", [None, 4])
def test__creation(qtbot, param, precision):
    widget = widget_instance(qtbot, param, precision=precision)
    assert isinstance(widget, ParamIoWidgetLineEdit)
    if param.dtype == Real and precision is not None:
        assert widget._precision == precision
    else:
        assert widget._precision is None
    assert hasattr(widget, "sig_new_value")
    assert hasattr(widget, "sig_value_changed")
    assert widget.current_text == str(param.value)

    if param.dtype == str:
        assert widget.validator() is None
    elif param.dtype == Integral and param.allow_None:
        assert widget.validator() == QT_REG_EXP_INT_VALIDATOR
    elif param.dtype == Integral:
        assert isinstance(widget.validator(), QtGui.QIntValidator)
    elif param.dtype == Real and param.allow_None:
        assert widget.validator() == QT_REG_EXP_FLOAT_VALIDATOR
    elif param.dtype == Real:
        assert isinstance(widget.validator(), QtGui.QDoubleValidator)
    else:
        raise TypeError("Unhandled test case")


@pytest.mark.gui
def test_current_text(qtbot):
    param_str.value = "new test value"
    widget = widget_instance(qtbot, param_str)
    assert widget.current_text == param_str.value


@pytest.mark.gui
@pytest.mark.parametrize("precision", [None, 2, 13])
def test_current_text__w_precision(qtbot, precision):
    _value = 1.234573532424162344
    param = param_float.copy()
    param.value = _value
    widget = widget_instance(qtbot, param, precision=precision)
    assert widget._linked_param.value == _value
    _expected = np.round(_value, precision) if precision is not None else _value
    assert float(widget.text()) == _expected
    assert float(widget.current_text) == _value


@pytest.mark.gui
@pytest.mark.parametrize("precision", [None, 2, 13])
@pytest.mark.parametrize(
    "value", [1.234573532424162344, np.nan, np.inf, None, "None", "nan"]
)
def test_set_text__w_precision(qtbot, precision, value):
    widget = widget_instance(qtbot, param_float_w_None, precision=precision)
    widget.setText(value)
    widget.clearFocus()
    if value in [None, "None"]:
        assert widget.text() == "None"
        assert widget.current_text == "None"
        widget.spy_new_value.results[0][0] is None
    elif value in [np.nan, "nan"]:
        assert widget.text() == "nan"
        assert widget.current_text == "nan"
        assert widget.spy_new_value.results == [["nan"]]
    elif value is np.inf:
        assert widget.text() == "inf"
        assert widget.current_text == "inf"
        assert widget.spy_new_value.results == [["inf"]]
    else:
        _expected = np.round(value, precision) if precision is not None else value
        assert float(widget.text()) == _expected
        assert widget.current_text == str(value)
        assert widget.spy_new_value.results == [[str(value)]]


@pytest.mark.gui
@pytest.mark.parametrize("param, value", [[param_str, "new val"], [param_int, -7]])
def test__setText__w_non_float_and_precision(qtbot, param, value):
    widget = widget_instance(qtbot, param, precision=4)
    widget.setText(value)
    assert widget.text() == str(value)


@pytest.mark.gui
def test__editing_finished(qtbot):
    param = Parameter("test_int", int, 5, name="Test Int")
    widget = widget_instance(qtbot, param)
    widget.setText("10")
    qtbot.keyPress(widget, QtCore.Qt.Key.Key_Enter)
    qtbot.wait(5)  # wait for signals to be processed
    assert widget.current_text == "10"
    assert widget.spy_new_value.n == 1
    assert widget.spy_value_changed.n == 1
    assert widget.spy_new_value.results == [["10"]]


@pytest.mark.gui
def test__lost_focus(qtbot):
    param = Parameter("test_int", int, 5, name="Test Int")
    widget = widget_instance(qtbot, param)
    widget.setText("10")
    if os.environ.get("QT_QPA_PLATFORM") == "offscreen":
        widget.editingFinished.emit()
    else:
        widget.clearFocus()
    qtbot.wait(5)  # wait for signals to be processed
    assert widget.current_text == "10"
    assert widget.spy_new_value.n == 1
    assert widget.spy_value_changed.n == 1
    assert widget.spy_new_value.results == [["10"]]


@pytest.mark.gui
def test_update_display_value(qtbot):
    param = Parameter("test_float", float, 0.0, name="Test Float")
    widget = widget_instance(qtbot, param)
    widget.update_display_value(3.14159)
    assert widget.spy_new_value.n == 0
    assert widget.current_text == "3.14159"


if __name__ == "__main__":
    pytest.main([])

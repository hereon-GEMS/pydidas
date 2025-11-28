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


from numbers import Integral

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


def widget_instance(qtbot, param):
    param.restore_default()
    widget = ParamIoWidgetLineEdit(param)
    widget.spy_new_value = SignalSpy(widget.sig_new_value)
    widget.spy_value_changed = SignalSpy(widget.sig_value_changed)
    widget.show()
    widget.setFocus()
    qtbot.add_widget(widget)
    qtbot.waitUntil(lambda: widget.hasFocus(), timeout=1000)
    return widget


@pytest.fixture(autouse=True)
def _cleanup():
    yield
    app = PydidasQApplication.instance()
    for widget in [
        _w for _w in app.topLevelWidgets() if isinstance(_w, ParamIoWidgetLineEdit)
    ]:
        widget.deleteLater()
    app.processEvents()


@pytest.mark.gui
@pytest.mark.parametrize("param", _PARAM_LIST)
def test__creation(qtbot, param):
    widget = widget_instance(qtbot, param)
    assert isinstance(widget, ParamIoWidgetLineEdit)
    assert hasattr(widget, "sig_new_value")
    assert hasattr(widget, "sig_value_changed")
    assert widget.current_text == str(param.value)
    if param.dtype == str:
        assert widget.validator() is None
    elif param.dtype == Integral and param.allow_None:
        assert widget.validator() == QT_REG_EXP_INT_VALIDATOR
    elif param.dtype == Integral:
        assert isinstance(widget.validator(), QtGui.QIntValidator)
    elif param.dtype == float and param.allow_None:
        assert widget.validator() == QT_REG_EXP_FLOAT_VALIDATOR
    elif param.dtype == float:
        assert isinstance(widget.validator(), QtGui.QDoubleValidator)


@pytest.mark.gui
def test_current_text(qtbot):
    param_str.value = "new test value"
    widget = widget_instance(qtbot, param_str)
    assert widget.current_text == param_str.value


@pytest.mark.gui
def test__editing_finished(qtbot):
    param = Parameter("test_int", int, 5, name="Test Int")
    widget = widget_instance(qtbot, param)
    widget.setText("10")
    qtbot.keyPress(widget, QtCore.Qt.Key.Key_Enter)
    assert widget.current_text == "10"
    assert widget.spy_new_value.n == 1
    assert widget.spy_value_changed.n == 1
    assert widget.spy_new_value.results == [["10"]]


@pytest.mark.gui
def test__lost_focus(qtbot):
    param = Parameter("test_int", int, 5, name="Test Int")
    widget = widget_instance(qtbot, param)
    widget.setText("10")
    widget.clearFocus()
    assert widget.current_text == "10"
    assert widget.spy_new_value.n == 1
    assert widget.spy_value_changed.n == 1
    assert widget.spy_new_value.results == [["10"]]


@pytest.mark.gui
def test__update_widget_value(qtbot):
    param = Parameter("test_float", float, 0.0, name="Test Float")
    widget = widget_instance(qtbot, param)
    widget.update_widget_value(3.14159)
    assert widget.spy_new_value.n == 0
    assert widget.current_text == "3.14159"


if __name__ == "__main__":
    pytest.main([])

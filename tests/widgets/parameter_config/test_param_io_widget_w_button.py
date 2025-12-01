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


import pytest
from qtpy import QtCore, QtGui

from pydidas.core import Parameter
from pydidas.unittest_objects import SignalSpy
from pydidas.widgets import get_pyqt_icon_from_str
from pydidas.widgets.parameter_config.param_io_widget_with_button import (
    ParamIoWidgetWithButton,
)
from pydidas_qtcore import PydidasQApplication


param = Parameter("test", str, "item", name="Test param")


@pytest.fixture(autouse=True)
def _cleanup():
    yield
    app = PydidasQApplication.instance()
    for widget in [
        _w for _w in app.topLevelWidgets() if isinstance(_w, ParamIoWidgetWithButton)
    ]:
        widget.deleteLater()
    app.processEvents()


@pytest.fixture
def widget(qtbot):
    _standard_button_func = ParamIoWidgetWithButton.button_function

    def dummy_button_function(widget):
        widget.button_clicked = True

    ParamIoWidgetWithButton.button_function = dummy_button_function
    param.restore_default()
    widget = ParamIoWidgetWithButton(param)
    widget.button_clicked = False
    widget.spy_new_value = SignalSpy(widget.sig_new_value)
    widget.spy_value_changed = SignalSpy(widget.sig_value_changed)
    widget.show()
    qtbot.add_widget(widget)
    qtbot.wait_until(lambda: widget.isVisible(), timeout=500)
    yield widget
    ParamIoWidgetWithButton.button_function = _standard_button_func
    widget.deleteLater()


@pytest.mark.gui
def test__creation(widget):
    assert isinstance(widget, ParamIoWidgetWithButton)
    assert hasattr(widget, "sig_new_value")
    assert hasattr(widget, "sig_value_changed")
    assert widget._io_lineedit.text() == param.value


@pytest.mark.gui
@pytest.mark.parametrize(
    "icon",
    [None, get_pyqt_icon_from_str("pydidas::generic_copy"), "pydidas::generic_copy"],
)
def test__creation__w_icon(icon):
    widget = ParamIoWidgetWithButton(param, button_icon=icon)
    assert isinstance(widget, ParamIoWidgetWithButton)
    assert isinstance(widget._button.icon(), QtGui.QIcon)


@pytest.mark.gui
def test_button_function():
    widget = ParamIoWidgetWithButton(param)
    with pytest.raises(NotImplementedError):
        widget.button_function()


@pytest.mark.gui
def test__button_click(qtbot, widget):
    qtbot.mouseClick(widget._button, QtCore.Qt.LeftButton)
    assert widget.button_clicked


@pytest.mark.gui
def test_current_text(widget):
    widget._io_lineedit.setText("sample_text")
    assert widget.current_text == "sample_text"


@pytest.mark.gui
@pytest.mark.parametrize("text", ["", "sample_text", 123, 42.1])
def test_update_widget_value(widget, text):
    widget.update_widget_value(text)
    assert widget._io_lineedit.text() == str(text)
    assert widget.spy_new_value.n == 0
    assert widget.spy_value_changed.n == 0


@pytest.mark.gui
def test__editing_finished(qtbot, widget):
    widget._io_lineedit.setText("10")
    qtbot.keyPress(widget._io_lineedit, QtCore.Qt.Key.Key_Enter)
    assert widget.current_text == "10"
    assert widget.spy_new_value.n == 1
    assert widget.spy_value_changed.n == 1
    assert widget.spy_new_value.results == [["10"]]


@pytest.mark.gui
def test__lost_focus(widget):
    widget._io_lineedit.setFocus()
    widget._io_lineedit.setText("10")
    widget._io_lineedit.clearFocus()
    assert widget.current_text == "10"
    assert widget.spy_new_value.n == 1
    assert widget.spy_value_changed.n == 1
    assert widget.spy_new_value.results == [["10"]]


if __name__ == "__main__":
    pytest.main([])

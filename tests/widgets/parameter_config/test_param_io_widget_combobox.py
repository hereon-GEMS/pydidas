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

from pydidas.core import Parameter
from pydidas.core.constants import ASCII_TO_UNI
from pydidas.unittest_objects import SignalSpy
from pydidas.widgets.parameter_config.param_io_widget_combobox import (
    ParamIoWidgetComboBox,
)
from pydidas_qtcore import PydidasQApplication


_PARAM_CHOICES = ["value", "B", "C", "Tau", "Mu", "gamma", "Angstrom"]
_UNICODE_CHOICES = [
    (ASCII_TO_UNI[item] if item in ASCII_TO_UNI else item) for item in _PARAM_CHOICES
]
_NEW_CHOICES = ["Mu", "value", "1.2 um"]


@pytest.fixture(scope="module")
def param():
    return Parameter("test", str, "value", name="Test name", choices=_PARAM_CHOICES)


@pytest.fixture(autouse=True)
def _cleanup():
    yield
    app = PydidasQApplication.instance()
    for widget in [
        _w for _w in app.topLevelWidgets() if isinstance(_w, ParamIoWidgetComboBox)
    ]:
        widget.deleteLater()
    app.processEvents()


@pytest.fixture
def widget(qtbot, param):
    widget = ParamIoWidgetComboBox(param)
    widget.spy_new_value = SignalSpy(widget.sig_new_value)
    widget.spy_value_changed = SignalSpy(widget.sig_value_changed)
    widget.show()
    qtbot.add_widget(widget)
    qtbot.wait_until(lambda: widget.isVisible(), timeout=500)
    return widget


@pytest.mark.gui
def test__creation(widget, param):
    assert isinstance(widget, ParamIoWidgetComboBox)
    assert hasattr(widget, "sig_new_value")
    assert hasattr(widget, "sig_value_changed")
    assert [widget.itemText(i) for i in range(widget.count())] == _UNICODE_CHOICES
    assert widget.current_text == param.value
    widget.setCurrentText("\u03a4")  # Tau
    assert widget.current_text == "Tau"
    assert widget.currentText() == "\u03a4"


@pytest.mark.gui
def test__creation__w_value_selected():
    param = Parameter("test", str, "B", choices=["A", "B", "C"])
    widget = ParamIoWidgetComboBox(param)
    assert widget.current_text == "B"
    assert widget.current_choices == param.choices


@pytest.mark.gui
@pytest.mark.parametrize(
    "index, item", [(index, item) for index, item in enumerate(_UNICODE_CHOICES)]
)
def test_current_text(widget, index, item):
    widget.setCurrentIndex(index)
    assert widget.currentText() == item
    assert widget.current_text == _PARAM_CHOICES[index]


@pytest.mark.gui
@pytest.mark.parametrize(
    "index, new_value", [(_i, _v) for _i, _v in enumerate(_PARAM_CHOICES)]
)
def test_update_widget_value(widget, index, new_value):
    widget.update_widget_value(new_value)
    assert widget.current_text == new_value
    assert widget.currentText() == _UNICODE_CHOICES[index]
    assert widget.spy_new_value.n == 0
    assert widget.spy_value_changed.n == 0


@pytest.mark.gui
@pytest.mark.parametrize("value", [0, 1])
def test_update_widget_value__w_bool(widget, value):
    widget.update_choices(["True", "False", "other"])
    widget.update_widget_value(value)
    assert widget.current_text == ("True" if value else "False")


@pytest.mark.gui
@pytest.mark.parametrize("emit_signal", [True, False])
@pytest.mark.parametrize("selection", [None, "invalid"] + _NEW_CHOICES)
def test_update_choices(widget, emit_signal, selection):
    _new_item = selection != widget.current_text
    _new_choice = selection if selection in _NEW_CHOICES else _NEW_CHOICES[0]
    assert widget.spy_value_changed.n == 0
    assert widget.current_choices == _PARAM_CHOICES
    widget.update_choices(_NEW_CHOICES, selection=selection, emit_signal=emit_signal)
    assert widget.spy_value_changed.n == (emit_signal and _new_item)
    if emit_signal and _new_item:
        assert widget.spy_new_value.results[0] == [_new_choice]
    assert widget.current_text == _new_choice
    assert widget.current_choices == _NEW_CHOICES


if __name__ == "__main__":
    pytest.main([])

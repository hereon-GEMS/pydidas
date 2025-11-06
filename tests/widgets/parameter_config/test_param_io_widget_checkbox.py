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
from pydidas.unittest_objects import SignalSpy
from pydidas.widgets.parameter_config.param_io_widget_checkbox import (
    ParamIoWidgetCheckBox,
)
from pydidas_qtcore import PydidasQApplication


@pytest.fixture(scope="module")
def param():
    return Parameter("test", bool, True, name="Test name", choices=[True, False])


@pytest.fixture(scope="module", autouse=True)
def _cleanup():
    yield
    app = PydidasQApplication.instance()
    for widget in [
        _w for _w in app.topLevelWidgets() if isinstance(_w, ParamIoWidgetCheckBox)
    ]:
        widget.deleteLater()
    app.processEvents()


@pytest.fixture
def widget(qtbot, param):
    widget = ParamIoWidgetCheckBox(param)
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
    widget = ParamIoWidgetCheckBox(param)
    widget.show()
    qtbot.add_widget(widget)
    qtbot.wait_until(lambda: widget.isVisible(), timeout=500)
    return widget


@pytest.mark.gui
def test__creation(widget, param, spy_value_changed):
    assert isinstance(widget, ParamIoWidgetCheckBox)
    assert hasattr(widget, "sig_new_value")
    assert hasattr(widget, "sig_value_changed")
    assert widget.isEnabled()
    assert widget.text() == param.name
    assert spy_value_changed.n == 0


@pytest.mark.gui
@pytest.mark.parametrize(
    "local_param",
    [
        Parameter("entry", bool, True, choices=[True], name="A / B"),
        Parameter("entry", bool, False, choices=[False], name="test"),
    ],
)
def test__creation__w_one_choice_entry(qtbot, local_param):
    widget = widget_with_param(qtbot, local_param)
    assert isinstance(widget, ParamIoWidgetCheckBox)
    assert not widget.isEnabled()
    assert widget.text() == local_param.name
    assert widget.isChecked() == local_param.value


@pytest.mark.gui
@pytest.mark.parametrize("checked", [True, False])
def test_current_text(widget, param, checked):
    widget.update_widget_value(checked)
    assert widget.current_text == ("True" if checked else "False")


if __name__ == "__main__":
    pytest.main([])

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

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"

import numpy as np
import pytest
from qtpy import QtCore, QtTest, QtWidgets

from pydidas import IS_QT6
from pydidas.widgets.silx_plot.data_viewer.data_axis_selector import DataAxisSelector
from pydidas_qtcore import PydidasQApplication


@pytest.fixture(scope="module")
def app():
    app = PydidasQApplication([])
    yield app
    app.quit()


@pytest.fixture
def selector(request):
    _kwargs = getattr(request, "param", {})
    index = _kwargs.get("index", 0)
    _selector = DataAxisSelector(index)
    yield _selector
    _selector.deleteLater()


@pytest.fixture
def spy_display_choice(selector):
    return QtTest.QSignalSpy(selector.sig_display_choice_changed)


@pytest.fixture
def spy_new_slicing(selector):
    return QtTest.QSignalSpy(selector.sig_new_slicing)


def _get_spy_results(spy):
    if IS_QT6:
        return [spy.at(i) for i in range(spy.count())]
    else:
        return [spy[i] for i in range(len(spy))]


def test_init(selector):
    assert selector._data_range is None
    assert selector._data_unit == ""
    assert selector._data_label == ""
    assert selector._current_index == 0
    for _widget in ["label_axis", "combo_axis_use"]:
        assert isinstance(selector._widgets[_widget], QtWidgets.QWidget)


def test_npoints(selector):
    selector._npoints = 42
    assert selector.npoints == 42


def test_display_choice(selector):
    selector.define_additional_choices("choice1;;choice2")
    selector._widgets["combo_axis_use"].setCurrentText("choice2")
    assert selector.display_choice == "choice2"


def test_display_choice_setter(selector):
    selector.define_additional_choices("choice1;;choice2")
    selector.display_choice = "choice1"
    assert selector._widgets["combo_axis_use"].currentText() == "choice1"


def test_display_choice_setter__invalid(selector):
    selector.define_additional_choices("choice1;;choice2")
    with pytest.raises(ValueError):
        selector.display_choice = "choice3"


@pytest.mark.parametrize(
    "testcase", ["slice at index", "slice at data value", "choice1"]
)
def test_current_slice(selector, testcase):
    _result = slice(None) if testcase == "choice1" else slice(5, 6)
    selector._current_index = 5
    selector.set_axis_metadata(np.arange(10), "dummy", "unit")
    selector.define_additional_choices("choice1")
    selector.display_choice = testcase
    assert selector.current_slice == _result


def test_set_axis_metadata(selector):
    axis = np.arange(10)
    unit = "m"
    label = "Distance"
    selector.set_axis_metadata(axis, label, unit)
    assert np.array_equal(selector._data_range, axis)
    assert selector._data_label == label
    assert selector._data_unit == unit


def test_set_axis_metadata__no_data_range_no_npoints(selector):
    with pytest.raises(ValueError):
        selector.set_axis_metadata(None, "distance", "m")


def test_set_axis_metadata__no_data_range(selector):
    selector.set_axis_metadata(None, "distance", "m", npoints=42)
    assert selector._npoints == 42
    assert selector._data_range is None
    assert selector._data_unit == ""
    assert selector._data_label == ""


def test_define_additional_choices(selector):
    choices = "choice1;;choice2"
    selector.define_additional_choices(choices)
    expected_choices = ["slice at index", "choice1", "choice2"]
    combo_items = [
        selector._widgets["combo_axis_use"].itemText(i)
        for i in range(selector._widgets["combo_axis_use"].count())
    ]
    assert combo_items == expected_choices


def test_define_additional_choices__w_data_range_set(selector):
    selector.set_axis_metadata(np.arange(10), "dummy", "unit")
    choices = "choice1;;choice2"
    selector.define_additional_choices(choices + ";;choice3")
    selector.define_additional_choices(choices)
    expected_choices = [
        "slice at index",
        "slice at data value",
        "choice1",
        "choice2",
    ]
    combo_items = [
        selector._widgets["combo_axis_use"].itemText(i)
        for i in range(selector._widgets["combo_axis_use"].count())
    ]
    assert combo_items == expected_choices


@pytest.mark.parametrize(
    "choice", ["slice at index", "slice at data value", "choice1", "choice2"]
)
def test_axis_use_changed(selector, choice):
    selector.show()
    selector.set_axis_metadata(np.arange(10), "dummy", "unit")
    selector.define_additional_choices("choice1;;choice2")
    selector._axis_use_changed(choice)
    assert selector._widgets["edit_index"].isVisible() == (choice == "slice at index")
    assert selector._widgets["edit_data"].isVisible() == (
        choice == "slice at data value"
    )
    assert selector._widgets["label_unit"].isVisible() == (
        choice == "slice at data value"
    )
    assert selector._widgets["slider"].isVisible() == (
        choice in ["slice at data value", "slice at index"]
    )


@pytest.mark.parametrize("selector", [{"index": 7}], indirect=True)
def test_slider_changed(selector, spy_new_slicing):
    _range = 0.75 * np.arange(20) - 5
    _pos = 5
    selector.show()
    selector.set_axis_metadata(_range, "dummy", "unit")
    selector._widgets["slider"].setSliderPosition(_pos)
    _results = _get_spy_results(spy_new_slicing)
    assert _results[0][0] == 7
    assert _results[0][1] == str(_pos)
    assert selector._widgets["edit_index"].text() == str(_pos)
    assert selector._widgets["edit_data"].text() == f"{_range[_pos]:.4f}"


@pytest.mark.parametrize("selector", [{"index": 6}], indirect=True)
@pytest.mark.parametrize("case", [[-3, 0], [0, 5], [1, -1]])
def test_manual_index_changed(selector, spy_new_slicing, case):
    _range = 0.75 * np.arange(20) - 5
    _range_index = np.mod(case[1], _range.size)
    _input = _range_index + case[0]
    selector.set_axis_metadata(_range, "dummy", "unit")
    with QtCore.QSignalBlocker(selector._widgets["edit_index"]):
        selector._widgets["edit_index"].setText(str(_input))
    selector._manual_index_changed()
    assert selector._widgets["slider"].sliderPosition() == _range_index
    assert selector._widgets["edit_data"].text() == f"{_range[_range_index]:.4f}"
    assert selector._widgets["edit_index"].text() == str(_range_index)
    _results = _get_spy_results(spy_new_slicing)
    assert _results[0] == [6, str(_range_index)]


@pytest.mark.parametrize("selector", [{"index": 42}], indirect=True)
@pytest.mark.parametrize("case", [[-3, 0], [0, 5], [1, -1]])
def test_manual_data_value_changed(selector, spy_new_slicing, case):
    _range = 0.75 * np.arange(20) - 5
    _range_index = np.mod(case[1], _range.size)
    _expectation = _range[_range_index]
    _value = _range[_range_index] + case[0]
    selector.set_axis_metadata(_range, "dummy", "unit")
    with QtCore.QSignalBlocker(selector._widgets["edit_data"]):
        selector._widgets["edit_data"].setText(str(_value))
    selector._manual_data_value_changed()
    assert selector._widgets["slider"].sliderPosition() == np.mod(
        _range_index, _range.size
    )
    assert selector._widgets["edit_data"].text() == f"{_expectation:.4f}"
    assert selector._widgets["edit_index"].text() == str(_range_index)
    _results = _get_spy_results(spy_new_slicing)
    assert _results[0] == [42, str(_range_index)]


def test_move_to_index__no_change(selector, spy_new_slicing):
    _range = 0.75 * np.arange(20) - 5
    _axindex = 6
    selector.set_axis_metadata(_range, "dummy", "unit")
    selector._current_index = 7
    selector._move_to_index(7)
    _results = _get_spy_results(spy_new_slicing)
    assert _results == []


@pytest.mark.parametrize("selector", [{"index": 12}], indirect=True)
def test_move_to_index(selector, spy_new_slicing):
    _range = 0.75 * np.arange(20) - 5
    _index = 7
    selector.set_axis_metadata(_range, "dummy", "unit")
    selector._move_to_index(_index)
    _results = _get_spy_results(spy_new_slicing)
    assert _results[0] == [12, str(_index)]
    assert selector._widgets["slider"].sliderPosition() == _index
    assert selector._widgets["edit_data"].text() == f"{_range[_index]:.4f}"
    assert selector._widgets["edit_index"].text() == str(_index)


if __name__ == "__main__":
    pytest.main()

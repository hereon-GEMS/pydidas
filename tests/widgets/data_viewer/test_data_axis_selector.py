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
from pydidas.core import UserConfigError
from pydidas.widgets.data_viewer.data_axis_selector import (
    _GENERIC_CHOICES,
    DataAxisSelector,
)
from pydidas_qtcore import PydidasQApplication


_DATA_RANGE = 0.4 * np.arange(20) - 5


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
def data_range():
    return _DATA_RANGE.copy()


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
    assert selector._current_slice == slice(0, 1)
    for _widget in ["label_axis", "combo_axis_use"]:
        assert isinstance(selector._widgets[_widget], QtWidgets.QWidget)


def test_npoints(selector):
    selector._npoints = 42
    assert selector.npoints == 42


def test_available_choices(selector):
    assert selector.available_choices == ["slice at index"]


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


def test_current_slice(selector):
    selector._current_slice = slice(4, 6)
    selector.set_axis_metadata(np.arange(10), "dummy", "unit")
    assert selector.current_slice == slice(4, 6)


def test_set_axis_metadata(selector, data_range):
    unit = "m"
    label = "Distance"
    selector.set_axis_metadata(data_range, label, unit)
    assert np.array_equal(selector._data_range, _DATA_RANGE)
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
    expected_choices = [
        "slice at index",
        "choice1",
        "choice2",
    ]
    combo_items = [
        selector._widgets["combo_axis_use"].itemText(i)
        for i in range(selector._widgets["combo_axis_use"].count())
    ]
    assert combo_items == expected_choices


def test_define_additional_choices__w_data_range_set(selector, data_range):
    selector.set_axis_metadata(data_range, "dummy", "unit")
    choices = "choice1;;choice2"
    selector.define_additional_choices(choices + ";;choice3")
    selector.define_additional_choices(choices)
    expected_choices = _GENERIC_CHOICES + ["choice1", "choice2"]
    combo_items = [
        selector._widgets["combo_axis_use"].itemText(i)
        for i in range(selector._widgets["combo_axis_use"].count())
    ]
    assert combo_items == expected_choices


@pytest.mark.parametrize("slicing_choice", _GENERIC_CHOICES)
@pytest.mark.parametrize("choice", _GENERIC_CHOICES + ["choice1", "choice2"])
def test_handle_new_axis_use(
    selector, data_range, choice, slicing_choice, spy_display_choice, spy_new_slicing
):
    selector.show()
    selector.set_axis_metadata(data_range, "dummy", "unit")
    selector.define_additional_choices("choice1;;choice2")
    selector._handle_new_axis_use(slicing_choice)
    selector._handle_new_axis_use(choice)
    assert selector._widgets["edit_index"].isVisible() == (choice == "slice at index")
    assert selector._widgets["edit_data"].isVisible() == (
        choice == "slice at data value"
    )
    assert selector._widgets["label_unit"].isVisible() == (
        choice == "slice at data value"
    )
    assert selector._widgets["slider"].isVisible() == (choice in _GENERIC_CHOICES)
    if choice not in _GENERIC_CHOICES:
        assert selector._last_slicing_at_index == (slicing_choice == "slice at index")
    _display_res = _get_spy_results(spy_display_choice)
    _slicing_res = _get_spy_results(spy_new_slicing)
    assert len(_display_res) == 2
    assert _display_res[0][1] == slicing_choice
    assert _display_res[1][1] == choice
    assert len(_slicing_res) == 0


@pytest.mark.parametrize("selector", [{"index": 7}], indirect=True)
def test_slider_changed(selector, data_range, spy_new_slicing):
    _pos = 5
    selector.show()
    selector.set_axis_metadata(data_range, "dummy", "unit")
    selector._widgets["slider"].setSliderPosition(_pos)
    _results = _get_spy_results(spy_new_slicing)
    assert _results[0][0] == 7
    assert _results[0][1] == f"{_pos}:{_pos + 1}"
    assert selector._widgets["edit_index"].text() == str(_pos)
    assert selector._widgets["edit_data"].text() == f"{data_range[_pos]:.4f}"


@pytest.mark.parametrize("selector", [{"index": 6}], indirect=True)
@pytest.mark.parametrize("case", [[-3, 0], [0, 5], [1, -1]])
def test_manual_index_changed(selector, data_range, spy_new_slicing, case):
    _range_index = np.mod(case[1], data_range.size)
    _input = _range_index + case[0]
    selector.set_axis_metadata(data_range, "dummy", "unit")
    with QtCore.QSignalBlocker(selector._widgets["edit_index"]):
        selector._widgets["edit_index"].setText(str(_input))
    selector._manual_index_changed()
    assert selector._widgets["slider"].sliderPosition() == _range_index
    assert selector._widgets["edit_data"].text() == f"{data_range[_range_index]:.4f}"
    assert selector._widgets["edit_index"].text() == str(_range_index)
    _results = _get_spy_results(spy_new_slicing)
    assert _results[0] == [6, f"{_range_index}:{_range_index + 1}"]


@pytest.mark.parametrize("selector", [{"index": 42}], indirect=True)
@pytest.mark.parametrize("case", [[-3, 0], [0, 5], [1, -1]])
def test_manual_data_value_changed(selector, data_range, spy_new_slicing, case):
    _range_index = np.mod(case[1], data_range.size)
    _expectation = data_range[_range_index]
    _value = data_range[_range_index] + case[0]
    selector.set_axis_metadata(data_range, "dummy", "unit")
    with QtCore.QSignalBlocker(selector._widgets["edit_data"]):
        selector._widgets["edit_data"].setText(str(_value))
    selector._manual_data_value_changed()
    assert selector._widgets["slider"].sliderPosition() == np.mod(
        _range_index, data_range.size
    )
    assert selector._widgets["edit_data"].text() == f"{_expectation:.4f}"
    assert selector._widgets["edit_index"].text() == str(_range_index)
    _results = _get_spy_results(spy_new_slicing)
    assert _results[0] == [42, f"{_range_index}:{_range_index + 1}"]


def test_move_to_index__no_change(selector, data_range, spy_new_slicing):
    selector.set_axis_metadata(data_range, "dummy", "unit")
    selector._current_slice = slice(7, 8)
    selector._move_to_index(7)
    _results = _get_spy_results(spy_new_slicing)
    assert _results == []


@pytest.mark.parametrize("selector", [{"index": 12}], indirect=True)
def test_move_to_index(selector, data_range, spy_new_slicing):
    _index = 7
    selector.set_axis_metadata(data_range, "dummy", "unit")
    selector._move_to_index(_index)
    _results = _get_spy_results(spy_new_slicing)
    assert _results[0] == [12, "7:8"]
    assert selector._widgets["slider"].sliderPosition() == _index
    assert selector._widgets["edit_data"].text() == f"{data_range[_index]:.4f}"
    assert selector._widgets["edit_index"].text() == str(_index)


@pytest.mark.parametrize("testcase", [["slice at index", 3, 4]])  # ["choice1", 0, 12],
def test__slice_after_changing_selection(selector, testcase):
    choice, start, stop = testcase
    selector.set_axis_metadata(None, npoints=12)
    selector.define_additional_choices("choice1;;choice2")
    selector._current_slice = slice(0, 1)
    with QtCore.QSignalBlocker(selector._widgets["edit_index"]):
        selector._widgets["edit_index"].setText("3")
    with QtCore.QSignalBlocker(selector._widgets["combo_axis_use"]):
        selector._widgets["combo_axis_use"].setCurrentText("choice2")
    selector.display_choice = choice
    assert selector._current_slice == slice(start, stop)


@pytest.mark.parametrize(
    "axis_range_selection",
    ["use full axis", "select range by indices", "select range by data values"],
)
def test_handle_range_selection(selector, data_range, axis_range_selection):
    selector.define_additional_choices("choice1;;choice2")
    selector.set_axis_metadata(data_range, "dummy", "unit")
    selector.show()
    selector._widgets["combo_range"].setCurrentText(axis_range_selection)
    assert selector._widgets["edit_range_data"].isVisible() == (
        axis_range_selection == "select range by data values"
    )
    assert selector._widgets["edit_range_index"].isVisible() == (
        axis_range_selection == "select range by indices"
    )


@pytest.mark.parametrize(
    "input",
    [
        ["0:5", 0, 6],
        ["-5:17", 0, 18],
        ["-5:25", 0, 20],
        ["7:14", 7, 15],
        ["9:24", 9, 20],
    ],
)
def test_handle_new_index_range_selection__correct_input(
    selector, input, spy_new_slicing, data_range
):
    selector.set_axis_metadata(data_range, "dummy", "unit")
    selector._widgets["edit_range_index"].setText(input[0])
    selector._handle_new_index_range_selection()
    _results = _get_spy_results(spy_new_slicing)
    assert _results[0] == [0, f"{input[1]}:{input[2]}"]
    assert selector._current_slice == slice(input[1], input[2])
    assert selector._widgets["edit_range_index"].text() == f"{input[1]}:{input[2] - 1}"


@pytest.mark.parametrize("input", ["0:", "", ":-3", "a:5"])
def test_handle_new_index_range_selection__incorrect_input(
    selector, input, spy_new_slicing, data_range
):
    selector.set_axis_metadata(data_range, "dummy", "unit")
    selector._widgets["edit_range_index"].setText(input)
    with pytest.raises(UserConfigError):
        selector._handle_new_index_range_selection()


@pytest.mark.parametrize(
    "input",
    [
        [f"{_DATA_RANGE[0]}:{_DATA_RANGE[5]} ", 0, 6],
        [f"{_DATA_RANGE[0] - 5}:{_DATA_RANGE[5]} ", 0, 6],
        [f"{_DATA_RANGE[7] - 0.05}:{_DATA_RANGE[14] - 0.04} ", 7, 15],
        [f"{_DATA_RANGE[9] - 0.05}:{_DATA_RANGE[19] + 12} ", 9, 20],
    ],
)
def test_handle_new_data_range_selection(selector, input, spy_new_slicing, data_range):
    selector.set_axis_metadata(data_range, "dummy", "unit")
    selector._widgets["edit_range_data"].setText(input[0])
    selector._handle_new_data_range_selection()
    _results = _get_spy_results(spy_new_slicing)
    assert _results[0] == [0, f"{input[1]}:{input[2]}"]

    assert selector._current_slice == slice(input[1], input[2])
    assert (
        selector._widgets["edit_range_data"].text()
        == f"{_DATA_RANGE[input[1]]:.4f}:{_DATA_RANGE[input[2] - 1]:.4f}"
    )


@pytest.mark.parametrize("input", ["0.0:", "", ":-3.", "a:5"])
def test_handle_new_data_range_selection__incorrect_input(
    selector, input, spy_new_slicing, data_range
):
    selector.set_axis_metadata(data_range, "dummy", "unit")
    selector._widgets["edit_range_data"].setText(input)
    with pytest.raises(UserConfigError):
        selector._handle_new_data_range_selection()


if __name__ == "__main__":
    pytest.main()

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
from qtpy import QtCore, QtTest

from pydidas import IS_QT6
from pydidas.core import UserConfigError
from pydidas.unittest_objects import create_dataset
from pydidas.widgets.data_viewer import AxesSelector
from pydidas.widgets.data_viewer.data_axis_selector import (
    DataAxisSelector,
)
from pydidas_qtcore import PydidasQApplication


_DATA = create_dataset(5, dtype=float)


@pytest.fixture(scope="module")
def app():
    app = PydidasQApplication([])
    yield app
    app.quit()


@pytest.fixture
def selector(request):
    _kwargs = getattr(request, "param", {})
    _selector = AxesSelector()
    yield _selector
    _selector.deleteLater()


@pytest.fixture
def data():
    return _DATA.copy()


@pytest.fixture
def spy_new_slicing_str(selector):
    return QtTest.QSignalSpy(selector.sig_new_slicing_str_repr)


@pytest.fixture
def spy_new_slicing(selector):
    return QtTest.QSignalSpy(selector.sig_new_slicing)


def _get_spy_results(spy):
    if IS_QT6:
        return [spy.at(i) for i in range(spy.count())]
    else:
        return [spy[i] for i in range(len(spy))]


def test_init(selector):
    assert selector._axwidgets == {}
    assert selector._data_shape == ()
    assert selector._data_ndim == 0


def test_current_display_selection__empty(selector):
    assert selector.current_display_selection == ()


def test_current_display_selection__simple(selector):
    selector.set_data_shape((5, 7, 4))
    assert selector.current_display_selection == (
        "slice at index",
        "slice at index",
        "slice at index",
    )


def test_current_display_selection__w_change(selector):
    selector.set_data_shape((5, 7, 4))
    selector.set_axis_metadata(1, np.arange(12), "axis 1", "unit 1")
    selector._axwidgets[1].display_choice = "slice at data value"
    assert selector.current_display_selection == (
        "slice at index",
        "slice at data value",
        "slice at index",
    )


def test_set_data_shape__invalid_type(selector):
    with pytest.raises(UserConfigError):
        selector.set_data_shape([0, 4])


def test_set_data_shape__valid(selector):
    _shape = (5, 7, 4)
    selector.set_data_shape(_shape)
    assert selector._data_shape == (5, 7, 4)
    assert selector._data_ndim == 3
    for _dim in range(3):
        assert isinstance(selector._axwidgets[_dim], DataAxisSelector)
        assert selector._axwidgets[_dim].npoints == _shape[_dim]


def test_create_data_axis_selectors(selector):
    selector._data_shape = (5, 7, 4)
    selector._data_ndim = 3
    selector._additional_choices_str = "choice1;;choice2"
    selector._create_data_axis_selectors()
    assert len(selector._axwidgets) == selector._data_ndim
    for _dim, _len in enumerate(selector._data_shape):
        assert isinstance(selector._axwidgets[_dim], DataAxisSelector)
        assert "choice1" in selector._axwidgets[_dim].available_choices
        assert "choice2" in selector._axwidgets[_dim].available_choices


def test_create_data_axis_selectors__multiple_calls(selector):
    _raw_shape = (5, 7, 4, 8, 3, 3, 5)
    _ndim_list = [5, 3, 7, 6]
    for _index, _ndim in enumerate(_ndim_list):
        selector._data_shape = _raw_shape[:_ndim]
        selector._data_ndim = _ndim
        selector._additional_choices_str = "choice1;;choice2"
        for _item in selector._axwidgets.values():
            _item.set_axis_metadata(np.linspace(3, 7, num=_raw_shape[_index]), "", "")
            with QtCore.QSignalBlocker(_item):
                _item.display_choice = "slice at data value"
        selector._create_data_axis_selectors()
        assert len(selector._axwidgets) == max(_ndim_list[: _index + 1])
        for _dim, _len in enumerate(selector._data_shape):
            assert isinstance(selector._axwidgets[_dim], DataAxisSelector)
            assert "choice1" in selector._axwidgets[_dim].available_choices
            assert "choice2" in selector._axwidgets[_dim].available_choices
        for _dim, _item in selector._axwidgets.items():
            if _dim >= _ndim:
                assert _item.display_choice == "slice at index"


def test_set_axis_metadata(selector):
    selector.set_data_shape((5, 7, 4))
    selector.set_axis_metadata(1, np.arange(12), "axis 1", "unit 1")
    assert selector._axwidgets[1].npoints == 12
    assert "slice at data value" in selector._axwidgets[1].available_choices


def test_set_axis_metadata__invalid_axis(selector):
    selector.set_data_shape((5, 7, 4))
    with pytest.raises(UserConfigError):
        selector.set_axis_metadata(3, np.arange(12), "axis 1", "unit 1")


def test_set_axis_metadata__invalid_ndim(selector):
    selector.define_additional_choices("choice1;;choice2;;choice3")
    data = create_dataset(2, dtype=float)
    with pytest.raises(UserConfigError):
        selector.set_metadata_from_dataset(data)


def test_set_metadata_from_dataset(selector):
    selector.set_metadata_from_dataset(_DATA)
    assert selector._data_shape == _DATA.shape
    for _dim, _item in selector._axwidgets.items():
        assert _item.npoints == _DATA.shape[_dim]
        assert _item.data_label == _DATA.axis_labels[_dim]
        assert _item.data_unit == _DATA.axis_units[_dim]


def test_set_metadata_from_dataset__w_choices(selector):
    selector.define_additional_choices("choice1;;choice2")
    selector.set_metadata_from_dataset(_DATA)
    assert selector._data_shape == _DATA.shape
    assert selector.current_display_selection.count("choice1") == 1
    assert selector.current_display_selection.count("choice2") == 1
    for _dim, _item in selector._axwidgets.items():
        assert _item.npoints == _DATA.shape[_dim]
        assert _item.data_label == _DATA.axis_labels[_dim]
        assert _item.data_unit == _DATA.axis_units[_dim]


def test_set_metadata_from_dataset__no_dataset(selector):
    with pytest.raises(UserConfigError):
        selector.set_metadata_from_dataset("")


def test_define_additional_choices(selector, data):
    _choices = "choice1;;choice2"
    selector.set_metadata_from_dataset(data)
    selector.define_additional_choices(_choices)
    assert selector._additional_choices_str == _choices
    assert selector._additional_choices == _choices.split(";;")
    for _dim, _item in selector._axwidgets.items():
        assert "choice1" in _item.available_choices
        assert "choice2" in _item.available_choices


def test_define_additional_choices__no_metadata_set(selector, data):
    _choices = "choice1;;choice2"
    selector.define_additional_choices(_choices)
    assert selector._additional_choices_str == _choices
    assert selector._additional_choices == _choices.split(";;")
    for _dim, _item in selector._axwidgets.items():
        assert "choice1" in _item.available_choices
        assert "choice2" in _item.available_choices


def test_define_additional_choices__existing_choices(selector, data):
    _choices = "choice3;;choice4"
    selector.set_metadata_from_dataset(data)
    selector._additional_choices_str = "choice1;;choice2"
    selector._additional_choices = ["choice1", "choice2"]
    selector.define_additional_choices(_choices)
    assert selector._additional_choices_str == "choice3;;choice4"
    assert selector._additional_choices == _choices.split(";;")
    for _item in selector._axwidgets.values():
        assert "choice1" not in _item.available_choices
        assert "choice2" not in _item.available_choices
        assert "choice3" in _item.available_choices
        assert "choice4" in _item.available_choices


def test_define_additional_choices__values_set_in_widgets(selector, data):
    selector.set_metadata_from_dataset(data)
    selector._additional_choices = "choice1;;choice2"
    for _item in selector._axwidgets.values():
        with QtCore.QSignalBlocker(_item):
            _item.define_additional_choices("choice1;;choice2")
            _item.display_choice = "choice1"
    selector.define_additional_choices("choice3;;choice4")
    assert selector._additional_choices_str == "choice3;;choice4"
    assert selector._additional_choices == ["choice3", "choice4"]
    for _item in selector._axwidgets.values():
        assert "choice1" not in _item.available_choices
        assert "choice2" not in _item.available_choices
        assert "choice3" in _item.available_choices
        assert "choice4" in _item.available_choices
    assert selector.current_display_selection.count("choice1") == 0
    assert selector.current_display_selection.count("choice2") == 0
    assert selector.current_display_selection.count("choice3") == 1
    assert selector.current_display_selection.count("choice4") == 1


@pytest.mark.parametrize(
    "choices", ["choice1;;choice2", "choice1;;choice2;;choice3", "another_choice"]
)
@pytest.mark.parametrize(
    "set_axwidget",
    [
        [4, "choice1"],
        [2, "choice2"],
        [0, "another_choice"],
        [1, "slice at index"],
        [0, "slice at index"],
        [3, "slice at data value"],
    ],
)
def test_process_new_display_choice(selector, choices, set_axwidget, data):
    selector.set_metadata_from_dataset(data)
    selector.define_additional_choices(choices)
    if set_axwidget[1] not in choices.split(";;"):
        return
    with QtCore.QSignalBlocker(selector._axwidgets[set_axwidget[0]]):
        selector._axwidgets[set_axwidget[0]].display_choice = set_axwidget[1]
    selector._process_new_display_choice(*set_axwidget)
    _current_selection = selector.current_display_selection
    for _choice in choices.split(";;"):
        assert _current_selection.count(_choice) == 1


def test_process_new_slicing(selector, data, spy_new_slicing, spy_new_slicing_str):
    selector.set_metadata_from_dataset(data)
    selector.define_additional_choices("choice1;;choice2")
    for _dim, _item in selector._axwidgets.items():
        if _item.display_choice in ["choice1", "choice2"]:
            continue
        with QtCore.QSignalBlocker(_item):
            _item._move_to_index(data.shape[_dim] - 2)
    selector.process_new_slicing()
    assert len(_get_spy_results(spy_new_slicing)) == 1
    assert len(_get_spy_results(spy_new_slicing_str)) == 1
    for _dim, _item in selector._axwidgets.items():
        if _item.display_choice in ["choice1", "choice2"]:
            assert selector._current_slice[_dim] == slice(0, data.shape[_dim])
            assert selector._current_slice_strings[_dim] == _item.current_slice_str
        else:
            assert selector.current_slice[_dim] == slice(
                data.shape[_dim] - 2, data.shape[_dim] - 1
            )
            assert selector._current_slice_strings[_dim] == _item.current_slice_str


def test_update_ax_slicing(selector, data, spy_new_slicing, spy_new_slicing_str):
    selector.set_metadata_from_dataset(data)
    selector.define_additional_choices("choice1;;choice2")
    for _dim in selector._axwidgets:
        selector._current_slice[_dim] = slice(0, 1)
        selector._current_slice_strings[_dim] = "0:1"
    with QtCore.QSignalBlocker(selector._axwidgets[3]):
        selector._axwidgets[3]._move_to_index(3)
    assert selector._current_slice[3] == slice(0, 1)
    selector._update_ax_slicing(3, "3:4")
    assert selector._current_slice[3] == slice(3, 4)
    assert selector._current_slice_strings[3] == "3:4"
    assert len(_get_spy_results(spy_new_slicing)) == 1
    assert len(_get_spy_results(spy_new_slicing_str)) == 1
    assert "3::3:4" in _get_spy_results(spy_new_slicing_str)[0][0]


if __name__ == "__main__":
    pytest.main()

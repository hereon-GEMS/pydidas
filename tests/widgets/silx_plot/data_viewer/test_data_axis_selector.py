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


import unittest

import numpy as np
from qtpy import QtCore, QtTest, QtWidgets

from pydidas import IS_QT6
from pydidas.widgets.silx_plot.data_viewer.data_axis_selector import DataAxisSelector
from pydidas_qtcore import PydidasQApplication


class TestDataAxisSelector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = PydidasQApplication([])

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()

    def setUp(self):
        self.selector = None
        self.spy_display_choice = None
        self.spy_new_slicing = None

    def tearDown(self):
        if isinstance(self.spy_display_choice, QtTest.QSignalSpy):
            self.spy_display_choice = None
        if isinstance(self.spy_new_slicing, QtTest.QSignalSpy):
            self.spy_new_slicing = None
        if isinstance(self.selector, DataAxisSelector):
            self.selector.deleteLater()

    def create_selector(self, ax_index: int):
        self.selector = DataAxisSelector(ax_index)
        self.spy_display_choice = QtTest.QSignalSpy(
            self.selector.sig_display_choice_changed
        )
        self.spy_new_slicing = QtTest.QSignalSpy(self.selector.sig_new_slicing)
        return self.selector

    def _get_spy_results(self, spy: QtTest.QSignalSpy):
        if IS_QT6:
            return [spy.at(i) for i in range(spy.count())]
        else:
            return [spy[i] for i in range(len(spy))]

    def get_new_slicing_spy_results(self):
        return self._get_spy_results(self.spy_new_slicing)

    def get_display_choice_spy_results(self):
        return self._get_spy_results(self.spy_display_choice)

    def test_init(self):
        _selector = self.create_selector(0)
        self.assertEqual(_selector._data_range, None)
        self.assertEqual(_selector._data_unit, "")
        self.assertEqual(_selector._data_label, "")
        self.assertEqual(_selector._current_index, 0)
        for _widget in ["label_axis", "combo_axis_use"]:
            self.assertIsInstance(_selector._widgets[_widget], QtWidgets.QWidget)

    def test_npoints(self):
        _selector = self.create_selector(0)
        _selector._npoints = 42
        self.assertEqual(_selector.npoints, 42)

    def test_display_choice(self):
        _selector = self.create_selector(0)
        _selector.define_additional_choices("choice1;;choice2")
        _selector._widgets["combo_axis_use"].setCurrentText("choice2")
        self.assertEqual(_selector.display_choice, "choice2")

    def test_display_choice_setter(self):
        _selector = self.create_selector(0)
        _selector.define_additional_choices("choice1;;choice2")
        _selector.display_choice = "choice1"
        self.assertEqual(_selector._widgets["combo_axis_use"].currentText(), "choice1")

    def test_display_choice_setter__invalid(self):
        _selector = self.create_selector(0)
        _selector.define_additional_choices("choice1;;choice2")
        with self.assertRaises(ValueError):
            _selector.display_choice = "choice3"

    def test_current_slice(self):
        _selector = self.create_selector(0)
        _selector._current_index = 5
        _selector.set_axis_metadata(np.arange(10), "dummy", "unit")
        _selector.define_additional_choices("choice1")
        for _choice, _result in [
            ("slice at index", slice(5, 6)),
            ("slice at data value", slice(5, 6)),
            ("choice1", slice(None)),
        ]:
            with self.subTest(choice=_choice):
                _selector.display_choice = _choice
                self.assertEqual(_selector.current_slice, _result)

    def test_set_axis_metadata(self):
        axis = np.arange(10)
        unit = "m"
        label = "Distance"
        _selector = self.create_selector(0)
        _selector.set_axis_metadata(axis, label, unit)
        self.assertTrue(np.array_equal(_selector._data_range, axis))
        self.assertEqual(_selector._data_label, label)
        self.assertEqual(_selector._data_unit, unit)

    def test_set_axis_metadata__no_data_range_no_npoints(self):
        _selector = self.create_selector(0)
        with self.assertRaises(ValueError):
            _selector.set_axis_metadata(None, "distance", "m")

    def test_set_axis_metadata__no_data_range(self):
        _selector = self.create_selector(0)
        _selector.set_axis_metadata(None, "distance", "m", npoints=42)
        self.assertEqual(_selector._npoints, 42)
        self.assertEqual(_selector._data_range, None)
        self.assertEqual(_selector._data_unit, "")
        self.assertEqual(_selector._data_label, "")

    def test_define_additional_choices(self):
        _selector = self.create_selector(0)
        choices = "choice1;;choice2"
        _selector.define_additional_choices(choices)
        expected_choices = ["slice at index", "choice1", "choice2"]
        combo_items = [
            _selector._widgets["combo_axis_use"].itemText(i)
            for i in range(_selector._widgets["combo_axis_use"].count())
        ]
        self.assertEqual(combo_items, expected_choices)

    def test_define_additional_choices__w_data_range_set(self):
        _selector = self.create_selector(0)
        _selector.set_axis_metadata(np.arange(10), "dummy", "unit")
        choices = "choice1;;choice2"
        _selector.define_additional_choices(choices + ";;choice3")
        _selector.define_additional_choices(choices)
        expected_choices = [
            "slice at index",
            "slice at data value",
            "choice1",
            "choice2",
        ]
        combo_items = [
            _selector._widgets["combo_axis_use"].itemText(i)
            for i in range(_selector._widgets["combo_axis_use"].count())
        ]
        self.assertEqual(combo_items, expected_choices)

    def test_axis_use_changed(self):
        _selector = self.create_selector(0)
        _selector.show()
        _selector.set_axis_metadata(np.arange(10), "dummy", "unit")
        _selector.define_additional_choices("choice1;;choice2")
        for _choice in ["slice at index", "slice at data value", "choice1", "choice2"]:
            with self.subTest(choice=_choice):
                _selector._axis_use_changed(_choice)
                self.assertEqual(
                    _selector._widgets["edit_index"].isVisible(),
                    _choice == "slice at index",
                )
                self.assertEqual(
                    _selector._widgets["edit_data"].isVisible(),
                    _choice == "slice at data value",
                )
                self.assertEqual(
                    _selector._widgets["label_unit"].isVisible(),
                    _choice == "slice at data value",
                )
                self.assertEqual(
                    _selector._widgets["slider"].isVisible(),
                    _choice in ["slice at data value", "slice at index"],
                )

    def test_slider_changed(self):
        _range = 0.75 * np.arange(20) - 5
        _pos = 5
        _selector = self.create_selector(7)
        _selector.show()
        _selector.set_axis_metadata(_range, "dummy", "unit")
        _selector._widgets["slider"].setSliderPosition(_pos)
        _results = self.get_new_slicing_spy_results()
        self.assertEqual(_results[0][0], 7)
        self.assertEqual(_results[0][1], str(_pos))
        self.assertEqual(_selector._widgets["edit_index"].text(), str(_pos))
        self.assertEqual(_selector._widgets["edit_data"].text(), f"{_range[_pos]:.4f}")

    def test_manual_index_changed(self):
        _range = 0.75 * np.arange(20) - 5
        _pos = 5
        _axindex = 6
        _selector = self.create_selector(_axindex)
        _selector.set_axis_metadata(_range, "dummy", "unit")
        for _test_index, (_set, _expectation) in enumerate(
            [[-5, 0], [_pos, _pos], [25, _range.size - 1]]
        ):
            with self.subTest(entry=_set, expectation=_expectation):
                with QtCore.QSignalBlocker(_selector._widgets["edit_index"]):
                    _selector._widgets["edit_index"].setText(str(_set))
                _selector._manual_index_changed()
                self.assertEqual(
                    _selector._widgets["slider"].sliderPosition(), _expectation
                )
                self.assertEqual(
                    _selector._widgets["edit_data"].text(),
                    f"{_range[_expectation]:.4f}",
                )
                self.assertEqual(
                    _selector._widgets["edit_index"].text(), str(_expectation)
                )
                _results = self.get_new_slicing_spy_results()
                self.assertEqual(_results[_test_index][0], _axindex)
                self.assertEqual(_results[_test_index][1], str(_expectation))

    def test_manual_data_value_changed(self):
        _range = 0.75 * np.arange(20) - 5
        _pos = 5
        _axindex = 6
        _selector = self.create_selector(_axindex)
        _selector.set_axis_metadata(_range, "dummy", "unit")
        for _test_index, (_set, _expectation) in enumerate(
            [
                [_range[0] - 3, 0],
                [_range[_pos] + 0.1, _pos],
                [_range[-1] + 1, _range.size - 1],
            ]
        ):
            with self.subTest(entry=_set, expectation=_expectation):
                with QtCore.QSignalBlocker(_selector._widgets["edit_data"]):
                    _selector._widgets["edit_data"].setText(str(_set))
                _selector._manual_data_value_changed()
                self.assertEqual(
                    _selector._widgets["slider"].sliderPosition(), _expectation
                )
                self.assertEqual(
                    _selector._widgets["edit_data"].text(),
                    f"{_range[_expectation]:.4f}",
                )
                self.assertEqual(
                    _selector._widgets["edit_index"].text(), str(_expectation)
                )
                _results = self.get_new_slicing_spy_results()
                self.assertEqual(_results[_test_index][0], _axindex)
                self.assertEqual(_results[_test_index][1], str(_expectation))

    def test_move_to_index__no_change(self):
        _selector = self.create_selector(0)
        _range = 0.75 * np.arange(20) - 5
        _axindex = 6
        _selector = self.create_selector(_axindex)
        _selector.set_axis_metadata(_range, "dummy", "unit")
        _selector._current_index = 7
        _selector._move_to_index(7)
        _results = self.get_new_slicing_spy_results()
        self.assertEqual(_results, [])

    def test_move_to_index(self):
        _selector = self.create_selector(0)
        _range = 0.75 * np.arange(20) - 5
        _axindex = 6
        _index = 7
        _selector = self.create_selector(_axindex)
        _selector.set_axis_metadata(_range, "dummy", "unit")
        _selector._move_to_index(_index)
        _results = self.get_new_slicing_spy_results()
        self.assertEqual(_results[0], [_axindex, str(_index)])
        self.assertEqual(_selector._widgets["slider"].sliderPosition(), _index)
        self.assertEqual(
            _selector._widgets["edit_data"].text(), f"{_range[_index]:.4f}"
        )
        self.assertEqual(_selector._widgets["edit_index"].text(), str(_index))


if __name__ == "__main__":
    unittest.main()

# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"

import os
import random
import shutil
import string
import sys
import tempfile
import time
import unittest
from contextlib import redirect_stdout

from pydidas.core.utils import get_formatted_dict_representation
from pydidas.core.utils.str_utils import (
    convert_special_chars_to_unicode,
    convert_unicode_to_ascii,
    format_input_to_multiline_str,
    get_fixed_length_str,
    get_random_string,
    get_range_as_formatted_string,
    get_short_time_string,
    get_time_string,
    get_warning,
    print_warning,
    timed_print,
    update_separators,
)


class Test_str_utils(unittest.TestCase):
    def setUp(self):
        self.length = 20
        self._tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self._tmpdir)

    def test_get_fixed_length_str_length(self):
        self.assertEqual(len(get_fixed_length_str("test", self.length)), self.length)

    def test_get_fixed_length_str_fill_char_too_long(self):
        with self.assertRaises(TypeError):
            get_fixed_length_str("test", self.length, fill_char="..")

    def test_get_fixed_length_str_w_number(self):
        _num = 20
        _formatter = "{:.3f}"
        _str = get_fixed_length_str(
            _num, self.length, fill_char=" ", formatter=_formatter
        )
        self.assertEqual(len(_str), self.length)
        self.assertEqual(_str.strip(), _formatter.format(_num))

    def test_get_fixed_length_str_w_list(self):
        _obj = [10, 20]
        _str = get_fixed_length_str(_obj, self.length, fill_char=" ")
        self.assertEqual(len(_str), self.length)
        self.assertEqual(_str.strip(), repr(_obj))

    def test_get_fixed_length_str_w_tuple(self):
        _obj = (10, 20)
        _str = get_fixed_length_str(_obj, self.length, fill_char=" ")
        self.assertEqual(len(_str), self.length)
        self.assertEqual(_str.strip(), repr(_obj))

    def test_get_fixed_length_str_w_set(self):
        _obj = {10, 20}
        _str = get_fixed_length_str(_obj, self.length, fill_char=" ")
        self.assertEqual(len(_str), self.length)
        self.assertEqual(_str.strip(), repr(_obj))

    def test_get_fixed_length_str_w_dict(self):
        _obj = {"a": 10, "b": 20}
        _str = get_fixed_length_str(_obj, self.length, fill_char=" ")
        self.assertEqual(len(_str), self.length)
        self.assertEqual(_str.strip(), repr(_obj))

    def test_get_fixed_length_str_str_too_long(self):
        _obj = "this is a very long test string with no content"
        _str = get_fixed_length_str(_obj, self.length, fill_char=" ")
        self.assertEqual(len(_str), self.length)

    def test_get_fixed_length_str_final_char(self):
        _obj = "test this"
        _str = get_fixed_length_str(_obj, self.length, fill_char=".", final_space=True)
        self.assertEqual(len(_str), self.length)
        self.assertEqual(_str[-1], " ")

    def test_get_fixed_length_str_no_final_char(self):
        _obj = "test this"
        _fill = "."
        _str = get_fixed_length_str(
            _obj, self.length, fill_char=_fill, final_space=False
        )
        self.assertEqual(len(_str), self.length)
        self.assertEqual(_str[-1], _fill)

    def test_get_fixed_length_str_fill_front(self):
        _obj = "test this"
        _fill = "."
        _str = get_fixed_length_str(
            _obj, self.length, fill_char=_fill, final_space=False, fill_back=False
        )
        self.assertEqual(len(_str), self.length)
        self.assertTrue(_str.endswith(_obj))
        self.assertTrue(_str[0], _fill)

    def test_get_fixed_length_str_fill_back(self):
        _obj = "test this"
        _fill = "."
        _str = get_fixed_length_str(
            _obj, self.length, fill_char=_fill, final_space=False, fill_back=True
        )
        self.assertEqual(len(_str), self.length)
        self.assertTrue(_str.startswith(_obj))
        self.assertTrue(_str[-1], _fill)

    def test_time_str_plain(self):
        _str = get_time_string()
        t = time.localtime()
        _tstr = f"{t.tm_year}/{t.tm_mon:02d}/{t.tm_mday:02d}"
        self.assertTrue(_str.startswith(_tstr))

    def test_time_str_machine(self):
        _str = get_time_string(human_output=False)
        t = time.localtime()
        _tstr = f"{t.tm_year}{t.tm_mon:02d}{t.tm_mday:02d}"
        self.assertTrue(_str.startswith(_tstr))

    def test_time_str_epoch(self):
        _str = get_time_string(epoch=0)
        # check only for year, month, day and minute, second because of
        # conversion of time in different time zones.
        self.assertTrue(_str.startswith("1970/01/01"))
        self.assertTrue(_str.endswith(":00:00.000"))

    def test_get_short_time_string(self):
        _str = get_short_time_string(epoch=0)
        # check only for year, month, day and minute, second because of
        # conversion of time in different time zones.
        self.assertTrue(_str.startswith("01/01"))
        self.assertTrue(_str.endswith(":00:00"))

    def test_timed_print(self):
        _teststr = "afs 4-2 version 1.0"
        _fname = os.path.join(self._tmpdir, "out.txt")
        with open(_fname, "w") as _f:
            with redirect_stdout(_f):
                timed_print(_teststr)
        with open(_fname, "r") as _f:
            _text = _f.read()
        self.assertIn(_teststr, _text)

    def test_timed_print_verbose_false(self):
        _teststr = "afs 4-2 version 1.0"
        _fname = os.path.join(self._tmpdir, "out.txt")
        with open(_fname, "w") as _f:
            with redirect_stdout(_f):
                timed_print(_teststr, verbose=False)
        with open(_fname, "r") as _f:
            _text = _f.read()
        self.assertNotIn(_teststr, _text)

    def test_get_warning__simple(self):
        _teststr = "test"
        w = get_warning(_teststr)
        w_parts = w.split("\n")
        w_lens = [len(_w) for _w in w_parts]
        self.assertEqual(len(w_parts), 3)
        self.assertEqual(w_parts[0], "-" * 60)
        self.assertEqual(w_lens, [60, len(_teststr) + 2, 60])
        self.assertTrue(w_parts[1].startswith(f"- {_teststr}"))

    def test_print_warning(self):
        _teststr = "test"
        _fname = os.path.join(self._tmpdir, "out.txt")
        with open(_fname, "w") as _f:
            with redirect_stdout(_f):
                print_warning(_teststr)
        with open(_fname, "r") as _f:
            _text = _f.read().strip()
        w_parts = _text.split("\n")
        w_lens = [len(_w) for _w in w_parts]
        self.assertEqual(len(w_parts), 3)
        self.assertEqual(w_parts[0], "-" * 60)
        self.assertEqual(w_lens, [60, len(_teststr) + 2, 60])
        self.assertTrue(w_parts[1].startswith(f"- {_teststr}"))

    def test_get_warning__multiline(self):
        _teststr = ["test", "test2"]
        w = get_warning(_teststr, return_warning=True, print_warning=False)
        w_parts = w.split("\n")
        w_lens = [len(_w) for _w in w_parts]
        self.assertEqual(len(w_parts), 4)
        self.assertEqual(w_parts[0], "-" * 60)
        self.assertEqual(w_lens, [60] + [2 + len(_str) for _str in _teststr] + [60])
        self.assertTrue(w_parts[1].startswith(f"- {_teststr[0]}"))
        self.assertTrue(w_parts[2].startswith(f"- {_teststr[1]}"))

    def test_get_warning__multiline_with_empty_line(self):
        _teststr = ["test", "", "test2"]
        w = get_warning(_teststr)
        w_parts = w.split("\n")
        w_lens = [len(_w) for _w in w_parts]
        self.assertEqual(len(w_parts), 5)
        self.assertEqual(w_lens, [60] + [2 + len(_str) for _str in _teststr] + [60])
        self.assertEqual(w_parts[0], "-" * 60)
        self.assertTrue(w_parts[1].startswith(f"- {_teststr[0]}"))
        self.assertEqual(w_parts[2], "- ")
        self.assertTrue(w_parts[3].startswith(f"- {_teststr[2]}"))

    def test_get_warning__long_w_defaults(self):
        _teststr = "".join(random.choice(string.ascii_letters) for i in range(64))
        w = get_warning(_teststr)
        w_parts = w.split("\n")
        self.assertEqual(len(w_parts), 3)
        self.assertEqual(w_parts[0], "-" * 80)
        self.assertEqual(w_parts[2], "-" * 80)
        self.assertTrue(w_parts[1].startswith(f"- {_teststr}"))

    def test_get_warning__no_dashes(self):
        _teststr = "".join(random.choice(string.ascii_letters) for i in range(64))
        w = get_warning(_teststr, leading_dash=False, fill_dashes=False)
        w_parts = w.split("\n")
        self.assertEqual(len(w_parts), 3)
        self.assertEqual(w_parts[0], "-" * 80)
        self.assertEqual(w_parts[1], _teststr)
        self.assertEqual(w_parts[2], "-" * 80)

    def test_get_warning__long_fill_dashes(self):
        _teststr = "".join(random.choice(string.ascii_letters) for i in range(64))
        w = get_warning(_teststr, fill_dashes=True)
        w_parts = w.split("\n")
        w_lens = [len(_w) for _w in w_parts]
        self.assertEqual(len(w_parts), 3)
        self.assertEqual(w_parts[0], "-" * 80)
        self.assertEqual(w_parts[2], "-" * 80)
        self.assertEqual(w_lens, [80] * 3)
        self.assertTrue(w_parts[1].startswith(f"- {_teststr} -"))

    def test_get_warning_very_long(self):
        _teststr = "".join(random.choice(string.ascii_letters) for i in range(89))
        w = get_warning(_teststr, return_warning=True, print_warning=False)
        w_parts = w.split("\n")
        w_lens = [len(_w) for _w in w_parts]
        self.assertEqual(len(w_parts), 3)
        self.assertEqual(w_parts[0], "-" * 80)
        self.assertEqual(w_lens, [80] * len(w_parts))
        self.assertEqual(w_parts[1], f"- {_teststr[:73]}[...]")

    def test_get_warning_severe(self):
        _teststr = "test"
        w = get_warning(_teststr, severe=True)
        w_parts = w.split("\n")
        w_lens = [len(_w) for _w in w_parts]
        self.assertEqual(len(w_parts), 5)
        self.assertTrue(w_parts[0] == w_parts[4] == "=" * 60)
        self.assertTrue(w_parts[1] == w_parts[3] == "-" * 60)
        self.assertEqual(w_lens, [60, 60, len(_teststr) + 2, 60, 60])
        self.assertTrue(w_parts[2].startswith(f"- {_teststr}"))

    def test_get_warning_newlines(self):
        _teststr = "test"
        _newlines = 4
        w = get_warning(
            _teststr, return_warning=True, print_warning=False, new_lines=_newlines
        )
        w_parts = w.split("\n")
        for i in range(_newlines):
            self.assertEqual(len(w_parts[i]), 0)

    def test_convert_special_chars_to_unicode__list(self):
        _list = ["chi test", "test2", "another thetastr"]
        _target = ["\u03c7 test", "test2", "another thetastr"]
        _new_list = convert_special_chars_to_unicode(_list)
        self.assertEqual(_target, _new_list)

    def test_convert_special_chars_to_unicode__nested_list(self):
        _list = ["chi test", "test2", ["another thetastr", "item"]]
        _target = ["\u03c7 test", "test2", ["another thetastr", "item"]]
        _new_list = convert_special_chars_to_unicode(_list)
        self.assertEqual(_target, _new_list)

    def test_convert_special_chars_to_unicode__str(self):
        _str = "chi test test2 Another thetastr^-1"
        _target = "\u03c7 test test2 Another thetastr\u207b\u00b9"
        _new_str = convert_special_chars_to_unicode(_str)
        self.assertEqual(_target, _new_str)

    def test_convert_special_chars_to_unicode__int(self):
        with self.assertRaises(TypeError):
            convert_special_chars_to_unicode(12)

    def test_convert_unicode_to_ascii__list(self):
        _list = ["\u03c7 test", "test2", "another thetastr"]
        _target = ["chi test", "test2", "another thetastr"]
        _new_list = convert_unicode_to_ascii(_list)
        self.assertEqual(_target, _new_list)

    def test_convert_unicode_to_ascii__str(self):
        _str = "\u03c7 test test2 Another thetastr\u207b\u00b9"
        _target = "chi test test2 Another thetastr^-1"
        _new_str = convert_unicode_to_ascii(_str)
        self.assertEqual(_new_str, _target)

    def test_convert_unicode_to_ascii__wrong_type(self):
        with self.assertRaises(TypeError):
            convert_unicode_to_ascii((1, 2, 3))

    def test_get_range_as_formatted_string__w_string(self):
        _input = "12321"
        _output = get_range_as_formatted_string(_input)
        self.assertEqual(_input, _output)

    def test_get_range_as_formatted_string__w_list(self):
        _input = [0, 1, 2, 3]
        _output = get_range_as_formatted_string(_input)
        self.assertEqual(_output, "0 ... 3")

    def test_get_range_as_formatted_string__w_tuple(self):
        _input = (0, 1, 2, 3)
        _output = get_range_as_formatted_string(_input)
        self.assertEqual(_output, "0 ... 3")

    def test_get_range_as_formatted_string__w_iterator(self):
        _input = range(0, 4)
        _output = get_range_as_formatted_string(_input)
        self.assertEqual(_output, "0 ... 3")

    def test_get_range_as_formatted_string__w_float(self):
        _input = (0.1, 1.2, 2.3, 3.4)
        _output = get_range_as_formatted_string(_input)
        self.assertEqual(_output, "0.100000 ... 3.400000")

    def test_get_range_as_formatted_string__w_strings(self):
        _input = ("a", "b", "c")
        _output = get_range_as_formatted_string(_input)
        self.assertEqual(_output, "a ... c")

    def test_get_range_as_formatted_string__w_mixed(self):
        _input = ("a", "b", 4)
        _output = get_range_as_formatted_string(_input)
        self.assertEqual(_output, "a ... 4")

    def test_get_range_as_formatted_string__range_of_len_one(self):
        _input = ("a",)
        _output = get_range_as_formatted_string(_input)
        self.assertEqual(_output, "a ... a")

    def test_get_range_as_formatted_string__with_value(self):
        _input = 12
        _output = get_range_as_formatted_string(_input)
        self.assertEqual(_output, "unknown range")

    def test_update_separators(self):
        _test = "this\\string/has\\mixed/separators"
        _new = update_separators(_test)
        if sys.platform in ["win32", "win64"]:
            self.assertEqual(_new.find("/"), -1)
        else:
            self.assertEqual(_new.find("\\"), -1)

    def test_format_input_to_multiline_str__empty(self):
        _test = ""
        _new = format_input_to_multiline_str(_test)
        self.assertEqual(_new, "")

    def test_format_input_to_multiline_str__simple(self):
        _test = "test test test test "
        _new = format_input_to_multiline_str(_test)
        self.assertEqual(_new, "test test test test")

    def test_format_input_to_multiline_str__too_long(self):
        _test = "test test test test "
        _new = format_input_to_multiline_str(_test, max_line_length=12)
        self.assertEqual(_new, "test test\ntest test")

    def test_format_input_to_multiline_str__dont_keep_linebreaks(self):
        _test = "test test\n\ntest\ntest "
        _new = format_input_to_multiline_str(_test, keep_linebreaks=False)
        self.assertEqual(_new, "test test test test")

    def test_format_input_to_multiline_str__simple_with_padding(self):
        _test = "test test test test "
        _new = format_input_to_multiline_str(
            _test, max_line_length=12, pad_to_max_length=True
        )
        self.assertEqual(_new, " test test  \n test test  ")

    def test_format_input_to_multiline_str__too_long_word(self):
        _test = "test testtesttesttest test test "
        _new = format_input_to_multiline_str(_test, max_line_length=12)
        self.assertEqual(_new, "test\ntesttesttesttest\ntest test")

    def test_format_input_to_multiline_str__too_long_word_with_padding(self):
        _test = "test testtesttesttest test test "
        _new = format_input_to_multiline_str(
            _test, max_line_length=12, pad_to_max_length=True
        )
        self.assertEqual(_new, "    test    \ntesttesttesttest\n test test  ")

    def test_format_input_to_multiline_str__one_word_only(self):
        _test = "test"
        _new = format_input_to_multiline_str(_test)
        self.assertEqual(_new, "test")

    def test_format_input_to_multiline_str__one_word_only_with_padding(self):
        _test = "test"
        _new = format_input_to_multiline_str(
            _test, max_line_length=12, pad_to_max_length=True
        )
        self.assertEqual(_new, "    test    ")

    def test_format_input_to_multiline_str__max_len_changes(self):
        _test = "test test2 test3 test4 "
        _new = format_input_to_multiline_str(_test, max_line_length=6)
        self.assertEqual(_new, "test\ntest2\ntest3\ntest4")

    def test_format_input_to_multiline_str__w_indent(self):
        _test = "test1 test2 test3 test4 "
        for _indent in [0, 1, 2, 3]:
            with self.subTest(indent=_indent):
                _new = format_input_to_multiline_str(
                    _test, max_line_length=5 + _indent, indent=_indent
                )
                _expected = " " * _indent
                _expected += ("\n" + " " * _indent).join(
                    _item for _item in ["test1", "test2", "test3", "test4"]
                )
                self.assertEqual(_new, _expected)

    def test_format_input_to_multiline_str__too_long_with_space(self):
        _test = "test testtest"
        _new = format_input_to_multiline_str(_test, max_line_length=12)
        self.assertEqual(_new, "test\ntesttest")

    def test_format_input_to_multiline_str__too_long_with_space_padding(self):
        _test = "test testtest"
        _new = format_input_to_multiline_str(
            _test, max_line_length=12, pad_to_max_length=True
        )
        self.assertEqual(_new, "    test    \n  testtest  ")

    def test_get_random_string(self):
        _len = 37
        _test = get_random_string(_len)
        self.assertEqual(len(_test), _len)
        for _char in _test:
            self.assertIn(_char, string.ascii_letters)

    def test_get_formatted_dict_representation__indent(self):
        _test_dict = {"a": 1, "b": 2.3, "c": "a", "d": 0.0000004, "e": 556744335.2}
        for _indent in [0, 1, 3, 6]:
            with self.subTest(indent=_indent):
                _formatted = get_formatted_dict_representation(
                    _test_dict, indent=_indent
                )
                for _line in _formatted.split("\n"):
                    self.assertTrue(_line.startswith(" " * _indent))

    def test_get_formatted_dict_representation__digits(self):
        _test_dict = {"a": 2.3}
        for _digits in [2, 4, 6, 9]:
            with self.subTest(digits=_digits):
                _formatted = get_formatted_dict_representation(
                    _test_dict, digits=_digits
                )
                self.assertEqual(_formatted, f"a: {2.3:.{_digits}f}")

    def test_get_formatted_dict_representation__small_float(self):
        _value = 0.0000003
        _test_dict = {"a": _value}
        for _digits in [2, 4, 6, 9]:
            with self.subTest(digits=_digits):
                _formatted = get_formatted_dict_representation(
                    _test_dict, digits=_digits
                )
                self.assertEqual(_formatted, f"a: {_value:.{_digits}e}")

    def test_get_formatted_dict_representation__large_float(self):
        _value = 534636333.2
        _test_dict = {"a": _value}
        for _digits in [2, 4, 6, 9]:
            with self.subTest(digits=_digits):
                _formatted = get_formatted_dict_representation(
                    _test_dict, digits=_digits
                )
                self.assertEqual(_formatted, f"a: {_value:.{_digits}e}")

    def test_get_formatted_dict_representation__large_int(self):
        _value = 534636333
        _test_dict = {"a": _value}
        _formatted = get_formatted_dict_representation(_test_dict)
        self.assertEqual(_formatted, f"a: {_value}")


if __name__ == "__main__":
    unittest.main()

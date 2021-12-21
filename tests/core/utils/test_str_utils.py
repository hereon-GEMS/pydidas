# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
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
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import sys
import unittest
import time
import string
import random

from pydidas.core.utils.str_utils import (
    get_fixed_length_str, get_time_string, get_warning,
    convert_special_chars_to_unicode, format_input_to_multiline_str,
    convert_unicode_to_ascii, update_separators, get_random_string)


class Test_str_utils(unittest.TestCase):

    def setUp(self):
        self.length = 20

    def tearDown(self):
        ...

    def test_get_fixed_length_str_length(self):
        self.assertEqual(len(get_fixed_length_str('test', self.length)), self.length)

    def test_get_fixed_length_str_fill_char_too_long(self):
        with self.assertRaises(TypeError):
            get_fixed_length_str('test', self.length, fill_char='..')

    def test_get_fixed_length_str_w_number(self):
        _num = 20
        _formatter = '{:.3f}'
        _str = get_fixed_length_str(_num, self.length, fill_char=' ',
                          formatter=_formatter)
        self.assertEqual(len(_str), self.length)
        self.assertEqual(_str.strip(), _formatter.format(_num))

    def test_get_fixed_length_str_w_list(self):
        _obj = [10, 20]
        _str = get_fixed_length_str(_obj, self.length, fill_char=' ')
        self.assertEqual(len(_str), self.length)
        self.assertEqual(_str.strip(), repr(_obj))

    def test_get_fixed_length_str_w_tuple(self):
        _obj = (10, 20)
        _str = get_fixed_length_str(_obj, self.length, fill_char=' ')
        self.assertEqual(len(_str), self.length)
        self.assertEqual(_str.strip(), repr(_obj))

    def test_get_fixed_length_str_w_set(self):
        _obj = {10, 20}
        _str = get_fixed_length_str(_obj, self.length, fill_char=' ')
        self.assertEqual(len(_str), self.length)
        self.assertEqual(_str.strip(), repr(_obj))

    def test_get_fixed_length_str_w_dict(self):
        _obj = {'a': 10, 'b':20}
        _str = get_fixed_length_str(_obj, self.length, fill_char=' ')
        self.assertEqual(len(_str), self.length)
        self.assertEqual(_str.strip(), repr(_obj))

    def test_get_fixed_length_str_str_too_long(self):
        _obj = 'this is a very long test string with no content'
        _str = get_fixed_length_str(_obj, self.length, fill_char=' ')
        self.assertEqual(len(_str), self.length)

    def test_get_fixed_length_str_final_char(self):
        _obj = 'test this'
        _str = get_fixed_length_str(_obj, self.length, fill_char='.', final_space=True)
        self.assertEqual(len(_str), self.length)
        self.assertEqual(_str[-1], ' ')

    def test_get_fixed_length_str_no_final_char(self):
        _obj = 'test this'
        _fill = '.'
        _str = get_fixed_length_str(_obj, self.length, fill_char=_fill,
                          final_space=False)
        self.assertEqual(len(_str), self.length)
        self.assertEqual(_str[-1], _fill)

    def test_get_fixed_length_str_fill_front(self):
        _obj = 'test this'
        _fill = '.'
        _str = get_fixed_length_str(_obj, self.length, fill_char=_fill,
                          final_space=False, fill_back=False)
        self.assertEqual(len(_str), self.length)
        self.assertTrue(_str.endswith(_obj))
        self.assertTrue(_str[0], _fill)

    def test_get_fixed_length_str_fill_back(self):
        _obj = 'test this'
        _fill = '.'
        _str = get_fixed_length_str(_obj, self.length, fill_char=_fill,
                          final_space=False, fill_back=True)
        self.assertEqual(len(_str), self.length)
        self.assertTrue(_str.startswith(_obj))
        self.assertTrue(_str[-1], _fill)

    def test_time_str_plain(self):
        _str = get_time_string()
        t = time.localtime()
        _tstr = f'{t.tm_year}/{t.tm_mon:02d}/{t.tm_mday:02d}'
        self.assertTrue(_str.startswith(_tstr))

    def test_time_str_machine(self):
        _str = get_time_string(human_output=False)
        t = time.localtime()
        _tstr = f'{t.tm_year}{t.tm_mon:02d}{t.tm_mday:02d}'
        self.assertTrue(_str.startswith(_tstr))

    def test_time_str_epoch(self):
        _str = get_time_string(epoch=0)
        self.assertTrue(_str.startswith('1970/01/01'))
        self.assertTrue(_str.endswith(':00:00.000'))

    def test_get_warning_simple(self):
        _teststr = 'test'
        w = get_warning(_teststr, return_warning=True, print_warning=False)
        w_parts = w.split('\n')
        w_lens = [len(_w) for _w in w_parts]
        self.assertEqual(len(w_parts), 3)
        self.assertEqual(w_parts[0], '-' * 60)
        self.assertEqual(w_lens, [60] * len(w_parts))
        self.assertTrue(w_parts[1].startswith(f'- {_teststr} -'))

    def test_get_warning_multiline(self):
        _teststr = ['test', 'test2']
        w = get_warning(_teststr, return_warning=True, print_warning=False)
        w_parts = w.split('\n')
        w_lens = [len(_w) for _w in w_parts]
        self.assertEqual(len(w_parts), 4)
        self.assertEqual(w_parts[0], '-' * 60)
        self.assertEqual(w_lens, [60] * len(w_parts))
        self.assertTrue(w_parts[1].startswith(f'- {_teststr[0]} -'))
        self.assertTrue(w_parts[2].startswith(f'- {_teststr[1]} -'))

    def test_get_warning_long(self):
        _teststr = ''.join(random.choice(string.ascii_letters)
                           for i in range(64))
        w = get_warning(_teststr, return_warning=True, print_warning=False)
        w_parts = w.split('\n')
        w_lens = [len(_w) for _w in w_parts]
        self.assertEqual(len(w_parts), 3)
        self.assertEqual(w_parts[0], '-' * 80)
        self.assertEqual(w_lens, [80] * len(w_parts))
        self.assertTrue(w_parts[1].startswith(f'- {_teststr} -'))

    def test_get_warning_very_long(self):
        _teststr = ''.join(random.choice(string.ascii_letters)
                           for i in range(89))
        w = get_warning(_teststr, return_warning=True, print_warning=False)
        w_parts = w.split('\n')
        w_lens = [len(_w) for _w in w_parts]
        self.assertEqual(len(w_parts), 3)
        self.assertEqual(w_parts[0], '-' * 80)
        self.assertEqual(w_lens, [80] * len(w_parts))
        self.assertEqual(w_parts[1], f'- {_teststr[:73]}[...]')

    def test_get_warning_severe(self):
        _teststr = 'test'
        w = get_warning(_teststr, return_warning=True, print_warning=False,
                        severe=True)
        w_parts = w.split('\n')
        w_lens = [len(_w) for _w in w_parts]
        self.assertEqual(len(w_parts), 5)
        self.assertTrue(w_parts[0] == w_parts[4] == '=' * 60)
        self.assertTrue(w_parts[1] == w_parts[3] == '-' * 60)
        self.assertEqual(w_lens, [60] * len(w_parts))
        self.assertTrue(w_parts[2].startswith(f'- {_teststr} -'))

    def test_get_warning_newlines(self):
        _teststr = 'test'
        _newlines = 4
        w = get_warning(_teststr, return_warning=True, print_warning=False,
                        new_lines=_newlines)
        w_parts = w.split('\n')
        for i in range(_newlines):
            self.assertEqual(len(w_parts[i]), 0)

    def test_convert_special_chars_to_unicode__list(self):
        _list = ['chi test', 'test2', 'another thetastr']
        _target = ['\u03C7 test', 'test2', 'another thetastr']
        _new_list = convert_special_chars_to_unicode(_list)
        self.assertEqual(_target, _new_list)

    def test_convert_special_chars_to_unicode__nested_list(self):
        _list = ['chi test', 'test2', ['another thetastr', 'item']]
        _target = ['\u03C7 test', 'test2', ['another thetastr', 'item']]
        _new_list = convert_special_chars_to_unicode(_list)
        self.assertEqual(_target, _new_list)

    def test_convert_special_chars_to_unicode__str(self):
        _str = 'chi test test2 Another thetastr^-1'
        _target = '\u03C7 test test2 Another thetastr\u207b\u00B9'
        _new_str = convert_special_chars_to_unicode(_str)
        self.assertEqual(_target, _new_str)

    def test_convert_special_chars_to_unicode__int(self):
        with self.assertRaises(TypeError):
            convert_special_chars_to_unicode(12)

    def test_convert_unicode_to_ascii__list(self):
        _list = ['\u03C7 test', 'test2', 'another thetastr']
        _target = ['chi test', 'test2', 'another thetastr']
        _new_list = convert_unicode_to_ascii(_list)
        self.assertEqual(_target, _new_list)

    def test_convert_unicode_to_ascii__str(self):
        _str = '\u03C7 test test2 Another thetastr\u207b\u00B9'
        _target = 'chi test test2 Another thetastr^-1'
        _new_str = convert_unicode_to_ascii(_str)
        self.assertEqual(_new_str, _target)

    def test_update_separators(self):
        _test = 'this\\string/has\\mixed/separators'
        _new = update_separators(_test)
        if sys.platform in ['win32', 'win64']:
            self.assertEqual(_new.find('/'), -1)
        else:
            self.assertEqual(_new.find('\\'), -1)

    def test_format_input_to_multiline_str__simple(self):
        _test = 'test test test test '
        _new = format_input_to_multiline_str(_test)
        self.assertEqual(_new, 'test test\ntest test')

    def test_format_input_to_multiline_str__simple_with_padding(self):
        _test = 'test test test test '
        _new = format_input_to_multiline_str(_test, pad_to_max_length=True)
        self.assertEqual(_new, ' test test  \n test test  ')

    def test_format_input_to_multiline_str__too_long_word(self):
        _test = 'test testtesttesttest test test '
        _new = format_input_to_multiline_str(_test)
        self.assertEqual(_new, 'test\ntesttesttesttest\ntest test')

    def test_format_input_to_multiline_str__too_long_word_with_padding(self):
        _test = 'test testtesttesttest test test '
        _new = format_input_to_multiline_str(_test, pad_to_max_length=True)
        self.assertEqual(_new, '    test    \ntesttesttesttest\n test test  ')

    def test_format_input_to_multiline_str__one_word_only(self):
        _test = 'test'
        _new = format_input_to_multiline_str(_test)
        self.assertEqual(_new, 'test')

    def test_format_input_to_multiline_str__one_word_only_with_padding(self):
        _test = 'test'
        _new = format_input_to_multiline_str(_test, pad_to_max_length=True)
        self.assertEqual(_new, '    test    ')

    def test_format_input_to_multiline_str__max_len_changes(self):
        _test = 'test test2 test3 test4 '
        _new = format_input_to_multiline_str(_test, max_line_length=6)
        self.assertEqual(_new, 'test\ntest2\ntest3\ntest4')

    def test_format_input_to_multiline_str__too_long_with_space(self):
        _test = 'test testtest'
        _new = format_input_to_multiline_str(_test)
        self.assertEqual(_new, 'test\ntesttest')

    def test_format_input_to_multiline_str__too_long_with_space_padding(self):
        _test = 'test testtest'
        _new = format_input_to_multiline_str(_test, pad_to_max_length=True)
        self.assertEqual(_new, '    test    \n  testtest  ')

    def test_get_random_string(self):
        _len = 37
        _test = get_random_string(_len)
        self.assertEqual(len(_test), _len)
        for _char in _test:
            self.assertIn(_char, string.ascii_letters)


if __name__ == "__main__":
    unittest.main()

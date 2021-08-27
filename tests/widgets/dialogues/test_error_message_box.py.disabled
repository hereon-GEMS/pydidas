# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""Unit tests for pydidas modules."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import unittest
import string
import random

from PyQt5 import  QtWidgets

from pydidas._exceptions import WidgetLayoutError
from pydidas.widgets.dialogues.error_message_box import ErrorMessageBox


class TestErrorMessageBox(unittest.TestCase):

    def setUp(self):
        self.q_app = QtWidgets.QApplication([])
        self.widgets = []

    def tearDown(self):
        self.q_app.deleteLater()
        self.q_app.quit()

    def test_init__plain(self):
        box = ErrorMessageBox()
        self.assertIsInstance(box, ErrorMessageBox)

    def test_init__with_parent(self):
        _parent = QtWidgets.QWidget()
        box = ErrorMessageBox(_parent)
        self.assertEqual(box.parent(), _parent)

    def test_init__with_text(self):
        _text = 'error text'
        box = ErrorMessageBox(text=_text)
        self.assertEqual(box._label.text(), _text)

    def test_set_text__no_text(self):
        box = ErrorMessageBox()
        with self.assertRaises(TypeError):
            box.set_text()

    def test_set_text__text(self):
        _text = 'new text'
        box = ErrorMessageBox(text='old text')
        box.set_text(_text)
        self.assertEqual(box._label.text(), _text)

    def test_exec(self):
        box = ErrorMessageBox()
        box.exec_()


if __name__ == "__main__":
    unittest.main()

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

import numpy as np

from pydidas.image_io.image_reader_factory import (ImageReaderFactory,
                                                   _ImageReaderFactory)


class DummyReader:
    def __init__(self):
        ...

    def read_image(self, filename, **kwargs):
        return np.random.random((10, 10))


class TestImageReaderFactory(unittest.TestCase):

    def setUp(self):
        ...

    def tearDown(self):
        ...

    def test_get_instance(self):
        obj = ImageReaderFactory()
        self.assertIsInstance(obj, _ImageReaderFactory)

    def test_attributes(self):
        obj = ImageReaderFactory()
        self.assertTrue(hasattr(obj, '_readers'))
        self.assertTrue(hasattr(obj, '_extensions'))

    def test_register_format(self):
        obj = ImageReaderFactory()
        obj.register_format('test', ['.test'], DummyReader)
        self.assertTrue('.test' in obj._extensions)
        self.assertTrue('test' in obj._readers)
        self.assertIsInstance(obj._readers['test'](), DummyReader)

    def test_get_reader(self):
        obj = ImageReaderFactory()
        obj.register_format('test', ['.test'], DummyReader)
        reader = obj.get_reader('test/test2/testname.test')
        self.assertIsInstance(reader, DummyReader)

    def test_get_reader_wrong_ext(self):
        obj = ImageReaderFactory()
        with self.assertRaises(KeyError):
            obj.get_reader('test/test2/testname.test')

    def test_get_reader_no_reader(self):
        obj = ImageReaderFactory()
        obj._extensions['.test'] = None
        with self.assertRaises(KeyError):
            obj.get_reader('test/test2/testname.test')


if __name__ == "__main__":
    unittest.main()

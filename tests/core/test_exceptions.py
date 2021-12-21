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

import unittest

from pydidas.core import (AppConfigError, FrameConfigError, WidgetLayoutError,
                          DatasetConfigException)


class TestPydidasExceptions(unittest.TestCase):

    def setUp(self):
        ...

    def tearDown(self):
        ...

    def test_app_config_error(self):
        self.assertTrue(issubclass(AppConfigError, Exception))

    def test_widget_layout_error(self):
        self.assertTrue(issubclass(WidgetLayoutError, Exception))

    def test_frame_config_error(self):
        self.assertTrue(issubclass(FrameConfigError, Exception))

    def test_dataset_config_exception(self):
        self.assertTrue(issubclass(DatasetConfigException, Exception))


if __name__ == "__main__":
    unittest.main()

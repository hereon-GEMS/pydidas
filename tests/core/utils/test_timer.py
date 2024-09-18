# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import os
import shutil
import tempfile
import time
import unittest
from contextlib import redirect_stdout

from pydidas.core.utils import Timer, TimerSaveRuntime


class TestTimer(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self._tmpdir)

    def test_timer(self):
        _fname = os.path.join(self._tmpdir, "out.txt")
        with open(_fname, "w") as _f:
            with redirect_stdout(_f):
                with Timer():
                    time.sleep(0.01)
        with open(_fname, "r") as _f:
            _text = _f.read()
        self.assertIn("Code runtime is ", _text)

    def test_timer_save_runtime(self):
        _delays = [0.01, 0.02, 0.03, 0.08]
        for _delay in _delays:
            with self.subTest(code_runtime=_delay):
                with TimerSaveRuntime() as runtime:
                    time.sleep(_delay)
                _runtime = runtime()
                self.assertTrue(_runtime >= _delay)


if __name__ == "__main__":
    unittest.main()

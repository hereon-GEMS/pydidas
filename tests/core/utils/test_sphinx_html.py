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

import copy
import os
import shutil
import sys
import tempfile
import unittest

from pydidas.core.utils import sphinx_html


class Test_sphinx_html(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self._tmpdir, "docs", "build"))
        self._argv = copy.copy(sys.argv)

    def tearDown(self):
        shutil.rmtree(self._tmpdir)
        sys.argv = self._argv

    def test_check_sphinx_html_docs__generic_case(self):
        with open(os.path.join(self._tmpdir, "docs-built.yml"), "w") as f:
            f.write("docs-built: true")
        self.assertTrue(sphinx_html.check_sphinx_html_docs(self._tmpdir))

    def test_check_sphinx_html_docs__empty_folder(self):
        self.assertFalse(sphinx_html.check_sphinx_html_docs(self._tmpdir))

    def test_check_sphinx_html_docs__sphinx_running(self):
        sys.argv.append("sphinx-build")
        self.assertFalse(sphinx_html.check_sphinx_html_docs(self._tmpdir))

    #############
    # The following test runs for 30 seconds + and should not
    # be run routinely in the test suite.
    #############
    # def test_run_sphinx_html_build(self):
    #     import io
    #     import warnings
    #     from contextlib import redirect_stdout
    #     from pydidas.core.utils import DOC_SOURCE_DIRECTORY

    #     shutil.copytree(
    #         os.path.join(DOC_SOURCE_DIRECTORY, "src"),
    #         os.path.join(self._tmpdir, "docs", "src"),
    #     )
    #     with warnings.catch_warnings(), io.StringIO() as buf, redirect_stdout(buf):
    #         warnings.simplefilter("ignore")
    #         sphinx_html.run_sphinx_html_build(
    #             build_dir=os.path.join(self._tmpdir, "html")
    #         )
    #         _output = buf.getvalue()
    #     self.assertTrue(
    #         os.path.exists(os.path.join(self._tmpdir, "html", "index.html"))
    #     )
    #     self.assertTrue(len(_output) > 0)


if __name__ == "__main__":
    unittest.main()

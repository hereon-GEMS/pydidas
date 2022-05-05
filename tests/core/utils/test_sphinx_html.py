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
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import sys
import unittest
import tempfile
import os
import shutil
import copy

from pydidas.core.utils import sphinx_html


class Test_sphinx_html(unittest.TestCase):

    def setUp(self):
        self._tmpdir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self._tmpdir, 'docs', 'build'))
        self._argv = copy.copy(sys.argv)

    def tearDown(self):
        shutil.rmtree(self._tmpdir)
        sys.argv = self._argv

    def test_check_sphinx_html_docs__generic_case(self):
        self.assertTrue(sphinx_html.check_sphinx_html_docs())

    def test_check_sphinx_html_docs__empty_folder(self):
        self.assertFalse(sphinx_html.check_sphinx_html_docs(self._tmpdir))

    def test_check_sphinx_html_docs__sphinx_running(self):
        sys.argv.append('sphinx-build')
        self.assertFalse(sphinx_html.check_sphinx_html_docs(self._tmpdir))

    ##############
    # The following test runs for 15 seconds + and should not
    # be run routinely in the test suite.
    ##############
    # def test_run_sphinx_html_build(self):
    #     for _fname in ['make.bat', 'Makefile']:
    #         shutil.copyfile(os.path.join(get_doc_make_directory(), _fname),
    #                         os.path.join(self._tmpdir, 'docs', _fname))
    #     shutil.copytree(os.path.join(get_doc_make_directory(), 'source'),
    #                     os.path.join(self._tmpdir, 'docs', 'source'))
    #     with io.StringIO() as buf, redirect_stdout(buf):
    #         sphinx_html.run_sphinx_html_build(
    #             os.path.join(self._tmpdir, 'docs'))
    #         _output = buf.getvalue()
    #     self.assertTrue(os.path.exists(os.path.join(
    #         self._tmpdir, 'docs', 'build', 'html', 'index.html')))
    #     self.assertTrue(len(_output) > 0)


if __name__ == "__main__":
    unittest.main()

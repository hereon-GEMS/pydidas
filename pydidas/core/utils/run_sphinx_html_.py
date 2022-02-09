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

"""
The run_sphinx_html module includes functions to check whether the Sphinx
documentation exists or whether it needs to be created and a function to
generate the Sphinx html documentation.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['run_sphinx_html_build']

import os
import sys
import subprocess


_path = __file__
for _ in range(4):
    _path = os.path.dirname(__file__)
DOC_PATH = os.path.join(_path, 'docs')
"""
str :
    The home path of the documentation, i.e. the path where the make files
    can be found.
"""


def check_sphinx_html_docs():
    """
    This functions checks whether the index.html file for the built sphinx
    documentation exists or is in the process of being created and calls the
    builder if neither check is true.
    """
    _sphinx_running = 'sphinx-build' in sys.argv[0]
    _index_file = os.path.join(DOC_PATH, 'build', 'html', 'index.html')
    if not os.path.exists(_index_file) and not _sphinx_running:
        run_sphinx_html_build()


def run_sphinx_html_build():
    """
    Run the sphinx process to generate the html documentation.
    """
    print('=' * 60)
    print('-' * 60)
    print('----- The html documentation has not yet been created! -----')
    print('----- Running sphinx-build. This may take a bit.       -----')
    print('----- pydidas will automatically load once building of -----')
    print('----- the documentation has been finished.             -----')
    print('-' * 60)
    print('=' * 60)
    if sys.platform in ['win32', 'win64']:
        subprocess.call([os.path.join(DOC_PATH, 'make.bat'), 'html'])
    else:
        subprocess.call(['make', '-C',  DOC_PATH, 'html'])

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
The pydidas (PYthon DIffraction Data Analysis Suite) package is designed to
speed up and facilitate diffraction data analysis at Synchrotron beamlines.

It is being developed by Helmholtz-Zentrum Hereon.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

# import QtWebEngineWidgets first before creating any QApplication because
# of problem with binding (cannot import engine after application has been
# created)
from PyQt5 import QtCore, QtWebEngineWidgets

# import sub-packages:
from . import apps
from . import core
from . import experiment
from . import gui
from . import image_io
from . import managers
from . import multiprocessing
from . import plugins
from . import unittest_objects
from . import widgets
from . import workflow
__all__.extend(['apps', 'core', 'experiment', 'gui', 'image_io', 'managers',
                'multiprocessing', 'plugins', 'unittest_objects', 'utils',
                'widgets', 'workflow'])


import subprocess
import sys
import os
_doc_path = os.path.join(os.path.dirname(os.path.dirname((__file__))), 'docs')
_sphinx_running = 'sphinx-build' in sys.argv[0]
if (not os.path.exists(os.path.join(_doc_path, 'build', 'html', 'index.html'))
    and not _sphinx_running):
    print('=' * 60)
    print('-' * 60)
    print('----- The html documentation has not yet been created! -----')
    print('----- Running sphinx-build. This may take a bit.       -----')
    print('----- pydidas will automatically load once building of -----')
    print('----- the documentation has been finished.             -----')
    print('-' * 60)
    print('=' * 60)
    if sys.platform in ['win32', 'win64']:
        subprocess.call([os.path.join(_doc_path, 'make.bat'), 'html'])
    else:
        subprocess.call(['make', '-C',  _doc_path, 'html'])

del subprocess
del sys
del os

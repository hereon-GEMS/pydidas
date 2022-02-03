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
# of problem with python Qt binding (cannot import engine after application
# has been created)
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


# Check whether the sphinx documentation has been built and build it if
# has not:
if not core.utils.check_sphinx_html_docs():
    core.utils.run_sphinx_html_build()


# Disable the pyFAI logging to console
import os
os.environ['PYFAI_NO_LOGGING'] = '1'
# Change the pyFAI logging level to ERROR and above
import logging
pyFAI_azi_logger = logging.getLogger('pyFAI.azimuthalIntegrator')
pyFAI_azi_logger.setLevel(logging.ERROR)
silx_opencl_logger = logging.getLogger('silx.opencl.processing')
silx_opencl_logger.setLevel(logging.ERROR)

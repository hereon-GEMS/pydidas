# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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

"""
The pydidas (PYthon DIffraction Data Analysis Suite) package is designed to
speed up and facilitate diffraction data analysis at Synchrotron beamlines.

It is being developed by Helmholtz-Zentrum Hereon.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


# must import h5py and the hdf5plugin here to have the dll libraries linked correctly
# in Windows before using them in the package in different orders
import h5py as __h5py  # noqa: F401
import hdf5plugin as __hdf5plugin  # noqa: F401

# import pydidas_qtcore to set up the QApplication and assure
# that the QT_API is set correctly
import pydidas_qtcore as __pydidas_qtcore  # noqa: F401

# import local modules
# import sub-packages:
from . import (
    apps,
    contexts,
    core,
    data_io,
    gui,
    managers,
    multiprocessing,
    plugins,
    resources,
    unittest_objects,
    widgets,
    workflow,
)
from .core.utils.qt_utilities import IS_QT6
from .initialize import check_documentation, configure_pyFAI, initialize_qsetting_values
from .logging_level import LOGGING_LEVEL
from .version import VERSION, version


__version__ = VERSION
__all__ = [
    "core",
    "contexts",
    "data_io",
    "multiprocessing",
    "managers",
    "plugins",
    "workflow",
    "apps",
    "unittest_objects",
    "widgets",
    "gui",
    "IS_QT6",
    "version",
    "VERSION",
    "LOGGING_LEVEL",
]


check_documentation()

configure_pyFAI()

initialize_qsetting_values()

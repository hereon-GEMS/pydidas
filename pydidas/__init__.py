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

"""
The pydidas (PYthon DIffraction Data Analysis Suite) package is designed to
speed up and facilitate diffraction data analysis at Synchrotron beamlines.

It is being developed by Helmholtz-Zentrum Hereon.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []

import os as __os
import sys as __sys
import logging as __logging

import qtpy.QtCore as __QtCore
import qtpy.QtWidgets as __QtWidgets
import qtpy as __qtpy

# must import h5py here to have the dll libraries linked correctly
import h5py as __h5py
import hdf5plugin as __hdf5plugin


if __QtWidgets.QApplication.instance() is None:
    import pydidas_qtcore

    __app = pydidas_qtcore.PydidasQApplication(__sys.argv)


# import local modules
from .version import version, VERSION
from .logging_level import LOGGING_LEVEL

# import sub-packages:
from . import core
from . import resources
from . import contexts
from . import data_io
from . import multiprocessing
from . import managers
from . import plugins
from . import workflow
from . import apps
from . import unittest_objects
from . import widgets
from . import gui


IS_QT6 = __qtpy.QT_VERSION[0] == "6"

__all__.extend(
    [
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
)


# Check whether the sphinx documentation has been built and build it if it
# has not:
if not core.utils.check_sphinx_html_docs():
    core.utils.run_sphinx_html_build()

# Check whether a plugin directory has been set or set the default one:
core.utils.set_default_plugin_dir()

# Disable the pyFAI logging to console
__os.environ["PYFAI_NO_LOGGING"] = "1"
# Change the pyFAI logging level to ERROR and above
pyFAI_azi_logger = __logging.getLogger("pyFAI.azimuthalIntegrator")
pyFAI_azi_logger.setLevel(__logging.ERROR)
pyFAI_logger = __logging.getLogger("pyFAI")
pyFAI_logger.setLevel(__logging.ERROR)
silx_opencl_logger = __logging.getLogger("silx.opencl.processing")
silx_opencl_logger.setLevel(__logging.ERROR)


# if not existing, initialize all QSettings with the default values from the
# default Parameters to avoid having "None" keys returned.
__settings = __QtCore.QSettings("Hereon", "pydidas")
for _prefix, _keys in (
    ("global", core.constants.QSETTINGS_GLOBAL_KEYS),
    ("user", core.constants.QSETTINGS_USER_KEYS),
    ("user", core.constants.QSETTINGS_USER_SPECIAL_KEYS),
):
    for _key in _keys:
        _val = __settings.value(f"{VERSION}/{_prefix}/{_key}")
        if _val is None:
            _param = core.get_generic_parameter(_key)
            __settings.setValue(f"{VERSION}/{_prefix}/{_key}", _param.default)
del __settings
